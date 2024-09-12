import importlib
import json
import logging
import os
import pkgutil
from typing import Dict, Optional, TypeVar, Generic, Any, List

from openai import models
from pint import UnitRegistry
from pydantic import BaseModel, model_validator

from mat2devplatform.settings import BASE_DIR
from sdl.models import WorkflowModel


class WellLocation(BaseModel):
    """
    Represents the location of a well.

    Attributes:
        wellName (str): The name of the well.
    """
    wellName: str

class SlotLocation(BaseModel):
    """
    Represents the location of a slot.

    Attributes:
        slotName (str): The name of the slot.
    """
    slotName: str

class Location(BaseModel):
    """
    Represents the location of a well and a slot.

    Attributes:
        wellLocation (WellLocation): The location of the well.
        slotLocation (SlotLocation): The location of the slot.
    """
    wellLocation: WellLocation
    slotLocation: SlotLocation



ureg = UnitRegistry()


class Chemical(BaseModel):
    """
    Represents a chemical with its name, volume, unit, and location.

    Attributes:
        name (str): The name of the chemical.
        volume (float): The volume of the chemical.
        unit (str): The unit of the volume.
        location (Optional[Location]): The location of the chemical.
    """
    name: str
    volume: float
    unit: str
    location: Optional[Location] = None

    @classmethod
    def from_list(cls, data: list[Any]):
        """
        Creates a Chemical instance from a list.

        Args:
            data (list[Any]): A list containing the name, volume, and unit of the chemical.

        Returns:
            Chemical: A Chemical instance.
        """
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
        """
        Gets the quantity of the chemical.

        Returns:
            Quantity: The quantity of the chemical.
        """
        quantity = self.volume * ureg(self.unit)
        return quantity

    def add_quantity(self, other: "Chemical"):
        """
        Adds the quantity of another chemical to this one.

        Args:
            other (Chemical): The other chemical to add.
        """
        if self.name != other.name:
            raise ValueError("Cannot add chemicals with different names")

        self_quantity = self.get_quantity()
        other_quantity = other.get_quantity()

        total_quantity = self_quantity + other_quantity

        self.volume = total_quantity.magnitude
        self.unit = str(total_quantity.units)


