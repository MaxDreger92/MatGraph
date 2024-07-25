import json
import os
from datetime import datetime

import requests
from Arduino import Arduino
from neomodel import db

from mat2devplatform.settings import BASE_DIR
from matgraph.models.matter import Material
from matgraph.models.properties import Property
from sdl.models import Opentron_O2, Opentron_Module


class BaseSetup:
    def __init__(self, config_source, db_model):
        """
        Initialize the base experimental setup with configuration source and database model.

        Args:
            config_source (Union[dict, str, Model, URL]): The source of the configuration.
            db_model (Model): Django model for database operations.
        """
        self.config_source = self.load_configuration(config_source)
        self.setup_model = db_model
        self.config = None
        self.name_space = None  # needs to be implemented in subclass

    def load_config(self):
        """
        Load configuration from the specified source.
        """
        self.config = self.load_configuration(self.config_source)

    def load_configuration(self, config_source):
        """
        Load configuration from various sources: dict, file path, model, or URL.

        Args:
            config_source (Union[dict, str, Model, URL]): The source of the configuration.

        Returns:
            dict: The loaded configuration as a dictionary.

        Raises:
            ValueError: If the config source type is unsupported.
        """
        if isinstance(config_source, dict):
            return config_source
        elif isinstance(config_source, str):
            if config_source.startswith(('http://', 'https://')):
                response = requests.get(config_source)
                response.raise_for_status()
                return response.json()
            else:
                with open(config_source, 'r') as file:
                    return json.load(file)
        elif hasattr(config_source, 'get_config'):
            return config_source.get_config()
        else:
            raise ValueError("Unsupported configuration source type")

    def validate_config(self):
        """
        Validate the configuration settings.
        """
        # Implement validation logic if needed
        pass

    def save(self, **kwargs):
        """
        Store data in the database using Django ORM.

        Args:
            **kwargs: Key-value pairs of model fields and values.

        Returns:
            obj (Model): Saved Django model instance.
        """
        obj = self.setup_model(**kwargs)
        self.setup_model = obj
        obj.save()
        return obj

    def setup(self):
        """
        Load configuration, validate it, perform setup, and store results.
        """
        self.load_config()
        self.validate_config()
        self.perform_setup()
        self.store()

    def perform_setup(self):
        """
        Abstract method to be implemented by subclasses for specific setup tasks.
        """
        raise NotImplementedError


class SDLSetup(BaseSetup):
    def __init__(self, config_source, model):
        """
        Initialize the SDL setup with configuration source and model.

        Args:
            config_source (Union[dict, str, Model, URL]): The source of the configuration.
            model (Model): Django model for database operations.
        """
        super().__init__(config_source, model)
        self._setup_id = None
        self._user = None

    def setup(self):
        """
        Load configuration and set up SDL.
        """
        self.load_config()
        self.setup_sdl()

    def setup_sdl(self):
        """
        Set up SDL including generating a setup ID and initializing the robot.
        """
        self.setup_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{self.config['runNumber']}_{self.user}"
        self.initialize_platform()

    @property
    def setup_id(self):
        return self._setup_id

    @setup_id.setter
    def setup_id(self, value):
        self._setup_id = value if value else f'{datetime.now()}_{self.config["runNumber"]}_{self.user}'

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        self._user = value

    def initialize_platform(self):
        """
        Placeholder method for robot initialization.
        """
        return NotImplementedError


