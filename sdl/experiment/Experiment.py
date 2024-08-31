import json
import logging
import os
import uuid
from typing import Union, List

from django.db.models import Q
from pydantic import BaseModel

from mat2devplatform.settings import BASE_DIR
from sdl.models import ExperimentModel
from sdl.setup.arduino_setup.ArduinoSetup import ArduinoSetup
from sdl.setup.biologic_setup.BiologicSetup import BiologicSetup
from sdl.setup.opentrons_setup.OpentronsSetup import OpentronsSetup
from sdl.workflow.utils import BaseWorkflow, BaseProcedure, BaseStep, Requirements





class Experiment:
    def __init__(self, setups, workflow: Union[BaseWorkflow, List[Union[BaseWorkflow, BaseProcedure, BaseStep]]],
                 experiment_id = None, store_experiment = True):
        """
        Initialize an experiment with a list of setups and a workflow.

        Args:
            setups (list): A list of setup instances.
            workflow (Workflow): An instance of a workflow.
        """
        self.experiment_id = uuid.uuid4() if experiment_id is None else experiment_id
        self.create_experiment_directory()
        self.logger = self.initialize_logger()
        self.setups = {setup.name_space: setup for setup in setups}  # Using a dictionary for easy access by name
        self.workflow = workflow

        self.outputs = []
        self.experiment_id = uuid.uuid4() if experiment_id is None else experiment_id


        if store_experiment:
            self.store_experiment()


    def store_experiment(self):

        required_fields = {
            'id': self.experiment_id,
            'opentrons': self.setups['opentrons'].config,
            'labware': self.setups['opentrons'].labware_config,
            'chemicals': self.setups['opentrons'].chemicals_config,
            'workflow': {"name": "TestWorkflow", "variables": {"test": "test"}}
        }

        # Use dictionary comprehension to conditionally add optional fields
        optional_fields = {key: self.setups[key].config for key in ['biologic', 'arduino'] if key in self.setups}

        if 'arduino' in optional_fields:
            optional_fields['arduino_relays'] = self.setups['arduino'].relay_config

        # Merge required fields and optional fields
        model_data = {**required_fields, **optional_fields}

        # Create the ExperimentModel instance
        self.model = ExperimentModel(**model_data)
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

    @classmethod
    def from_model(cls, model, logger):
        setups = []
        if model.opentrons:
            opentrons = OpentronsSetup(robot_config_source=model.opentrons,
                                       labware_config_source=model.labware,
                                       chemicals_config_source=model.chemicals,
                                       ip=model.opentrons['ip'],
                                       port=model.opentrons['port'],
                                       logger=logger)
            setups.append(opentrons)
        if model.arduino:
            arduino = ArduinoSetup(config=model.arduino, relay_config=model.arduino_relays, logger=logger)
            setups.append(arduino)
        if model.biologic:
            biologic = BiologicSetup(config_source=model.biologic, logger=logger)
            setups.append(biologic)
        workflow = BaseWorkflow.from_config(model.workflow)
        return cls(setups = setups, workflow=workflow, experiment_id= model.id, store_experiment=False)

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
            output = self.workflow.execute(logger=self.logger, **self.configs)
            if not isinstance(output, list):
                output = [output]
            self.outputs = [*self.outputs, *output]


class ExperimentManager:
    """
    A class to manage experiments it gets a workflow and setups. Stores the experiment_id with a timestamp and a status in a csv file in the experiment directory.
    the csv file has the following columns:
    experiment_id, timestamp, status

    for each experiment it creates a directory with the experiment_id and stores the setups and the workflow in the folder.
    """

    def __init__(self, setups, logger):
        self.experiments = ExperimentModel.objects.filter(status="queued")
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

    def find_setup_by_namespace(self, setups, namespace):
        for setup in setups:
            if setup.name_space == namespace:
                return setup
        return None


    def find_executable_experiments(self):
        runnable_experiments = ExperimentModel.objects.filter(
            status="queued"
        ).filter(
            Q(opentrons__isnull=True) | Q(opentrons=self.opentrons_config),
            Q(labware__isnull=True) | Q(labware=self.labware_setup),
            Q(chemicals__isnull=True) | Q(chemicals=self.chemicals_setup),
            Q(arduino__isnull=True) | Q(arduino=self.relays_setup),
            Q(biologic__isnull=True) | Q(biologic=self.biologic_setup)
        )
        for i in runnable_experiments:
            print(i)
            try:
                self.runnable_experiments.append(Experiment.from_model(i, self.logger))
            except KeyError as e:
                print(e)
                self.logger.error(f"Error creating experiment: {e}")
                continue
        print("Runnable Experiments",
              self.runnable_experiments[0].workflow.get_procedures(),
              self.runnable_experiments[0].workflow.get_requirements()
              )
            self.check_executability(i)

        # self.runnable_experiments[0].initialize_setups()
        # self.runnable_experiments[0].store_setups()
        # self.runnable_experiments[0].execute()






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
