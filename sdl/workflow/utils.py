import importlib
import json
import pkgutil
from typing import Dict, Optional, Union, TypeVar, Generic

from pydantic import BaseModel

class BaseProcedure(BaseModel):
    pass

class Registry:
    def __init__(self, package):
        self.package = package
        self._registry = {}
        self._discover_procedures()

    def _discover_procedures(self):
        def walk_packages(package_name):
            package = importlib.import_module(package_name)
            for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
                full_module_name = f"{package_name}.{module_name}"
                yield full_module_name
                if is_pkg:
                    yield from walk_packages(full_module_name)

        for module_name in walk_packages(self.package):
            module = importlib.import_module(module_name)
            for attr in dir(module):
                obj = getattr(module, attr)
                if isinstance(obj, type) and issubclass(obj, BaseProcedure) and obj is not BaseProcedure:
                    self._registry[attr] = obj

    def get_procedure(self, name):
        if name not in self._registry:
            raise KeyError(f"No procedure found with the name '{name}'.")
        return self._registry[name]

    def list_procedures(self):
        return list(self._registry.keys())

class BaseWorkflow(Registry):
    def __init__(self, operations: list[Union['BaseWorkflow', BaseProcedure]] = None):
        self.operations = operations if operations is not None else []
        self.outputs = []

    def add_step(self, step):
        self.operations.append(step)

    def get_operations(self):
        return self.operations

    def execute(self, *args, **kwargs):
        for operation in self.operations:
            print(operation)
            output = operation.execute(*args, **kwargs)
            self.outputs.append(output)
            # response = output['response']
            # request = output['request']
            # self.responses = [*self.responses, *response]
            # self.requests = [*self.requests, *request]
        return self.outputs

    def to_graph(self):
        previous_step = None
        print(self.operations)
        for operation in self.operations:
            if previous_step:
                previous_step.followed_by.connect(operation)
            step = operation.to_graph()
            previous_step = step


class BaseStep:
    def execute(self):
        raise NotImplementedError("Each step must implement an execute method")

P = TypeVar('P', bound=BaseModel)


class BaseProcedure(Generic[P]):
    def __init__(self, params: P):
        self.params = params
    pass