import json
import logging
import os
import uuid
from typing import Union, List

from django.db.models import Q
from neomodel import db
from pydantic import BaseModel, ValidationError

from mat2devplatform.settings import BASE_DIR
from sdl.models import Job
from sdl.setup.arduino_setup.ArduinoSetup import ArduinoSetup
from sdl.setup.biologic_setup.BiologicSetup import BiologicSetup
from sdl.setup.opentrons_setup.OpentronsSetup import OpentronsSetup
from sdl.workflow.utils import BaseWorkflow, BaseProcedure, BaseStep, Chemical, SetupModel, Chemicals


class JobRequest:
    def __init__(self, job_request: json, job_uid: Union[str, uuid.UUID] = None):
        self.job_request = job_request
        self.workflow = self.create_workflow()
        self.requirements = self.workflow.get_requirements()
        self.job_uid = job_uid or uuid.uuid4()
        self.queue_job()

    def create_workflow(self):
        try:
            return BaseWorkflow.from_config(self.job_request)
        except KeyError as e:
            raise ValueError(f"Invalid workflow configuration: {str(e)}")

    def queue_job(self):
        requirements = self.parse_requirements()
        model_data = {
            'id': self.job_uid,
            **requirements,
            'workflow': self.job_request
        }
        self.model = Job(**model_data)
        self.model.save()

    def parse_requirements(self):
        try:
            requirements = json.loads(self.requirements.json())
            return {
                'opentrons': requirements.get('opentrons'),
                'opentrons_setup': requirements.get('opentrons_setup'),
                'chemicals': requirements.get('chemicals'),
                'arduino': requirements.get('arduino'),
                'biologic': requirements.get('biologic'),
                'arduino_setup': requirements.get('arduino_setup'),
            }
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing requirements: {str(e)}")