class Chemicals(BaseModel):
    """
    Represents a list of chemicals.

    Attributes:
        chemicals (List[Chemical]): The list of chemicals.
    """
    chemicals: List[Chemical]

    @classmethod
    def from_config(cls, config: Dict):
        """
        Creates a Chemicals instance from a configuration.

        Args:
            config (List[List[Any]]): A list of lists, where each sublist represents a chemical.

        Returns:
            Chemicals: A Chemicals instance.
        """
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
        Checks if the list of chemicals has the required chemical in the correct quantity.

        Args:
            chemical (Chemical): The chemical to check.

        Returns:
            bool: True if the required chemical is present in the correct quantity, False otherwise.
        """

        found = False
        for available_chemical in self.chemicals:
            if available_chemical.name == chemical.name:
                comparison = available_chemical.compare_quantity(chemical)
                if comparison < 0:
                    return False
                if comparison >= 0:
                    found = True
        return found

    def add_chemicals(self, chemicals: 'Chemicals'):
        """
        Adds chemicals to the list of chemicals.

        Args:
            chemicals (Chemicals): The chemicals to add.
        """
        for chemical in chemicals.chemicals:
            self.add_chemical(chemical)

    def add_chemical(self, chemical: Chemical):
        """
        Adds a chemical to the list of chemicals.

        Args:
            chemical (Chemical): The chemical to add.
        """
        for available_chemical in self.chemicals:
            if available_chemical.name == chemical.name:
                available_chemical.add_quantity(chemical)
                break
        else:
            self.chemicals.append(chemical)

from typing import Union
from pydantic import BaseModel


class RequirementModel(BaseModel):
    """
    Represents the requirements for a workflow.

    Attributes:
        chemicals (Chemicals): The required chemicals.
        opentrons (Union[dict, str]): The Opentrons configuration.
        opentrons_setup (Union[dict, str]): The Opentrons setup configuration.
        arduino (Optional[Union[dict, str]]): The Arduino configuration.
        arduino_setup (Optional[Union[dict, str]]): The Arduino setup configuration.
        biologic (Optional[Union[dict, str]]): The Biologic configuration.
    """
    chemicals: Chemicals
    opentrons: Union[dict, str]
    opentrons_setup: Union[dict, str]
    arduino: Optional[Union[dict, str]] = None
    arduino_setup: Optional[Union[dict, str]] = None
    biologic: Optional[Union[dict, str]] = None

    @model_validator(mode='before')
    def process_fields(cls, values):
        """
        Processes each field that can be a filename, dict, or list. If a filename is given, it loads the corresponding JSON and processes it.

        Args:
            values (dict): The values to process.

        Returns:
            dict: The processed values.
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
        """
        Retrieves JSON content from a file by its name.

        Args:
            name (str): The name of the file.

        Returns:
            dict: The JSON content of the file.

        Raises:
            PermissionError: If there is a permission error accessing the file.
            ValueError: If there is an error decoding the JSON content or if the file is empty.
            FileNotFoundError: If the file is not found.
        """
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
    """
    Represents the setup for a workflow.

    Methods:
        from_config: Creates a SetupModel instance from a configuration.
        check_requirements: Checks if the available setup meets the requirements.
        check_chemicals: Checks if the available setup has the required chemicals.
        check_setup: Checks if the available setup has the required labware.
    """
    @classmethod
    def from_config(cls, chemicals, arduino, opentrons, opentrons_setup, arduino_setup, biologic):
        """
        Creates a SetupModel instance from a configuration.

        Args:
            chemicals (Chemicals): The chemicals configuration.
            arduino (dict): The Arduino configuration.
            opentrons (dict): The Opentrons configuration.
            opentrons_setup (dict): The Opentrons setup configuration.
            arduino_setup (dict): The Arduino setup configuration.
            biologic (dict): The Biologic configuration.

        Returns:
            SetupModel: A SetupModel instance.
        """
        return cls(
            chemicals=chemicals,
            arduino=arduino,
            opentrons=opentrons,
            opentrons_setup=opentrons_setup,
            arduino_setup=arduino_setup,
            biologic=biologic
        )




    def check_requirements(self, requirements: RequirementModel) -> bool:
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

    def check_setup(self, requirement: RequirementModel) -> bool:
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
    """
    A registry to discover and manage workflows.

    Attributes:
        package (str): The package to discover workflows from.
        _registry (dict): The registry of discovered workflows.
    """
    package = None
    _registry = {}

    @classmethod
    def initialize(cls, package='sdl'):
        """
        Initializes the registry with the given package.

        Args:
            package (str): The package to discover workflows from.
        """
        cls.package = package
        cls._discover_workflows()

    @classmethod
    def _discover_workflows(cls):
        """
        Discovers workflows in the specified package.
        """
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
        """
        Walks through the packages to discover modules.

        Args:
            package_name (str): The package name to walk through.

        Yields:
            str: The full module name.
        """
        package = importlib.import_module(package_name)
        for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
            full_module_name = f"{package_name}.{module_name}"
            yield full_module_name
            if is_pkg:
                yield from cls.walk_packages(full_module_name)

    @classmethod
    def get_procedure(cls, name):
        """
        Gets a procedure by its name.

        Args:
            name (str): The name of the procedure.

        Returns:
            type: The procedure class.

        Raises:
            KeyError: If no procedure is found with the given name.
        """
        if name not in cls._registry:
            raise KeyError(f"No procedure found with the name '{name}'.")
        return cls._registry[name]

    @classmethod
    def list_procedures(cls):
        """
        Lists all discovered procedures.

        Returns:
            list: A list of discovered procedures.
        """
        cls.initialize()
        return list(cls._registry.values())


P = TypeVar('P', bound=BaseModel)

class BaseProcedure(Generic[P]):
    def __init__(self, params: P):
        self.params = params

    pass


