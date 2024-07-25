from typing import Union, List, Callable, Optional, Dict

from sdl.Robot.workflow.utils import BaseProcedure, BaseStep, BaseWorkflow


class SingleStep(BaseStep):
    def __init__(self, action: Union[str, dict, BaseProcedure, Callable]):
        if isinstance(action, BaseProcedure):
            self.parameters = action.dict()
            self.action = action.executable

    def execute(self):
        self.action(self.parameters)
        return self.parameters




class ParallelStep(BaseStep):
    def __init__(self, steps: List[BaseStep]):
        self.steps = steps

    def execute(self):
        # Example: using threading or multiprocessing for parallel execution
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor() as executor:
            executor.map(lambda step: step.execute(), self.steps)

class ConditionalStep(BaseStep):
    def __init__(self, condition: Callable[[], bool], true_step: BaseStep, false_step: Optional[BaseStep] = None):
        self.condition = condition
        self.true_step = true_step
        self.false_step = false_step

    def execute(self):
        if self.condition():
            self.true_step.execute()
        elif self.false_step:
            self.false_step.execute()

class LoopStep(BaseStep):
    def __init__(self, action: Union[BaseStep, BaseProcedure, BaseWorkflow], condition: Callable[['LoopStep'], bool], limit : Union[float, int], step_size = 1, counter: Union[float, int] = 0):
        self.action = action
        self.condition = condition
        self.step_size = step_size
        self.counter = counter
        self.limit = limit
        self.requests = []
        self.responses  = []


    def execute(self, robot_ip, headers, run_id, logger, additional_params, offline = True):
        print(f"Counter: {self.counter}", self.limit, self.condition(self), self.counter > self.limit)
        while self.condition(self):
            output = self.action.execute(robot_ip, headers, run_id, logger, additional_params, offline)
            response = output['response']
            request = output['request']
            self.responses.append(response)
            self.requests.append(request)
            self.counter = self.counter + self.step_size
        return {"response": self.responses, "request": self.requests}




class ProcessingStep(BaseStep):
    def __init__(self, command_function: Callable, params: Dict):
        self.command_function = command_function
        self.params = params

    def execute(self):
        self.command_function(**self.params)