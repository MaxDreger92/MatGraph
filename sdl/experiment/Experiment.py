import os
import uuid
from typing import Union, List

from django.db.models import Q

from mat2devplatform.settings import BASE_DIR
from sdl.models import ExperimentModel
from sdl.workflow.utils import BaseWorkflow, BaseProcedure, BaseStep


class Experiment:
    def __init__(self, setups, workflow: Union[BaseWorkflow, List[Union[BaseWorkflow, BaseProcedure, BaseStep]]],
                 logger, experiment_id = None):
        """
        Initialize an experiment with a list of setups and a workflow.

        Args:
            setups (list): A list of setup instances.
            workflow (Workflow): An instance of a workflow.
        """
        self.setups = {setup.name_space: setup for setup in setups}  # Using a dictionary for easy access by name
        self.workflow = workflow
        self.logger = logger
        self.outputs = []
        self.experiment_id = uuid.uuid4() if experiment_id is None else experiment_id
        self.create_experiment_directory()
        required_fields = {
            'id': self.experiment_id,
            'opentrons': self.setups['opentrons'].config,
            'labware': self.setups['opentrons'].labware_config,
            'chemicals': self.setups['opentrons'].chemicals_config,
            'workflow': {"test": "test"}
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

    def create_experiment_directory(self):
        # Construct the directory path
        experiment_dir = os.path.join(BASE_DIR, str(self.experiment_id))

        # Create the directory if it doesn't exist
        os.makedirs(experiment_dir, exist_ok=True)

        # Log or print a message that the directory has been created
        self.logger.info(f"Experiment directory created: {experiment_dir}")


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