class OpentronsSetup(SDLSetup):
    def __init__(self, robot_config_source, labware_config_source, ip=None, port=None, model=Opentron_O2):
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
        self._labware_config = self.load_configuration(labware_config_source)
        self.pipettes = {}

    def setup(self):
        """
        Load configuration, validate it, initialize the robot, and save the setup ID.
        """
        print("Setting up Opentrons")
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

        strRunURL = f"http://{self.robot_ip}:{self.port}/runs"
        response = requests.post(url=strRunURL,
                                 headers=self.headers,
                                 )

        if response.status_code == 201:
            dicResponse = json.loads(response.text)
            # get the run ID
            self.runID = dicResponse['data']['id']
            # setup command endpoints
            self.commandURL = strRunURL + f"/{self.runID}/commands"

            # LOG - info
            # LOGGER.info(f"New run created with ID: {self.runID}")
            # LOGGER.info(f"Command URL: {self.commandURL}")
            print(f"New run created with ID: {self.runID}")
            print(f"Command URL: {self.commandURL}")
        else:
            raise Exception(
                f"Failed to create a new run.\nError code: {response.status_code}\n Error message: {response.text}")

    def initialize_modules(self):
        """
        Initialize the Opentrons modules.
        """
        schema_path = os.path.join(BASE_DIR, 'sdl', 'Robot', 'config', 'labware', 'schemas', 'labware_schema.json')
        schema = json.load(open(schema_path))

        for lw in self.labware_config["labware"]:
            # if lw['namespace'] == 'opentrons':
            #     continue
            labware_file_path = os.path.join(BASE_DIR, 'sdl', 'Robot', 'config', 'labware', lw['filename'])
            json_file = None  # Default value if file does not exist
            try:
                with open(labware_file_path) as f:
                    json_file = json.load(f)
            except FileNotFoundError:
                pass
             # self.validate_json(json_file, schema)


            # Assuming you have a method to load labware
            module_id = self.load_labware(
                slot=lw["slot"],
                name=lw["name"],
                schema=json_file,
                name_space=lw["namespace"],
                version=lw["version"],
                intent=lw["intent"],
            )
            if json_file != None:
                module = Opentron_Module.from_json(json_file)
            else:
                module = Opentron_Module(name=lw["name"], date_added="2024-07-13")
            module.module_id = module_id
            module.save()
            module.add_slot(self.setup_id, lw["slot"])

            print("Initialized module:", module)

    def get_labware_id(self, slot):
        """
        Get the labware ID for a given slot.

        Args:
            slot (int): Slot number.

        Returns:
            str: Labware ID.
        """
        query = f"MATCH (o:Opentron_O2 {{uid: '{self.setup_model.uid}'}})-[:HAS_PART]->(s:Slot {{number: {slot}}})-[:HAS_PART]->(m:Opentron_Module) RETURN m.module_id"
        labware_id = db.cypher_query(query, resolve_objects=False)[0][0][0]
        if labware_id:
            return labware_id
        else:
            return None

    def loadPipette(self,
                    strPipetteName = 'p50_single_flex',
                    strMount = 'left'

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
            if len(self.pipettes) == 1:
                self.default_pipette = strPipetteID
                print(f"Default pipette set to {strPipetteID}")
            # LOG - info
        else:
            raise Exception(
                f"Failed to load pipette.\nError code: {response.status_code}\n Error message: {response.text}"
            )


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
        print(f"Loading labware {name} in slot {slot}")
        if schema != None:
            dicCommand = {'data': schema}

            strCommand = json.dumps(dicCommand)

            # LOG - info
            # LOGGER.info(f"Loading custom labware: {dicLabware['parameters']['loadName']} in slot: {intSlot}")
            # # LOG - debug
            # LOGGER.debug(f"Command: {strCommand}")

            response = requests.post(
                url=f"http://{self.robot_ip}:{self.port}/runs/{self.runID}/labware_definitions",
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
            # LOGGER.info(f"Custome labware {dicLabware['parameters']['loadName']} loaded in slot: {intSlot} successfully.")
            # load the labware

        dicCommand = {
            "data": {
                "commandType": "loadLabware",
                "params": {
                    "location": {"slotName": str(slot)},
                    "loadName": name,
                    "namespace": name_space,
                    "version": str(version)
                },
                "intent": intent
            }
        }

        strCommand = json.dumps(dicCommand)

        # LOG - info
        # LOGGER.info(f"Loading labware: {strLabwareName} in slot: {intSlot}")
        # LOG - debug
        # LOGGER.debug(f"Command: {strCommand}")

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
            # strLabwareURi = dicResponse['data']['result']['labwareUri']
            # strLabwareIdentifier_temp = name + "_" + str(slot)
            # LOG - info
            # LOGGER.info(f"Labware loaded with name: {strLabwareName} and ID: {strLabwareID}")
        else:
            raise Exception(
                f"Failed to load labware.\nError code: {response.status_code}\n Error message: {response.text}")

        return strLabwareID


    def add_material(self, slot, coordinates, name, quantity):
        """
        Add material/chemical to a module.

        Args:
            slot (int): Slot number of the module.
            coordinates (tuple): Coordinates of the module (x, y, z).
            name (str): Name of the material/chemical.
            quantity (float): Quantity of the material/chemical.
        """
        print(f"Adding material {name} to slot {slot} at coordinates {coordinates} with quantity {quantity}")
        query = f"""MATCH (:Opentron_O2 {{uid: '{self.setup_model.uid}'}})-[r:HAS_PART]->(s:Slot {{number: {int(slot)}}})
        -[:HAS_PART]->(m:Opentron_Module)-[:HAS_PART]->(W:Well{{well_id: '{coordinates}'}}) RETURN s"""
        # Assuming the module has a method to add material
        print("query", query)
        well = db.cypher_query(query, resolve_objects=True)[0][0][0]
        print("well", well)
        if well:
            mat = Material(name=name)
            prop = Property(name="amount", value=quantity)
            prop.save()
            mat.save()
            mat.properties.connect(prop)
            mat.by.connect(well)
            print(f"Added material {name} to module in slot {slot}")
        else:
            print(f"Module in slot {slot} not found")

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

    @property
    def labware_config(self):
        return self._labware_config


class ExternalDeviceSetup(BaseSetup):
    def __init__(self, config_source):
        """
        Initialize the external device setup with configuration source.

        Args:
            config_source (Union[dict, str, Model, URL]): The source of the configuration.
        """
        super().__init__(config_source, None)
        self.devices = []

    def setup(self):
        """
        Load configuration, validate it, and set up external devices.
        """
        self.load_config()
        self.validate_config()
        self.setup_devices()

    def setup_devices(self):
        """
        Initialize and configure external devices.
        """
        for device_config in self.config['labware']:
            device = self.initialize_device(device_config)
            self.validate_device(device)
            self.devices.append(device)

    def initialize_device(self, device_config):
        """
        Initialize an external device.

        Args:
            device_config (dict): Configuration for the device.
        """
        pass

    def validate_device(self, device):
        """
        Validate the device configuration.

        Args:
            device (dict): Device configuration.
        """
        pass


class ArduinoSetup(BaseSetup):
    def __init__(self, config_source, model):
        """
        Initialize the Arduino setup with configuration source and model.

        Args:
            config_source (Union[dict, str, Model, URL]): The source of the configuration.
            model (Model): Django model for database operations.
        """
        super().__init__(config_source, model)
        self.arduino = None
        self.name_space = "arduino"  # Important for mapping to procedures

    def setup(self):
        """
        Load configuration, validate it, initialize the Arduino, and save the setup ID.
        """
        self.load_config()
        self.validate_config()
        self.initialize_arduino()
        self.save(setup_id=self.setup_id)

    def initialize_arduino(self):
        """
        Initialize the Arduino based on the configuration.
        """
        self.arduino = Arduino(
            arduino_search_string=self.config.get("arduino_search_string", "CH340"),
            list_of_cartridges=self.config.get("list_of_cartridges", [0, 1]),
            list_of_pump_relays=self.config.get("list_of_pump_relays", [0, 1, 2, 3, 4, 5]),
            list_of_ultrasonic_relays=self.config.get("list_of_ultrasonic_relays", [6, 7]),
            pump_slope=self.config.get("pump_slope", {0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0}),
            pump_intercept=self.config.get("pump_intercept", {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0}),
        )
