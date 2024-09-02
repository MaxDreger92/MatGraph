import json
import os
from datetime import datetime

import requests
from neomodel import db, DateTimeProperty

from mat2devplatform.settings import BASE_DIR
from matgraph.models.matter import Material
from matgraph.models.properties import Property
from sdl.models import Opentron_Module, Opentrons, Pipette
from sdl.setup.ExperimentalSetup import SDLSetup


class OpentronsSetup(SDLSetup):
    def __init__(self, robot_config_source, labware_config_source, chemicals_config_source, logger, ip=None, port=None, model=Opentrons):
        """
        Initialize the Opentrons setup with configuration source and model.

        Args:
            robot_config_source (Union[dict, str, Model, URL]): The source of the configuration.
            labware_config_source (Union[dict, str, Model, URL]): The source of the labware configuration.
            model (Model): Django model for database operations.
        """
        super().__init__(robot_config_source, model)
        self.name_space = "opentrons"
        self._robot_ip = ip
        self._port = port
        self._headers = robot_config_source.get("headers", {})
        self._run_id = None
        self.labware_config = self.load_configuration(labware_config_source)
        self.chemicals_config = self.load_configuration(chemicals_config_source)
        self.pipettes = {}
        self.logger = logger

    @property
    def info(self):
        return {
            "opentrons_ip": self.robot_ip,
            "opentrons_port": self.port,
            "opentrons_headers": self.headers,
            "opentrons_run_id": self.run_id,
            "opentrons_id": self.setup_id
        }

    def setup(self, simulate = False):
        """
        Load configuration, validate it, initialize the robot, and save the setup ID.
        """
        self.simulate = simulate
        self.load_config()
        self.validate_config()
        self.initialize_platform()
        self.save(setup_id=self.setup_id)
        self.initialize_modules()
        self.loadPipette()


    def initialize_platform(self):
            '''
            creates a new blank run on the opentrons with command endpoints

            arguments
            ----------
            None

            returns
            ----------
            None
            '''
            if self.simulate:
                self._run_id = "simulate"
                self.logger.info("Simulating Opentrons")
                return

            strRunURL = f"http://{self.robot_ip}:{self.port}/runs"
            response = requests.post(url=strRunURL,
                                     headers=self.headers,
                                     )

            if response.status_code == 201:
                dicResponse = json.loads(response.text)
                # get the run ID

                self._run_id = dicResponse['data']['id']
                # setup command endpoints
                self.commandURL = strRunURL + f"/{self.run_id}/commands"

                # LOG - info
                self.logger.info(f"New run created with ID: {self.run_id}")
                self.logger.info(f"Command URL: {self.commandURL}")
                print(f"New run created with ID: {self.run_id}")
                print(f"Command URL: {self.commandURL}")
            else:
                raise Exception(
                    f"Failed to create a new run.\nError code: {response.status_code}\n Error message: {response.text}")


    def save_graph(self, **kwargs):
        """
        Save the initialized modules to the graph.
        """
        for lw in self.labware_config["labware"]:
            module_id = lw.get("module_id")
            if module_id is not None:
                json_file = None
                labware_file_path = os.path.join(BASE_DIR, 'sdl', 'config', 'labware', lw['filename'])
                try:
                    with open(labware_file_path, encoding ='utf-8') as f:
                        json_file = json.load(f)
                except FileNotFoundError:
                    pass

                if json_file is not None:
                    module = Opentron_Module.from_json(json_file)
                else:
                    module = Opentron_Module(name=lw["name"], date_added="2024-07-13")

                module.module_id = lw["module_id"]
                module.save()
                module.add_slot(self.setup_id, lw["slot"])
                self.logger.info(f"Saved module {module.name} with ID {module_id} to the graph")
        self.initialize_chemicals()




    def initialize_modules(self):
        """
        Initialize the Opentrons modules.
        """
        schema_path = os.path.join(BASE_DIR, 'sdl', 'Robot', 'config', 'labware', 'schemas', 'labware_schema.json')

        for i, lw in enumerate(self.labware_config["labware"]):
            labware_file_path = os.path.join(BASE_DIR, 'sdl', 'config', 'labware', lw['filename'])
            json_file = None  # Default value if file does not exist
            try:
                with open(labware_file_path,encoding='utf-8') as f:
                    json_file = json.load(f)
            except FileNotFoundError:
                pass

            # Assuming you have a method to load labware
            if self.simulate:
                module_id = "simulate"
            else:
                module_id = self.load_labware(
                    slot=lw["slot"],
                    name=lw["name"],
                    schema=json_file,
                    name_space=lw["namespace"],
                    version=lw["version"],
                    intent=lw["intent"],
                )

            self.labware_config["labware"][i]["module_id"] = module_id  # Add module_id to labware_config

    def initialize_chemicals(self):
        """
        Initialize the chemicals/materials.
        """
        for i, chem in enumerate(self.chemicals_config["opentrons"]):
            self.add_material(
                slot=chem["location"]["slot"],
                well=chem["location"]["well"],
                name=chem["name"],
                quantity=chem["volume"]["value"],
                unit = chem["volume"]["unit"]
            )


    def get_labware_id(self, slot):
        """
        Get the labware ID for a given slot.

        Args:
            slot (int): Slot number.

        Returns:
            str: Labware ID.
        """
        query = f"MATCH (o:Opentrons {{uid: '{self.setup_model.uid}'}})-[:HAS_PART]->(s:Slot {{number: '{slot}'}})-[:HAS_PART]->(m:Opentron_Module) RETURN m.module_id"
        labware_id = db.cypher_query(query, resolve_objects=False)[0][0][0]
        if labware_id:
            return labware_id
        else:
            return None



    def get_labware_id_by_name(self, name):
        """
        Get the labware ID for a given name.

        Args:
            name (str): Name of the labware.

        Returns:
            str: Labware ID.
        """
        query = f"MATCH (o:Opentrons {{uid: '{self.setup_model.uid}'}})-[:HAS_PART]->(:Slot)-[:HAS_PART]->(m:Opentron_Module {{name: '{name}'}}) RETURN m.module_id"
        result = db.cypher_query(query, resolve_objects=False)
        print(result)
        print(query)
        labware_id =result[0][0][0]
        if labware_id:
            return labware_id
        else:
            return None

    def get_pipette_id(self, name):
        """
        Get the pipette ID for a given name.

        Args:
            name (str): Name of the pipette.

        Returns:
            str: Pipette ID.
        """
        if not name:
            return self.default_pipette
        query = f"MATCH (o:Opentrons {{uid: '{self.setup_model.uid}'}})-[:HAS_PART]->(p:Pipette {{name: '{name}'}}) RETURN p.module_id"
        pipette_id = db.cypher_query(query, resolve_objects=False)[0][0][0]
        if pipette_id:
            return pipette_id
        else:
            return

    def loadPipette(self,
                    strMount = 'right'

                    ):
        '''
        loads a pipette onto the robot

        arguments
        ----------
        strPipetteName: str
            the name of the pipette to be loaded

        strMount: str
            the mount where the pipette is to be loaded

        returns
        ----------
        None
        '''
        for pipette in self.labware_config["pipettes"]:
            strPipetteName = pipette["name"]
            strMount = pipette["mount"]
            dicCommand = {
                "data": {
                    "commandType": "loadPipette",
                    "params": {
                        "pipetteName": strPipetteName,
                        "mount": strMount
                    },
                    "intent": "setup"
                }
            }

            strCommand = json.dumps(dicCommand)


            if not self.simulate:
                response = requests.post(
                    url = self.commandURL,
                    headers = self.headers,
                    params = {"waitUntilComplete": True},
                    data = strCommand
                )

                # LOG - debug

                if response.status_code == 201:
                    dicResponse = json.loads(response.text)
                    print(dicResponse)
                    strPipetteID = dicResponse['data']['result']['pipetteId']
                    self.pipettes[strPipetteName] = {"id": strPipetteID, "mount": strMount}
                    self.logger.info(f"Pipette loaded with name: {strPipetteName} and ID: {strPipetteID}")
                    pipette_node = Pipette(date_added = DateTimeProperty(), name=strPipetteName, module_id=strPipetteID)
                    pipette_node.save()
                    self.setup_model.pipettes.connect(pipette_node)

                    if len(self.pipettes) == 1:
                        self.default_pipette = strPipetteID
                        self.logger.info(f"Default pipette set to {strPipetteID}")
                        print(f"Default pipette set to {strPipetteID}")
                    # LOG - info
                else:
                    raise Exception(
                        f"Failed to load pipette.\nError code: {response.status_code}\n Error message: {response.text}"
                    )
            else:
                self.logger.info(f"Simulating loading pipette with name: {strPipetteName} and mount: {strMount}")
                print(f"Simulating loading pipette with name: {strPipetteName} and mount: {strMount}")



    def load_labware(self, slot,
                     name,
                     schema,
                     name_space,
                     version,
                     intent,
                     ):
        '''
        loads custom labware onto the robot

        arguments
        ----------
        dicLabware: dict
            the JSON object of the custom labware to be loaded (directly from opentrons labware definitions)

        intSlot: int
            the slot number where the labware is to be loaded

        strLabwareID: str
            the ID of the labware to be loaded - to be used for loading the same labware multiple times
            default: None

        returns
        ----------
        None
        '''
        if schema != None:
            dicCommand = {'data': schema}

            strCommand = json.dumps(dicCommand)

            # LOG - info
            self.logger.info(f"Loading custom labware: {name} in slot: {slot}")
            # # LOG - debug
            # LOGGER.debug(f"Command: {strCommand}")

            response = requests.post(
                url=f"http://{self.robot_ip}:{self.port}/runs/{self.run_id}/labware_definitions",
                headers=self.headers,
                params = {"waitUntilComplete": True},
                data=strCommand
            )

            # LOG - debug
            # LOGGER.debug(f"Response: {response.text}")

            if response.status_code != 201:
                raise Exception(
                    f"Failed to load custom labware.\nError code: {response.status_code}\n Error message: {response.text}")
            # LOG - info
            self.logger.info(f"Custome labware {name} loaded in slot: {slot} successfully.")
            # load the labware

        dicCommand = {
            "data": {
                "commandType": "loadLabware",
                "params": {
                    "location": {"slotName": str(slot)},
                    "loadName": name,
                    "namespace": name_space,
                    "version": version
                },
                "intent": intent
            }
        }

        strCommand = json.dumps(dicCommand)

        # LOG - info
        self.logger.info(f"Loading labware: {name} in slot: {slot}")
        # LOG - debug
        # self.logger.debug(f"Command: {strCommand}")

        response = requests.post(
            url=self.commandURL,
            headers=self.headers,
            params={"waitUntilComplete": True},
            data=strCommand
        )

        # LOG - debug
        # LOGGER.debug(f"Response: {response.text}")

        if response.status_code == 201:
            dicResponse = json.loads(response.text)
            print(dicResponse)
            print(dicResponse)
            if dicResponse['data']['result']['definition']['parameters']['isTiprack']:
                self.tiprackID = dicResponse['data']['result']['labwareId']
            strLabwareID = dicResponse['data']['result']['labwareId']

            # LOG - info
            self.logger.info(f"Labware loaded with name: {name} and ID: {strLabwareID}")
        else:
            raise Exception(
                f"Failed to load labware.\nError code: {response.status_code}\n Error message: {response.text}")

        return strLabwareID


    def add_material(self, slot, well, name, quantity, unit):
        """
        Add material/chemical to a module.

        Args:
            slot (int): Slot number of the module.
            coordinates (tuple): Coordinates of the module (x, y, z).
            name (str): Name of the material/chemical.
            quantity (float): Quantity of the material/chemical.
        """
        self.logger.info(f"Adding material {name} to slot {slot} at coordinates {well} with quantity {quantity}")
        query = f"""MATCH (:Opentrons {{uid: '{self.setup_model.uid}'}})-[r:HAS_PART]->(s:Slot {{number: '{str(slot)}'}})
        -[:HAS_PART]->(m:Opentron_Module)-[:HAS_PART]->(W:Well{{well_id: '{well}'}}) RETURN W"""
        # Assuming the module has a method to add material
        try:
            slot = db.cypher_query(query, resolve_objects=True)[0][0][0]
        except:
            raise Exception(f"Well {well} and slot {slot} could not be found")
        mat = Material(name=name)
        prop = Property(name="amount", value=quantity, unit = unit)
        prop.save()
        mat.save()
        mat.properties.connect(prop)
        mat.by.connect(slot)





    @property
    def robot_ip(self):
        return self._robot_ip

    @robot_ip.setter
    def robot_ip(self, value):
        self._robot_ip = value

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, value):
        self._headers = value

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        self._port = value

    @property
    def base_url(self):
        return f"http://{self.robot_ip}:{self.port}"

    @property
    def run_url(self):
        return f"{self.base_url}/runs"

    @property
    def command_url(self):
        return f"{self.run_url}/{self.run_id}/commands"

    @property
    def setup_id(self):
        if not self._setup_id:
            self._setup_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{self.run_id}-{self.user}"
        return self._setup_id

    @setup_id.setter
    def setup_id(self, value):
        self._setup_id = value if value else f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{self.run_id}-{self.user}"

    @property
    def run_id(self):
        return self._run_id

    @run_id.setter
    def run_id(self, value):
        self._run_id = value

