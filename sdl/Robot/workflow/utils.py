import importlib
import json
import pkgutil
from typing import Dict, Optional

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
    def __init__(self, operations: list = None):
        self.operations = operations if operations is not None else []
        self.responses = []
        self.requests = []

    def add_step(self, step):
        self.operations.append(step)

    def get_operations(self):
        return self.operations

    def execute(self, robot_ip, headers, run_id, additional_params, offline=False, logger = None, LOGGER=None):
        for operation in self.operations:
            print(operation)
            operation.execute(robot_ip, headers, run_id, logger, additional_params, offline)
            # response = output['response']
            # request = output['request']
            # self.responses = [*self.responses, *response]
            # self.requests = [*self.requests, *request]
        return {"response": self.responses, "request": self.requests}


class BaseStep:
    def execute(self):
        raise NotImplementedError("Each step must implement an execute method")


class BaseProcedure(BaseModel):
    pass