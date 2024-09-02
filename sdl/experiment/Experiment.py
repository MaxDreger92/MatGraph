import json
import logging
import os
import uuid
from typing import Union, List

from django.db.models import Q
from neomodel import db
from pydantic import BaseModel

from mat2devplatform.settings import BASE_DIR
from sdl.models import Job
from sdl.setup.arduino_setup.ArduinoSetup import ArduinoSetup
from sdl.setup.biologic_setup.BiologicSetup import BiologicSetup
from sdl.setup.opentrons_setup.OpentronsSetup import OpentronsSetup
from sdl.workflow.utils import BaseWorkflow, BaseProcedure, BaseStep, Requirements



class JobRequest:
    def __init__(self, job_request: json, job_uid: Union[str, uuid] = None):
        self.job_request = job_request
        self.workflow = BaseWorkflow.from_config(job_request)
        self.requirements = self.workflow.get_requirements()
        self.job_uid = job_uid if job_uid else uuid.uuid4()
        self.queue_job()

    def get_workflow(self):
        return self.workflow

    def queue_job(self):
        model_data = {
            'id': self.job_uid,
            'requirements': self.requirements.json(),
            'workflow': self.job_request
        }
        # Create the ExperimentModel instance
        self.model = Job(**model_data)
        self.model.save()






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
                    store_experiment: bool = True
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
        self.setups = self.create_setups(opentrons_config,labware_config, chemicals_config, arduino_config, relay_config, biologic_config)  # Using a dictionary for easy access by name
        self.workflow = self.create_workflow(workflow)
        self.outputs = []
        self.experiment_id = uuid.uuid4() if experiment_id is None else experiment_id


        # if store_experiment:
        #     self.store_experiment()


    def create_workflow(self, workflow):
        if workflow:
            return BaseWorkflow.from_config(workflow)
        raise KeyError("No workflow provided.")


    def create_setups(self, opentrons_config, labware_config, chemicals_config, arduino_config, relay_config, biologic_config):
        setups = {}
        if opentrons_config:
            opentrons = OpentronsSetup(robot_config_source=opentrons_config,
                                       labware_config_source=labware_config,
                                       chemicals_config_source=chemicals_config,
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
                                              experiment_id = self.experiment_id,
                                              opentrons_setup = self.setups['opentrons'])
                self.outputs = [*self.outputs, *output]
        else:
            output = self.workflow.execute(logger=self.logger, **self.configs, opentrons_setup=self.setups['opentrons'])
            if not isinstance(output, list):
                output = [output]
            self.outputs = [*self.outputs, *output]


    def find_chemicals(self, chemical_name, opentrons_id):
        query = f'''
            MATCH (p:Property)<-[:HAS_PROPERTY]-(c:Matter {{name: '{chemical_name}'}})-[:IN|HAS_METADATA]->(m:Metadata)<-[:HAS_PART*..5]-(o:Opentrons {{setup_id: '{opentrons_id}'}})
            WHERE p.name = 'amount' OR p.name = 'Quantity'
            RETURN c.name, p.value, p.unit'''
        print(query)
        res, _ = db.cypher_query(query, {})
        print(res)

        return res


class ExperimentManager:
    """
    A class to manage experiments it gets a workflow and setups. Stores the experiment_id with a timestamp and a status in a csv file in the experiment directory.
    the csv file has the following columns:
    experiment_id, timestamp, status

    for each experiment it creates a directory with the experiment_id and stores the setups and the workflow in the folder.
    """

    def __init__(self, setups, logger):
        self.jobs = Job.objects.filter(status="queued")
        self.opentrons = self.find_setup_by_namespace(setups, "opentrons")
        self.arduino = self.find_setup_by_namespace(setups, "arduino")
        self.biologic = self.find_setup_by_namespace(setups, "biologic")
        self.opentrons_config = self.opentrons.config if self.opentrons else None
        self.labware_setup = self.opentrons.labware_config if self.opentrons else None
        self.arduino_config = self.arduino.config if self.arduino else None
        self.relays_setup = self.arduino.relay_config if self.arduino else None
        self.biologic_setup = self.biologic.config if self.biologic else None
        self.chemicals_setup = self.opentrons.chemicals_config if self.opentrons else None
        self.logger = logger
        self.setup = setups
        self.runnable_experiments = []
        self.experiment = None

    def find_setup_by_namespace(self, setups, namespace):
        for setup in setups:
            if setup.name_space == namespace:
                return setup
        return None


    def find_executable_experiments(self):
        self.initialize_setups()
        runnable_jobs = Job.objects.filter(
            status="queued"
        ).filter(
            Q(opentrons__isnull=True) | Q(opentrons=self.opentrons_config),
            Q(labware__isnull=True) | Q(labware=self.labware_setup),
            Q(chemicals__isnull=True) | Q(chemicals=self.chemicals_setup),
            Q(arduino__isnull=True) | Q(arduino=self.relays_setup),
            Q(biologic__isnull=True) | Q(biologic=self.biologic_setup)
        )
        for job in runnable_jobs:
            self.check_requirements(job)
            self.runnable_experiments.append(job)

    def initialize_setups(self):
        self.experiment = Experiment(
            opentrons_config=self.opentrons_config,
            labware_config=self.labware_setup,
            chemicals_config=self.chemicals_setup,
            arduino_config=self.arduino_config,
            relay_config=self.relays_setup,
            biologic_config=self.biologic_setup,
            workflow={
                "name": "TestWorkflow",
                "variables": {"test": "egal"}
            },
        )
        self.experiment.initialize_setups()
        self.experiment.store_setups()

    def check_requirements(self, job):
        print(job.requirements)
        req = job.requirements
        req = json.loads(req)  # Use json.loads instead of json.load
        requirements = Requirements(**req)
        for chemical in requirements.chemicals:
            id = self.experiment.setups['opentrons'].info['opentrons_id']
            print(self.experiment.find_chemicals(chemical.name, opentrons_id=id))
        print(job.requirements)
        print(self.experiment)






    def run_experiments(self):
        for experiment in self.experiments:
            experiment.initialize_setups()
            experiment.store_setups()
            experiment.execute()
            self.logger.info(f"Experiment {experiment.experiment_id} executed successfully.")
            self.update_experiment_status(experiment.experiment_id, "success")

    def update_experiment_status(self, experiment_id, status):
        pass

    def save_experiment_status(self):
        pass
