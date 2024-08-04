import logging
from abc import ABC, abstractmethod

from neomodel import db

from sdl.models import Pump, Ultrasonic, Relay, Reservoir

LOGGER = logging.getLogger(__name__)

class RelayClass(ABC):
    def __init__(self, relay_num: int, name: str, properties: dict):
        self.relay_num = relay_num
        self.name = name
        self.properties = properties
        self.db_model = None

    def connect_to_opentrons_query(self, opentrons_id, slot, well_id):
        return f"""
        MATCH (n:Opentrons {{setup_id: "{opentrons_id}"}})-[:HAS_PART]->(m:Slot {{number: {slot}}})
        -[:HAS_PART]->(o:Opentron_Module)-[:HAS_PART]->(p:Well {{well_id: "{well_id}"}})
        RETURN p as well
        """

    def connect_to_materials_query(self, material, quantity, quantity_unit, material_id = None):
        if material_id is None or material_id == "":
            return f"""
            CREATE (n:Matter {{name: "{material}"}})-[:HAS_PROPERTY]->(m:Quantity {{value: {quantity}, unit: "{quantity_unit}"}})
            RETURN n
            """
        else:
            return f"""
            MATCH (n:Material {{material_id: "{material_id}"}})
            (n)-[:HAS_PROPERTY]->(m:Quantity)
            SET m.value = {quantity}
            RETURN n
            """




    @abstractmethod
    def perform_action(self, connection, *args):
        pass



class PumpRelay(RelayClass):
    def __init__(self, relay_num: int, name: str, properties: dict):
        super().__init__(relay_num, name, properties)
        self.pump_slope = properties["calibration"]["slope"]
        self.pump_intercept = properties["calibration"]["intercept"]
        self.inlet = properties["inlet"]
        self.outlet = properties["outlet"]
        self.db_model = Pump
        self.device_node = None
        self.relay_node = None

    def perform_action(self, connection, volume: float):
        time_on = self.pump_slope * volume + self.pump_intercept
        command = f"<set_relay_on_time,{self.relay_num},{round(time_on * 1000, 0)}>"
        connection.write(command.encode())
        LOGGER.info(f"Pump {self.name} set on for {time_on} seconds to dispense {volume} ml from {self.inlet} to {self.outlet}")

    def save(self, *args, **kwargs):
        self.device_node = self.db_model(
            name=self.name,
            relay_num=self.relay_num,
            pump_slope=self.pump_slope,
            pump_intercept=self.pump_intercept,
        )
        self.relay_node = Relay(
            relay_id=self.name,
            name=self.name
        )
        self.device_node.save()
        self.relay_node.save()
        self.device_node.device.connect(self.relay_node)
        self.add_inlet_outlet(self.device_node, **kwargs)

    def add_inlet_outlet(self, node, **kwargs):

        if 'inlet' in self.__dict__:
            if self.inlet['device'] == "opentrons":
                self.connect_to_opentrons(node, self.inlet, "inlet", **kwargs)
            if self.inlet['device'] == "material":
                self.connect_to_materials(node, self.inlet, "inlet", **kwargs)
        if 'outlet' in self.__dict__:
            if self.outlet['device'] == "opentrons":
                self.connect_to_opentrons(node, self.outlet, "outlet", **kwargs)
            if self.outlet['device'] == "material":
                self.connect_to_materials(node, self.outlet, "outlet", **kwargs)
    def connect_to_materials(self, node, connection_props, connection_type, **kwargs):
        print("connection_props", connection_props)
        material = connection_props["properties"]["material"]
        quantity = connection_props["properties"]["quantity"]["value"]
        quantity_unit = connection_props["properties"]["quantity"]["unit"]
        material_id = connection_props["properties"].get("material_id", None)
        query = self.connect_to_materials_query(material, quantity, quantity_unit, material_id)
        print(query)
        result, _ = db.cypher_query(query, resolve_objects=True)
        material = result[0][0]
        if connection_type == "inlet":
            reservoir = Reservoir(
                name=material.name,
            )
            reservoir.save()
            reservoir.material.connect(material)
            node.inlet.connect(reservoir)
        elif connection_type == "outlet":
            reservoir = Reservoir(
                name=material.name,
            )
            reservoir.save()
            reservoir.material.connect(material)
            node.outlet.connect

    def connect_to_opentrons(self, node, connection_props, connection_type, **kwargs):
        print("connection_props", connection_props)
        opentrons_id = kwargs.get("opentrons_id")
        slot = connection_props["properties"]['slot']
        well_id = connection_props["properties"]['well']
        query = self.connect_to_opentrons_query(opentrons_id, slot, well_id)
        print(query)
        result, _ = db.cypher_query(query, resolve_objects=True)
        well = result[0][0]
        if connection_type == "inlet":
            node.inlet.connect(well)
        elif connection_type == "outlet":
            node.outlet.connect(well)




class UltrasonicRelay(RelayClass):
    def __init__(self, relay_num: int, name: str, properties: dict):
        super().__init__(relay_num, name, properties)
        self.connected_to = properties.get("connected_to", None)
        self.UltrasonicNode = Ultrasonic

    def perform_action(self, connection, time_on: float):
        command = f"<set_relay_on_time,{self.relay_num},{round(time_on * 1000, 0)}>"
        connection.write(command.encode())
        LOGGER.info(f"Ultrasonic {self.name} in slot {self.slot} set on for {time_on} seconds")


    def save(self, **kwargs):
        self.device_node = self.UltrasonicNode(
            name=self.name,
            relay_num=self.relay_num,
            connected_to=self.connected_to
        )
        self.relay_node = Relay(
            relay_id=self.name,
            name=self.name
        )
        self.device_node.save()
        self.relay_node.save()
        self.device_node.device.connect(self.relay_node)
        self.add_connected_to(self.device_node, **kwargs)


    def add_connected_to(self, node, **kwargs):
        if self.connected_to['device'] == "opentrons":
            opentrons_id = kwargs.get("opentrons_id")
            print(self.connected_to)
            query = self.connect_to_opentrons_query(opentrons_id, self.connected_to['properties']["slot"], self.connected_to['properties']["well"])
            result, _ = db.cypher_query(query, resolve_objects=True)
            well = result[0][0]
            print(node, type(node))
            print(well, type(well))
            node.slot.connect(well)
        elif self.connected_to['device'] == "material":
            query = self.connect_to_materials_query(self.connected_to['properties']["material"], self.connected_to['properties']["quantity"], self.connected_to['properties']["quantity_unit"], self.connected_to['properties']["material_id"])
            result, _ = db.cypher_query(query, resolve_objects=True)
            material = result[0][0]
            node.connected_to.connect(material)