class Experiment:
    def __init__(self,
                 opentrons_config: json = None,
                 labware_config: json = None,
                 chemicals_config: json = None,
                 arduino_config: json = None,
                 relay_config: json = None,
                 biologic_config: json = None,
                 workflow: json = None,
                 experiment_id: Union[uuid, str] = None,
                 store_experiment: bool = True,
                 offset_config: json = None
                 ):
        """
        Initialize an experiment with a list of setups and a workflow.

        Args:
            setups (list): A list of setup instances.
            workflow (Workflow): An instance of a workflow.
        """
        self.experiment_id = uuid.uuid4() if experiment_id is None else experiment_id
        self.create_experiment_directory()
        self.logger = self.initialize_logger()
        self.setups = self.create_setups(opentrons_config, labware_config, chemicals_config, arduino_config,
                                         relay_config, biologic_config, offset_config)  # Using a dictionary for easy access by name
        self.workflow = self.create_workflow(workflow)
        self.outputs = []
        self.experiment_id = uuid.uuid4() if experiment_id is None else experiment_id

    def create_workflow(self, workflow):
        if workflow:
            return BaseWorkflow.from_config(workflow)
        raise KeyError("No workflow provided.")

    def create_setups(self, opentrons_config, labware_config, chemicals_config, arduino_config, relay_config,
                      biologic_config, offset_config):
        setups = {}
        if opentrons_config:
            opentrons = OpentronsSetup(robot_config_source=opentrons_config,
                                       labware_config_source=labware_config,
                                       chemicals_config_source=chemicals_config,
                                       offset_config=offset_config,
                                       ip=opentrons_config['ip'],
                                       port=opentrons_config['port'],
                                       logger=self.logger)
            setups['opentrons'] = opentrons
        if arduino_config:
            arduino = ArduinoSetup(config=arduino_config, relay_config=relay_config, logger=self.logger)
            setups['arduino'] = arduino
        if biologic_config:
            biologic = BiologicSetup(config_source=biologic_config, logger=self.logger)
            setups['biologic'] = biologic
        return setups

    def store_experiment(self):

        required_fields = {
            'id': self.experiment_id,
            'requirements': self.setups['opentrons'].config,
            'workflow': self.workflow.json()
        }

        # Use dictionary comprehension to conditionally add optional fields
        optional_fields = {key: self.setups[key].config for key in ['biologic', 'arduino'] if key in self.setups}

        if 'arduino' in optional_fields:
            optional_fields['arduino_relays'] = self.setups['arduino'].relay_config

        # Merge required fields and optional fields
        model_data = {**required_fields, **optional_fields}

        # Create the ExperimentModel instance
        self.model = Job(**model_data)
        self.model.save()

    def initialize_logger(self):
        logging_path = os.path.join(self.experiment_directory, 'logfile.log')
        logging.basicConfig(
            level=logging.INFO,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Set the logging format
            handlers=[
                logging.FileHandler("logfile.log"),  # Log to a file
                logging.StreamHandler()  # Log to console
            ]
        )
        return logging.getLogger(__name__)

    def create_experiment_directory(self):
        # Construct the directory path
        experiment_dir = os.path.join(BASE_DIR, str(self.experiment_id))
        self.experiment_directory = experiment_dir

        # Create the directory if it doesn't exist
        os.makedirs(experiment_dir, exist_ok=True)

    def update_setups(self, setup):
        self.setups[setup.name_space] = setup

    @property
    def configs(self):
        return {setup.name_space: setup.info for setup in self.setups.values()}

    def initialize_setups(self, simulate=False):
        """Initialize all setups."""
        for name, setup in self.setups.items():
            self.logger.info(f"Initializing setup '{name}'")
            setup.setup(simulate)
            self.update_setups(setup)

    def store_setups(self):
        """Store all setups..."""
        for name, setup in self.setups.items():
            self.logger.info(f"Storing setup '{name}'")
            kwargs = self.configs
            setup.save_graph(**kwargs)

    def execute(self, workflow=None, *args, **kwargs):
        # Check if the workflow is a list
        if isinstance(self.workflow, list):
            for sub_workflow in self.workflow:
                configs = {k: v for config in self.configs.values() for k, v in config.items()}
                output = sub_workflow.execute(**configs,
                                              logger=self.logger,
                                              experiment_id=self.experiment_id,
                                              opentrons_setup=self.setups['opentrons'],
                                              opentrons_offset = self.setups['opentrons'].offset_config,
                                              experiment_directory=self.experiment_directory)
                self.outputs = [*self.outputs, *output]
        else:
            output = self.workflow.execute(logger=self.logger,
                                           **self.configs,
                                           opentrons_setup=self.setups['opentrons'],
                                           opentrons_offset=self.setups['opentrons'].offset_config,
                                           experiment_id=self.experiment_id,
                                           experiment_directory=self.experiment_directory)
            if not isinstance(output, list):
                output = [output]
            self.outputs = [*self.outputs, *output]

    def find_chemicals(self, chemical_name, opentrons_id):
        query = f'''
            MATCH (p:Property)<-[:HAS_PROPERTY]-(c:Matter {{name: '{chemical_name}'}})-[:IN|HAS_METADATA]->(m:Metadata)<-[:HAS_PART*..5]-(o:Opentrons {{setup_id: '{opentrons_id}'}})
            WHERE p.name = 'amount' OR p.name = 'Quantity'
            RETURN c.name, p.value, p.unit'''
        res, _ = db.cypher_query(query, {})

        return res

    def find_labware(self, labware_name, opentrons_id):
        query = f'''
            MATCH (l:Labware {{name: '{labware_name}'}})-[:HAS_PART]->(w:Well)-[:HAS_PROPERTY]->(p:Property)
            MATCH (l)-[:HAS_PART]->(o:Opentrons {{setup_id: '{opentrons_id}'}})
            RETURN l.name, w.well_id, p.value, p.unit'''
        res, _ = db.cypher_query(query, {})

        return res


