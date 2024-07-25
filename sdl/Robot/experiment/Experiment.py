from typing import Union, List

from sdl.Robot.workflow.utils import BaseWorkflow, BaseProcedure


class Experiment:
    def __init__(self, setups, workflow: Union[BaseWorkflow, List[Union[BaseWorkflow, BaseProcedure]]]):
        """
        Initialize an experiment with a list of setups and a workflow.

        Args:
            setups (list): A list of setup instances.
            workflow (Workflow): An instance of a workflow.
        """
        self.setups = {setup.name_space: setup for setup in setups}  # Using a dictionary for easy access by name
        self.workflow = workflow

    def initialize_setups(self):
        """Initialize all setups."""
        for name, setup in self.setups.items():
            print(f"Initializing setup '{name}'")
            print(setup)
            setup.setup()

    def execute(self):
        """Execute the experiment workflow."""
        if not self.workflow:
            raise RuntimeError("No workflow set for the experiment.")

        if isinstance(self.workflow, BaseWorkflow):
            self.workflow.execute()
        elif isinstance(self.workflow, list):
            for workflow in self.workflow:
                if isinstance(workflow, BaseWorkflow) or isinstance(workflow, BaseProcedure):
                    workflow.execute(robot_ip=self.setups['opentrons'].robot_ip, headers=self.setups['opentrons'].headers, run_id=self.setups['opentrons'].runID, LOGGER=None, additional_params=None)
                else:
                    raise ValueError(f"Invalid workflow type: {type(workflow)}")
        # for step in self.workflow.operations:
        #     setup_name = step.setup_name
        #     if setup_name in self.setups:
        #         self.setups[setup_name].execute_step(step)
        #     else:
        #         raise ValueError(f"Setup '{setup_name}' not found for step '{step}'.")

# Example usage: