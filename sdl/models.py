import os
from datetime import datetime
import time

from neomodel import UniqueIdProperty, FloatProperty, StringProperty, RelationshipTo, IntegerProperty, DateTimeProperty, \
    RelationshipFrom

from neomodel import db
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from matgraph.models.metadata import Metadata
from matgraph.models.relationships import HasPartRel, InLocationRel


# Create your models here.

class Well(BaseModel):
    depth: float
    totalLiquidVolume: float
    shape: str
    diameter: Optional[float] = None
    xDimension: Optional[float] = None
    yDimension: Optional[float] = None
    x: float
    y: float
    z: float

class Module(BaseModel):
    ordering: List[List[str]]
    brand: Dict[str, Any]
    metadata: Dict[str, Any]
    dimensions: Dict[str, float]
    wells: Dict[str, Well]
    groups: List[Dict[str, Any]]
    parameters: Dict[str, Any]
    namespace: str
    version: int
    schemaVersion: int
    cornerOffsetFromSlot: Dict[str, float]

    @classmethod
    def from_json(cls, data: Dict[str, Any]):
        wells_data = {well_id: Well(**well_attr) for well_id, well_attr in data.pop('wells').items()}
        return cls(wells=wells_data, **data)


class Well(Metadata):
    uid = UniqueIdProperty()
    depth = FloatProperty()
    totalLiquidVolume = FloatProperty()
    shape = StringProperty()
    diameter = FloatProperty()
    xDimension = FloatProperty()
    yDimension = FloatProperty()
    x = FloatProperty()
    y = FloatProperty()
    z = FloatProperty()
    well_id = StringProperty()

    def __str__(self):
        return f"Well {self.uid}"
    class Meta(Metadata.Meta):
        pass


class Opentron_Module(Metadata):
    """
    Abstract base class representing a Module in the knowledge graph.

    name: The name of the module.
    """
    name = StringProperty()
    date_added = StringProperty(required=True)
    wells = RelationshipTo('Well', 'HAS_PART', model=HasPartRel)
    module_id = StringProperty(unique=True)

    def __str__(self):
        return self.name

    @classmethod
    def from_json(cls, data: Dict[str, Any]):
        module_instance = cls(name=data["metadata"]["displayName"], date_added="2024-07-13")
        module_instance.save()

        wells_data = data.pop('wells')
        for well_id, well_attr in wells_data.items():
            well_instance = Well(well_id = well_id, **well_attr)
            well_instance.save()
            module_instance.wells.connect(well_instance)

        return module_instance

    def add_slot(self, ExperimentID, slot):
        query = f'''
            MATCH (o:Opentrons {{setup_id: '{ExperimentID}'}})-[:HAS_PART]->(s:Slot {{number: {slot}}})
            MATCH (m:Opentron_Module {{uid: '{self.uid}'}})
            WITH DISTINCT s, m
            CREATE (m)<-[:HAS_PART]-(s)
        '''

        res,_ = db.cypher_query(query, {})



    class Meta(Metadata.Meta):
        pass

class Slot(Metadata):
    number = IntegerProperty(unique=True, required=True)

    def __str__(self):
        return f"Slot {self.number}"



class Opentrons(Metadata):
    setup_id = StringProperty(unique=True, required=True)
    date_added = DateTimeProperty(default=datetime.now())
    slots = RelationshipTo('Slot', 'HAS_PART', model=HasPartRel)

    def save(self):
        super().save()
        for i in range(1, 13):
            slot = Slot(number=i)
            slot.save()
            self.slots.connect(slot)

    def __str__(self):
        return f"Opentron_O2 {self.experiment_id}"

    class Meta(Metadata.Meta):
        pass



class ArduinoModule(Metadata):
    setup_id = StringProperty(unique=True, required=True)
    date_added = DateTimeProperty(default=datetime.now())
    relay = RelationshipTo('Relay', 'HAS_PART', model=HasPartRel)
    cartridge = RelationshipTo('Slot', 'HAS_PART', model=HasPartRel)

    def save(self):
        super().save()
        for i in range(1, 13):
            slot = Slot(number=i)
            slot.save()
            self.slots.connect(slot)

    def __str__(self):
        return f"ArduinoModule {self.experiment_id}"

    class Meta(Metadata.Meta):
        pass

class ArduinoBoard(Metadata):
    date_added = DateTimeProperty(default=datetime.now())
    relay = RelationshipTo('Relay', 'HAS_PART', model=HasPartRel)
    cartridge = RelationshipTo('Slot', 'HAS_PART', model=HasPartRel)
    baud_rate = IntegerProperty()
    port = StringProperty()


    def __str__(self):
        return f"ArduinoSetup {self.experiment_id}"

    class Meta(Metadata.Meta):
        pass


class Relay(Metadata):
    relay_id = StringProperty(required=True)
    name = StringProperty(required=True)
    device = RelationshipTo('Metadata', 'HAS_PART', model=HasPartRel)

class Pump(Metadata):
    name = StringProperty(required=True)
    pump_slope = FloatProperty()
    pump_intercept = FloatProperty()
    device = RelationshipTo('matgraph.models.metadata.Metadata', 'HAS_PART', model=HasPartRel)
    inlet = RelationshipTo('matgraph.models.metadata.Metadata', 'HAS_PART', model=HasPartRel)
    outlet = RelationshipTo('matgraph.models.metadata.Metadata', 'HAS_PART', model=HasPartRel)

    slope = FloatProperty()
    intercept = FloatProperty()

class Ultrasonic(Metadata):
    name = StringProperty(required=True)
    device = RelationshipTo('Metadata', 'HAS_PART', model=HasPartRel)
    slot = RelationshipTo('Metadata', 'HAS_PART', model=HasPartRel)
    connected_to = RelationshipTo('Metadata', 'HAS_PART', model=HasPartRel)

class Reservoir(Metadata):
    name = StringProperty(required=True)
    device = RelationshipTo('Metadata', 'HAS_PART', model=HasPartRel)
    slot = RelationshipTo('Metadata', 'HAS_PART', model=HasPartRel)
    connected_to = RelationshipTo('Metadata', 'HAS_PART', model=HasPartRel)
    material = RelationshipFrom('matgraph.models.matter.Matter', 'IN', model=InLocationRel)
    volume = FloatProperty()
    unit = StringProperty()