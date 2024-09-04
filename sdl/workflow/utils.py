import importlib
import json
import os
import pkgutil
from typing import Dict, Optional, Union, TypeVar, Generic, Any, List

from pydantic import BaseModel
from sqlalchemy.testing.requirements import Requirements
from pint import UnitRegistry

from mat2devplatform.settings import BASE_DIR


class WellLocation(BaseModel):
    wellName: str

class SlotLocation(BaseModel):
    slotName: str

class Location(BaseModel):
    wellLocation: WellLocation
    slotLocation: SlotLocation

class BaseProcedure(BaseModel):
    pass

ureg = UnitRegistry()


class Chemical(BaseModel):
    name: str
    volume: float
    unit: str
    location: Optional[Location] = None

    @classmethod
    def from_list(cls, data: list[Any]):
        return cls(name=data[0], volume=data[1], unit=data[2])

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(name=data['name'], volume=data['volume']['value'], unit=data['volume']['unit'])


    def compare_quantity(self, other: "Chemical") -> int:
        """Compares the quantity of this chemical with another.

        Returns:
            -1 if this chemical's quantity is less than the other
            0 if both quantities are equal
            1 if this chemical's quantity is greater than the other
        """
        self_quantity = self.get_quantity()
        other_quantity = other.get_quantity()

        if self_quantity < other_quantity:
            return -1
        elif self_quantity > other_quantity:
            return 1
        else:
            return 0

    def get_quantity(self):
        return self.volume * ureg(self.unit)

    def add_quantity(self, other: "Chemical"):
        """Adds the quantity of another chemical to this one."""
        if self.name != other.name:
            raise ValueError("Cannot add chemicals with different names")

        self_quantity = self.get_quantity()
        other_quantity = other.get_quantity()

        total_quantity = self_quantity + other_quantity

        self.volume = total_quantity.magnitude
        self.unit = str(total_quantity.units)


class Chemicals(BaseModel):
    chemicals: List[Chemical]

    @classmethod
    def from_config(cls, config: List[List[Any]]):
        # Assuming config is a list of lists, where each sublist represents a chemical
        chemical_dict = {}
        for key, value in config.items():
            for chemical in value:
                if not isinstance(value, list):
                    raise ValueError(f"Expected a list of chemicals, but got {value} instead")
                if chemical['name'] not in chemical_dict.keys():
                    chemical_dict[chemical['name']] = Chemical.from_dict(chemical)
                else:
                    chemical_dict[chemical['name']].add_quantity(Chemical.from_dict(chemical))
        chemicals = chemical_dict.values()
        return cls(chemicals=chemicals)

    def check_chemical(self, chemical: Chemical) -> bool:
        """
        Check if the list of chemicals  has the required chemical in the correct quantity.

        :return:
        """
        for available_chemical in self.chemicals:
            if available_chemical.name == chemical.name:
                comparison = available_chemical.compare_quantity(chemical)
                if comparison < 0:
                    return False
        return True

from typing import Union, List
from pydantic import BaseModel, root_validator

class RequirementModel(BaseModel):
    chemicals: Chemicals
    opentrons: Union[dict, str]
    opentrons_setup: Union[dict, str]
    arduino: Union[dict, str]
    arduino_setup: Union[dict, str]
    biologic: Union[dict, str]

    @root_validator(pre=True)
    def process_fields(cls, values):
        """
        This validator processes each field that can be a filename, dict, or list.
        If a filename is given, it loads the corresponding JSON and processes it.
        """
        fields_to_process = ['chemicals', 'opentrons', 'opentrons_setup', 'arduino', 'arduino_setup', 'biologic']

        for field in fields_to_process:
            field_value = values.get(field)
            if isinstance(field_value, str):
                json_data = cls.get_json_by_filename(field_value)
                if field == 'chemicals':
                    values['chemicals'] = Chemicals.from_config(json_data)
                else:
                    values[field] = json_data
            elif isinstance(field_value, dict) and field == 'chemicals':
                values['chemicals'] = Chemicals.from_config(field_value)

        return values


    @staticmethod
    def get_json_by_filename(name):
        directory = os.path.join(BASE_DIR, 'sdl', 'config')

        # Walk through the directory and subdirectories to find the file
        for root, dirs, files in os.walk(directory):
            if name in files:
                file_path = os.path.join(root, name)
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read().strip()
                        if not content:
                            raise ValueError(f"The file {file_path} is empty.")
                        return json.loads(content)
                except PermissionError:
                    raise PermissionError(f"Permission denied when trying to access the file: {file_path}")
                except json.JSONDecodeError as e:
                    raise ValueError(f"Failed to decode JSON from file: {file_path}. Error: {str(e)}")

        raise FileNotFoundError(f"File {name} not found in config directory or its subdirectories: {directory}")




class SetupModel(RequirementModel):

    @classmethod
    def from_config(cls, chemicals, arduino, opentrons, opentrons_setup, arduino_setup, biologic):
        return cls(
            chemicals=chemicals,
            arduino=arduino,
            opentrons=opentrons,
            opentrons_setup=opentrons_setup,
            arduino_setup=arduino_setup,
            biologic=biologic
        )




    def check_requirements(self, requirements: Requirements) -> bool:
        """Checks if the available setup meets the requirements.

        Args:
            requirements: The requirements to check against.

        Returns:
            True if the available setup meets the requirements, False otherwise.
        """
        return self.check_chemicals(requirements.chemicals) and self.check_labware(requirements)

    def check_chemicals(self, chemicals: list[Chemical]) -> bool:
        """Checks if the available setup has the required chemicals. When a required chemical is available it compares the
        quantity of the available chemical with the required one.

        Args:
            chemicals: The required chemicals.

        Returns:
            True if the available setup has the required chemicals, False otherwise.
        """
        for required_chemical in chemicals:
            found = False
            for available_chemical in self.chemicals:
                if available_chemical.name == required_chemical.name:
                    found = True
                    comparison = available_chemical.compare_quantity(required_chemical)
                    if comparison < 0:
                        return False
                    break
            if not found:
                return False

    def check_setup(self, requirement: Requirements) -> bool:
        """Checks if the available setup has the required labware. checks sequentially and prints results.

        Args:
            requirements: Requirements instance.

        Returns:
            True if the configs are the same.
        """
        if requirement.opentrons != self.opentrons:
            print(f"Opentrons config does not match. Expected: {requirement.opentrons}, Found: {self.opentrons}")
            return False
        if requirement.labware != self.labware:
            print(f"Labware config does not match. Expected: {requirement.labware}, Found: {self.labware}")
            return False
        if requirement.arduino != self.arduino:
            print(f"Arduino config does not match. Expected: {requirement.arduino}, Found: {self.arduino}")
            return False
        if requirement.biologic != self.biologic:
            print(f"Biologic config does not match. Expected: {requirement.biologic}, Found: {self.biologic}")
            return False
        if requirement.relays != self.relays:
            print(f"Relays config does not match. Expected: {requirement.relays}, Found: {self.relays}")
            return False
        return True





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
        workflow_name = config['name']
        workflow_variables = config.get('variables', {})
        workflow = cls.get_workflow(workflow_name)(**workflow_variables)
        return workflow

    @classmethod
    def get_workflow(cls, name):
        """
        Get a workflow by name, using the __subclasses__ method.
        :param name:
        :return: workflow class
        """
        for subclass in cls.get_all_subclasses():
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
            accumulated_requirements = RequirementModel(chemicals=[], opentrons_setup={}, opentrons={}, arduino={}, biologic={}, arduino_setup={})

            # Iterate through each operation
            for operation in self.operations:
                # Check if the operation has its own requirements
                if hasattr(operation, 'get_requirements') and callable(operation.get_requirements):
                    # Recursively get the requirements from the operation
                    sub_requirements = operation.get_requirements()

                    # Accumulate the chemicals and labware from the operation
                    accumulated_requirements.chemicals.extend(sub_requirements.chemicals)
                    if sub_requirements.opentrons:
                        accumulated_requirements.opentrons = sub_requirements.opentrons
                    if sub_requirements.arduino:
                        accumulated_requirements.arduino = sub_requirements.arduino
                    if sub_requirements.biologic:
                        accumulated_requirements.biologic = sub_requirements.biologic
                    if sub_requirements.arduino_setup:
                        accumulated_requirements.arduino_setup = sub_requirements.arduino_setup
                    if sub_requirements.opentrons_setup:
                        accumulated_requirements.opentrons_setup = sub_requirements.opentrons_setup

            # Return the accumulated requirements
            return accumulated_requirements

    def add_step(self, step):
        self.operations.append(step)

    def get_operations(self):
        return self.operations

    def execute(self, *args, **kwargs):
        for operation in self.operations:
            output = operation.execute(*args, **kwargs)
            self.outputs.append(output)
            # response = output['response']
            # request = output['request']
            # self.responses = [*self.responses, *response]
            # self.requests = [*self.requests, *request]
        return self.outputs

    def to_graph(self):
        previous_step = None
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
