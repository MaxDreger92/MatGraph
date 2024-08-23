from typing import Union, List, Callable, Optional, Dict

from sdl.workflow.utils import BaseStep, BaseProcedure, BaseWorkflow


class SingleStep(BaseStep):
    def __init__(self, action: Union[str, dict, BaseProcedure, Callable]):
        if isinstance(action, BaseProcedure):
            self.parameters = action.dict()
            self.action = action.executable

    def execute(self):
        self.action(self.parameters)
        return self.parameters


class AddPythonCode(BaseStep):
    def __init__(self, func, **kwargs):
        self.func = func
        self.kwargs = kwargs

    def execute(self, **context_kwargs):
        # Merge context_kwargs with self.kwargs, giving priority to context_kwargs
        combined_kwargs = {**self.kwargs, **context_kwargs}
        return self.func(**combined_kwargs)



class ParallelStep(BaseStep):
    def __init__(self, steps: List[BaseStep]):
        self.steps = steps

    def execute(self):
        # Example: using threading or multiprocessing for parallel execution
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor() as executor:
            executor.map(lambda step: step.execute(), self.steps)

class ConditionalStep:
    def __init__(self, operation1, operation2_creator, update_operation2_func=None):
        self.operation1 = operation1
        self.operation2_creator = operation2_creator
        self.update_operation2_func = update_operation2_func
        self.operation2 = None

    def execute(self):
        # Execute the first operation
        self.operation1.execute()

        # Create the second operation using the data from the first operation
        self.operation2 = self.operation2_creator(self.operation1.get_result())

        # Optionally update parts of the second operation
        if self.update_operation2_func:
            self.update_operation2_func(self.operation2, self.operation1.get_result())

        # Execute the second operation
        self.operation2.execute()

class LoopStep(BaseStep):
    def __init__(self, operations: Union[BaseStep, BaseProcedure, BaseWorkflow], condition: Callable[['LoopStep'], bool], limit : Union[float, int], step_size = 1, counter: Union[float, int] = 0, update_counter_callback = None):
        self.operations = [operations]
        self.condition = condition
        self.step_size = step_size
        self.counter = counter
        self.limit = limit
        self.requests = []
        self.responses  = []


    def execute(self, robot_ip, headers, run_id, logger, additional_params = {}, offline = True):
        while self.condition(self):
            if isinstance(self.operations, list):
                for operation in self.operations:
                    output = operation.execute(robot_ip, headers, run_id, logger, additional_params, offline)
                    response = output['response']
                    request = output['request']
                    self.responses.append(response)
                    self.requests.append(request)
                self.counter = self.counter + self.step_size
            else:
                output = self.operations.execute(robot_ip, headers, run_id, logger, additional_params, offline)
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