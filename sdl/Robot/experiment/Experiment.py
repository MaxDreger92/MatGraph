from typing import Union, List

from neomodel import db

from sdl.Robot.workflow.ProcessingStep import LoopStep
from sdl.Robot.workflow.utils import BaseWorkflow, BaseProcedure, BaseStep


class Experiment:
    def __init__(self, setups, workflow: Union[BaseWorkflow, List[Union[BaseWorkflow, BaseProcedure, BaseStep]]], logger):
        """
        Initialize an experiment with a list of setups and a workflow.

        Args:
            setups (list): A list of setup instances.
            workflow (Workflow): An instance of a workflow.
        """
        print(setups)
        self.setups = {setup.name_space: setup for setup in setups}  # Using a dictionary for easy access by name
        self.workflow = workflow
        self.logger = logger
        self.outputs = []

    def update_setups(self, setup):
        self.setups[setup.name_space] = setup


    @property
    def configs(self):
        return {setup.name_space: setup.info for setup in self.setups.values()}

    def initialize_setups(self):
        """Initialize all setups."""
        for name, setup in self.setups.items():
            self.logger.info(f"Initializing setup '{name}'")
            setup.setup()
            self.update_setups(setup)

    def store_setups(self):
        """Store all setups."""
        for name, setup in self.setups.items():
            self.logger.info(f"Storing setup '{name}'")
            print("OPENTRONS ID: ", self.setups['opentrons'].setup_id)
            setup.save_graph(opentrons_id= self.setups['opentrons'].setup_id)



    def execute(self, workflow=None, *args, **kwargs):
        print("Executing workflow")
        print(type(self.workflow))
        print("LOGGER: ", self.logger)


    # Check if the workflow is a list
        if isinstance(self.workflow, list):
            for sub_workflow in self.workflow:
                print("CONFIGS: ", self.configs)
                configs = {k: v for config in self.configs.values() for k, v in config.items()}
                output = sub_workflow.execute(**configs,
                                     logger = self.logger)
                self.outputs = [*self.outputs, *output]
        else:
            output = self.workflow.execute(logger=self.logger, **self.configs)
            if not isinstance(output, list):
                output = [output]
            self.outputs = [*self.outputs, *output]

        match_query = []
        names = []
        connect_query = []





# Example usage: