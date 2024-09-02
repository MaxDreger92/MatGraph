import importlib
import json
import pkgutil
from typing import Dict, Optional, Union, TypeVar, Generic, Any

from pydantic import BaseModel
from sqlalchemy.testing.requirements import Requirements



class WellLocation(BaseModel):
    wellName: str

class SlotLocation(BaseModel):
    slotName: str

class Location(BaseModel):
    wellLocation: WellLocation
    slotLocation: SlotLocation

class BaseProcedure(BaseModel):
    pass

class Chemical(BaseModel):
    name: str
    volume: float
    unit: str
    location: Optional[Location] = None

class Labware(BaseModel):
    name_space: str
    name: str
    location: Optional[Location] = None

class Requirements(BaseModel):
    chemicals : list[Chemical]
    labware : list[Labware]


class Registry:
    package = None
    _registry = {}

    @classmethod
    def initialize(cls, package='sdl'):
        cls.package = package
        cls._discover_workflows()

    @classmethod
    def _discover_workflows(cls):
        def walk_packages(package_name):
            package = importlib.import_module(package_name)
            for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
                full_module_name = f"{package_name}.{module_name}"
                yield full_module_name
                if is_pkg:
                    yield from walk_packages(full_module_name)

        for module_name in cls.walk_packages(cls.package):
            module = importlib.import_module(module_name)
            for attr in dir(module):
                obj = getattr(module, attr)
                if isinstance(obj, type) and issubclass(obj, BaseWorkflow) and obj is not BaseWorkflow:
                    cls._registry[attr] = obj

    @classmethod
    def walk_packages(cls, package_name):
        package = importlib.import_module(package_name)
        for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
            full_module_name = f"{package_name}.{module_name}"
            yield full_module_name
            if is_pkg:
                yield from cls.walk_packages(full_module_name)

    @classmethod
    def get_procedure(cls, name):
        if name not in cls._registry:
            raise KeyError(f"No procedure found with the name '{name}'.")
        return cls._registry[name]

    @classmethod
    def list_procedures(cls):
        cls.initialize()
        return list(cls._registry.values())


class BaseWorkflow(Registry):
    def __init__(self, operations: list[Union['BaseWorkflow', BaseProcedure]] = None):
        self.operations = operations if operations is not None else []
        self.requirements = None
        self.outputs = []
        self.procedures = self.get_procedures()

    def json(self):

        return json.dumps({
            'name': self.__class__.__name__,
            'variables': {},
            'requirements': self.get_requirements().dict(),
        })

    @classmethod
    def get_all_subclasses(cls):
        """
        Get all subclasses of the current class as well as their subclasses.
        :return: list of subclasses
        """
        all_subclasses = cls.list_procedures()  # Start with direct subclasses
        return all_subclasses

    @classmethod
    def from_config(cls, config: Dict[str, Any]):
        """
        Create a workflow from a configuration dictionary.
        :param config:
        :return: workflow instance
        """
        print(config)
        workflow_name = config['name']
        workflow_variables = config.get('variables', {})
        workflow = cls.get_workflow(workflow_name)(**workflow_variables)
        print("Workflow", workflow)
        return workflow

    @classmethod
    def get_workflow(cls, name):
        """
        Get a workflow by name, using the __subclasses__ method.
        :param name:
        :return: workflow class
        """
        for subclass in cls.get_all_subclasses():
            print(subclass)
            if subclass.__name__ == name:
                return subclass
        raise KeyError(f"No workflow found with the name '{name}'.")

    def get_procedures(self):
        procedures = []
        for operation in self.operations:
            if isinstance(operation, BaseProcedure):
                procedures.append(operation)
            elif hasattr(operation, 'get_procedures') and callable(operation.get_procedures):
                procedures.extend(operation.get_procedures())
        return procedures

    def get_requirements(self):
        if self.requirements is not None:
            return self.requirements
        else:
            # Initialize an empty Requirements object to accumulate results
            accumulated_requirements = Requirements(chemicals=[], labware=[])

            # Iterate through each operation
            for operation in self.operations:
                print(operation)
                # Check if the operation has its own requirements
                if hasattr(operation, 'get_requirements') and callable(operation.get_requirements):
                    # Recursively get the requirements from the operation
                    sub_requirements = operation.get_requirements()

                    # Accumulate the chemicals and labware from the operation
                    accumulated_requirements.chemicals.extend(sub_requirements.chemicals)
                    accumulated_requirements.labware.extend(sub_requirements.labware)

            # Return the accumulated requirements
            return accumulated_requirements

    def add_step(self, step):
        self.operations.append(step)

    def get_operations(self):
        return self.operations

    def execute(self, *args, **kwargs):
        for operation in self.operations:
            print("OPERATION", operation)
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