class ExperimentManager:
    """
    A class to manage experiments it gets a workflow and setups. Stores the experiment_id with a timestamp and a status in a csv file in the experiment directory.
    the csv file has the following columns:
    experiment_id, timestamp, status

    for each experiment it creates a directory with the experiment_id and stores the setups and the workflow in the folder.
    """

    def __init__(self, opentrons: Union[str, dict], arduino: Union[str, dict], biologic: Union[str, dict],
                 opentrons_setup: Union[str, dict], chemicals: Union[str, dict], arduino_relays: Union[str, dict], offset_config: Union[str, dict],
                 logger):
        self.jobs = Job.objects.all()
        self.opentrons = opentrons if isinstance(opentrons, dict) else self.get_json_by_filename(opentrons)
        self.arduino = arduino if isinstance(arduino, dict) else self.get_json_by_filename(arduino)
        self.biologic = biologic if isinstance(biologic, dict) else self.get_json_by_filename(biologic)
        self.opentrons_setup = opentrons_setup if isinstance(opentrons_setup, dict) else self.get_json_by_filename(
            opentrons_setup)
        self.arduino_setup = arduino_relays if isinstance(arduino_relays, dict) else self.get_json_by_filename(
            arduino_relays)
        self.chemicals = Chemicals.from_config(chemicals) if isinstance(chemicals, dict) else Chemicals.from_config(
            self.get_json_by_filename(chemicals))
        self.chemical_config = chemicals if isinstance(chemicals, dict) else self.get_json_by_filename(chemicals)
        self.offset_config = offset_config if isinstance(offset_config, dict) else self.get_json_by_filename(offset_config)
        self.logger = logger
        self.runnable_experiments = []

    def find_setup_by_namespace(self, setups, namespace):
        for setup in setups:
            if setup.name_space == namespace:
                return setup
        return None

    def find_executable_experiments(self):
        self.setup = SetupModel.from_config(
            chemicals=self.chemicals,
            opentrons_setup=self.opentrons_setup,
            arduino_setup=self.arduino_setup,
            biologic=self.biologic,
            opentrons=self.opentrons,
            arduino=self.arduino
        )

        queued_jobs = Job.objects.filter(
            status="queued",
        )
        for job in queued_jobs:
            if self.check_requirements(job):
                self.runnable_experiments.append(job)
                print("Executeable Job", job.id)
            else:
                print("Not executable Job", job.id)
        print("Runnable Experiments", self.runnable_experiments)

    def check_requirements(self, job):
        chemical_check =  self.check_chemicals(job)
        setup_check = self.check_required_setup(job)
        return chemical_check and setup_check

    def check_chemicals(self, job):
        """
        Check if the required chemicals are present. Does a direct comparison of
        open
        """
        for chemical in job.chemicals['chemicals']:
            chemical = Chemical(**chemical)
            if not self.chemicals.check_chemical(chemical):
                return False
        return True


    def check_required_setup(self, job):
        """
        Check if the required setups are present. Does a direct comparison of the follwing:
        -opentrons
        -opentrons_setup
        -biologic
        -arduino
        -arduino_relays
        The comparison is done as a simple string comparison.
        """
        if job.opentrons != self.setup.opentrons:
            self.logger.info("Opentrons setup not matching")
            return False
        if job.opentrons_setup != self.setup.opentrons_setup:
            self.logger.info("Opentrons labware setup not matching")
            return False
        if job.biologic != self.setup.biologic:
            self.logger.info("Biologic setup not matching")
            return False
        if job.arduino != self.setup.arduino:
            self.logger.info("Arduino setup not matching")
            return False
        if job.arduino_setup != self.setup.arduino_setup:
            self.logger.info("Arduino relays not matching")
            return False
        return True


    def run_experiments(self):
        for runnable_experiment in self.runnable_experiments:
            experiment = Experiment(
                opentrons_config=self.opentrons,
                arduino_config=self.arduino,
                relay_config=self.arduino_setup,
                biologic_config=self.biologic,
                labware_config=self.opentrons_setup,
                chemicals_config=self.chemical_config,
                workflow=runnable_experiment.workflow,
                experiment_id=runnable_experiment.id,
                offset_config=self.offset_config
            )
            experiment.initialize_setups()
            experiment.store_setups()
            experiment.execute()
            self.logger.info(f"Experiment {experiment.experiment_id} executed successfully.")
            self.update_job_status(experiment.experiment_id, "completed")


    def update_job_status(self, experiment_id, status):
        # Check if the status is valid
        valid_statuses = dict(Job.STATUS_CHOICES).keys()
        if status not in valid_statuses:
            raise ValidationError(f"Invalid status: {status}. Must be one of {valid_statuses}")

        try:
            # Use get() for direct retrieval
            experiment = Job.objects.get(id=experiment_id)
        except Job.DoesNotExist:
            return f"Job with id {experiment_id} does not exist."

        # Update and save the status
        experiment.status = status
        experiment.save()

        return f"Job {experiment_id} status updated to {status}"



    @staticmethod
    def get_json_by_filename(name):
        directory = os.path.join(BASE_DIR, 'sdl', 'config')

        # Walk through the directory and subdirectories to find the file
        for root, dirs, files in os.walk(directory):
            if name in files:
                file_path = os.path.join(root, name)
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read().strip()
                        print(content)
                        if not content:
                            raise ValueError(f"The file {file_path} is empty.")
                        return json.loads(content)
                except PermissionError:
                    raise PermissionError(f"Permission denied when trying to access the file: {file_path}")
                except json.JSONDecodeError as e:
                    raise ValueError(f"Failed to decode JSON from file: {file_path}. Error: {str(e)}")
                except FileNotFoundError:
                    raise FileNotFoundError(f"File {name} not found in config directory or its subdirectories: {directory}")