class BaseWorkflow(Registry):
    """
    Base class for workflows.

    Attributes:
        operations (list[Union['BaseWorkflow', BaseProcedure]]): The list of operations in the workflow.
        requirements (RequirementModel): The requirements for the workflow.
        outputs (list): The outputs of the workflow.
        procedures (list): The list of procedures in the workflow.
    """
    def __init__(self, operations: list[Union['BaseWorkflow', BaseProcedure]] = None):
        self.operations = operations if operations is not None else []
        self.requirements = None
        self.outputs = []
        self.procedures = self.get_procedures()

    def json(self):
        """
        Converts the workflow to a JSON representation.

        Returns:
            str: The JSON representation of the workflow.
        """
        return json.dumps({
            'name': self.__class__.__name__,
            'variables': {},
            'requirements': self.get_requirements().model_dump(),
        })

    @staticmethod
    def get_json_by_filename(name):
        """
        Retrieves JSON content from a file by its name.

        Args:
            name (str): The name of the file.

        Returns:
            dict: The JSON content of the file.

        Raises:
            PermissionError: If there is a permission error accessing the file.
            ValueError: If there is an error decoding the JSON content or if the file is empty.
            FileNotFoundError: If the file is not found.
        """
        directory = os.path.join(BASE_DIR, 'sdl', 'config')

        # Walk through the directory and subdirectories to find the file
        for root, dirs, files in os.walk(directory):
            if name in files:
                file_path = os.path.join(root, name)
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read().strip()
                        print(content)
                        if not content:
                            raise ValueError(f"The file {file_path} is empty.")
                        return json.loads(content)
                except PermissionError:
                    raise PermissionError(f"Permission denied when trying to access the file: {file_path}")
                except json.JSONDecodeError as e:
                    raise ValueError(f"Failed to decode JSON from file: {file_path}. Error: {str(e)}")

        raise FileNotFoundError(f"File {name} not found in config directory or its subdirectories: {directory}")

    @classmethod
    def get_all_subclasses(cls):
        """
        Get all subclasses of the current class as well as their subclasses.

        Returns:
            list: A list of subclasses.
        """
        all_subclasses = cls.list_procedures()  # Start with direct subclasses
        return all_subclasses

    @classmethod
    def from_config(cls, config: Union[dict, str, WorkflowModel], logger: logging.Logger=None):
        """
        Creates a workflow from a configuration dictionary.

        Args:
            config (Dict[str, Any]): The configuration dictionary.
            logger (Optional[logging.Logger]): The logger instance.

        Returns:
            BaseWorkflow: A workflow instance.

        Raises:
            TypeError: If there are missing or incorrect variables in the configuration.
        """
        if type(config) is str:
            config = cls.get_json_by_filename(config)
        elif type(config) is WorkflowModel:
            config = config.model_dump()
        workflow_name = config['name']
        workflow_variables = config.get('variables', {})
        try:
            workflow = cls.get_workflow(workflow_name)(**workflow_variables)
        except TypeError:
            if logger:
                logger.error(f"Failed to create workflow {workflow_name}, due to missing or incorrect variables: {workflow_variables}")
            raise TypeError(f"Failed to create workflow {workflow_name}, due to missing or incorrect variables: {workflow_variables}")
        return workflow

    @classmethod
    def get_workflow(cls, name):
        """
        Gets a workflow by name.

        Args:
            name (str): The name of the workflow.

        Returns:
            type: The workflow class.

        Raises:
            KeyError: If no workflow is found with the given name.
        """
        for subclass in cls.get_all_subclasses():
            if subclass.__name__ == name:
                return subclass
        raise KeyError(f"No workflow found with the name '{name}'.")

    def get_procedures(self):
        """
        Gets the procedures in the workflow.

        Returns:
            list: A list of procedures in the workflow.
        """
        procedures = []
        for operation in self.operations:
            if isinstance(operation, BaseProcedure):
                procedures.append(operation)
            elif hasattr(operation, 'get_procedures') and callable(operation.get_procedures):
                procedures.extend(operation.get_procedures())
        return procedures

    def get_requirements(self):
        """
        Gets the requirements for the workflow.

        Returns:
            RequirementModel: The requirements for the workflow.
        """
        if self.requirements is not None:
            return self.requirements
        else:
            # Initialize an empty Requirements object to accumulate results
            accumulated_requirements = RequirementModel(chemicals=Chemicals(chemicals=[]), opentrons_setup={}, opentrons={}, arduino={}, biologic={}, arduino_setup={})

            # Iterate through each operation
            for operation in self.operations:
                # Check if the operation has its own requirements
                if hasattr(operation, 'get_requirements') and callable(operation.get_requirements):
                    # Recursively get the requirements from the operation
                    sub_requirements = operation.get_requirements()

                    # Accumulate the chemicals and labware from the operation
                    accumulated_requirements.chemicals.add_chemicals(sub_requirements.chemicals)
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

    def add_step(self, step: BaseProcedure):
        """
        Adds a step to the workflow.

        Args:
            step (BaseStep): The step to add.
        """
        self.operations.append(step)


    def execute(self, *args, **kwargs):
        """
        Executes the workflow.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            list: The outputs of the workflow.
        """
        for operation in self.operations:
            output = operation.execute(*args, **kwargs)
            self.outputs.append(output)
        return self.outputs


class BaseStep:
    def execute(self):
        raise NotImplementedError("Each step must implement an execute method")




