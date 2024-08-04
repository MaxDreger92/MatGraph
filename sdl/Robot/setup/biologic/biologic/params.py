"""
| Author: Mike Werezak <mike.werezak@nrcan-rncan.gc.ca>
| Created: 2024/02/22
"""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from collections import ChainMap
from collections.abc import Iterable, Collection
from typing import TYPE_CHECKING

from kbio.tech import ECC_parm, make_ecc_parm
from kbio.types import E_RANGE, I_RANGE, BANDWIDTH, EccParam
from biologic.json import from_json, to_json

if TYPE_CHECKING:
    from typing import Any, Optional, Type, Self, Callable
    from numbers import Number
    from biologic import BioLogic, DeviceInfo
    from biologic.json import Json, FromJson, ToJson
    from biologic.technique import Technique

__all__ = (
    'ValidationError',
    'pack_parameter',
    'Parameter',
    'TechniqueParams',
    'yield_errors',
    'validate_type',
    'validate_range',
    'validate_len',
    'DataRange',
    'E_RANGE',
    'I_RANGE',
    'BANDWIDTH',
    'from_json',
    'to_json',
)


class ValidationError(Exception):
    def __init__(self, param: str, message: str):
        self.param = param
        self.message = message
        super().__init__(f"parameter '{param}' {message}")


if TYPE_CHECKING:
    PackFunc = Callable[[Any], Any]


def pack_parameter(param: Any) -> Callable:
    """Decorator to define the function used to pack a parameter."""
    def decorator(func: PackFunc) -> PackFunc:
        param.pack = func
        return func
    return decorator


class Parameter:
    """Descriptor used to define the parameters of a technique.

    When used with TechniqueParams, registers the parameter ID
    and replaces itself with a dataclasses.Field descriptor."""

    name: str = None  #: The attribute name used to access the parameter

    param_id: str
    pack_type: Optional[type]

    NoDefault = object()

    def __init__(
            self,
            param_id: Optional[str] = None,
            pack_type: Optional[type] = None, *,
            default: Any = NoDefault,
            default_factory: Optional[Callable] = None,
            pack: Optional[PackFunc] = None,
            to_json: Optional[ToJson] = None,
            from_json: Optional[FromJson] = None,

            data_range: Optional[DataRange | Callable[[DeviceInfo], DataRange]] = None,
            units: Optional[str] = None,  #: unit tag, for informational purposes

            #: Specify conditional support for the the parameter depending on the device details
            #: If supplied, the parameter will only be used if the given predicate returns True.
            supports_devices: Optional[Callable[[DeviceInfo], bool]] = None,

            #: if False, do not create a field.
            #: The value is expected to be either derived from a property or set by __post_init__()
            #: if create_property is not None this will be forced to False
            create_field: bool = True,

            #: if set, create a property using the given callable
            create_property: Optional[Callable] = None,

            #: Used if the parameter represents a single element of a fixed-length array
            #: Setting this option (e.g. to 0) will force this parameter to be a scalar
            array_index: Optional[int] = None,
    ):
        if param_id is not None and pack_type is not None:
            self._ecc_proto = ECC_parm(param_id, pack_type)
        elif param_id is None and pack_type is None:
            self._ecc_proto = None
        else:
            raise ValueError('param_id and pack_type must either be both None or not-None')

        self.data_range = data_range
        self.units = units

        self.supports_devices = supports_devices

        self.create_field = create_field if create_property is None else False
        self.create_property = create_property
        self.array_index = array_index

        self.default = default
        self.default_factory = default_factory
        if default is not self.NoDefault and default_factory is not None:
            raise ValueError("default and default_factory cannot both be specified")

        self.pack = pack
        self.to_json = to_json
        self.from_json = from_json

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}: {self.name!r}, {self.param_id!r}>'

    @property
    def param_id(self) -> Optional[str]:
        """The parameter string ID defined by BioLogic"""
        if self._ecc_proto is not None:
            return self._ecc_proto.label
        return None

    @property
    def pack_type(self) -> Optional[type]:
        """The parameter pack type used by BioLogic"""
        if self._ecc_proto is not None:
            return self._ecc_proto.type_
        return None

    def get_default(self) -> Any:
        """Get the default value for this parameter if it has one, or raise AttributeError"""
        if self.default_factory is not None:
            return self.default_factory()

        if self.default is self.NoDefault:
            raise AttributeError("parameter does not have a default value")
        return self.default

    def get_data_range(self, device_info: DeviceInfo) -> Optional[DataRange]:
        if self.data_range is None:
            return None
        if isinstance(self.data_range, DataRange):
            return self.data_range
        return self.data_range(device_info)

    def make_ecc_params(self, bl: BioLogic, value: Any) -> Iterable[EccParam]:
        if self._ecc_proto is None:
            return

        if self.supports_devices is not None:
            if not self.supports_devices(bl.device_info):
                return

        if self.pack is not None:
            value = self.pack(value)

        if self.array_index is not None:
            yield make_ecc_parm(bl.api, self._ecc_proto, value, self.array_index)
        elif not isinstance(value, Iterable):
            yield make_ecc_parm(bl.api, self._ecc_proto, value)
        else:
            for idx, item in enumerate(value):
                yield make_ecc_parm(bl.api, self._ecc_proto, item, idx)

    def property(self, fget: Callable) -> Self:
        """Decorator to setup property-like Parameters."""
        self.create_property = fget
        return self

class _ParamsMeta(ABCMeta):
    """Metaclass for TechniqueParams data containers.

    Scans the class dict for TechParam instances and builds the _params_ attribute.
    Replaces the value of each found attribute with a dataclasses.Field descriptor so that
    TechniqueParams can be used with the dataclass decorator."""

    _params_: ChainMap[str, Parameter]

    tech_type: Type[Technique]

    def __new__(cls, name: str, bases: tuple[Type, ...], cls_dict: dict[str, Any], **kwargs: Any):
        local_params = {}
        for name, value in list(cls_dict.items()):
            if isinstance(value, Parameter):
                value.name = name

                if value.create_property is not None:
                    cls_dict[name] = property(value.create_property)
                elif not value.create_field:
                    cls_dict.pop(name)
                    if name in cls_dict['__annotations__']:
                        # needed to prevent dataclass from creating a field
                        del cls_dict['__annotations__'][name]
                else:
                    # replace instance with a field for dataclass support
                    if value.default is not Parameter.NoDefault:
                        field_obj = field(default=value.default)
                    elif value.default_factory is not None:
                        field_obj = field(default_factory=value.default_factory)
                    else:
                        field_obj = field()
                    cls_dict[name] = field_obj

                local_params[name] = value

        params = [ local_params ]
        for base in bases:
            base_params = getattr(base, '_params_', None)
            if base_params:
                params.append(base_params)

        cls_obj = super().__new__(cls, name, bases, cls_dict, **kwargs)
        cls_obj._params_ = ChainMap(*params)

        return cls_obj


@dataclass(kw_only=True)
class TechniqueParams(metaclass=_ParamsMeta):
    """Base class for Technique parameter data containers."""

    # Common hardware parameters (7.1.3)

    E_range: E_RANGE = Parameter(
        'E_Range', int,
        default=E_RANGE.E_RANGE_AUTO,
        pack=lambda o: o.value,
        to_json=lambda o: o.name,
        from_json=lambda s: E_RANGE[s],
    )

    I_range: I_RANGE = Parameter(
        'I_Range', int,
        default=I_RANGE.I_RANGE_AUTO,
        pack=lambda o: o.value,
        to_json=lambda o: o.name,
        from_json=lambda s: I_RANGE[s],
    )

    bandwidth: BANDWIDTH = Parameter(
        'Bandwidth', int,
        default=BANDWIDTH.BW_KEEP,
        pack=lambda o: o.value,
        to_json=lambda o: o.name,
        from_json=lambda s: BANDWIDTH[s],
    )

    def get_value(self, name: str) -> Any:
        try:
            return getattr(self, name)
        except AttributeError:
            pass

        param = self._params_.get(name)
        if param is None:
            raise AttributeError(f"{self.__class__.__name__} has no parameter {name!r}") from None
        return param.get_default()

    @abstractmethod
    def validate(self, device_info: DeviceInfo) -> Iterable[ValidationError]:
        tests = [
            validate_type(self.E_range, 'E_range', E_RANGE),
            validate_type(self.I_range, 'I_range', I_RANGE),
            validate_type(self.bandwidth, 'bandwidth', BANDWIDTH),
        ]

        # validate range of any parameters that have data_range set
        for param in self.parameters():
            data_range = param.get_data_range(device_info)
            if data_range is not None:
                value = self.get_value(param.name)
                if not isinstance(value, Iterable):
                    tests.append(validate_data_range(value, param.name, data_range))
                else:
                    tests.extend(
                        validate_data_range(elem, f'{param.name}[{idx}]', data_range)
                        for idx, elem in enumerate(value)
                    )

        yield from yield_errors(tests)

    def to_json(self) -> Json:
        json = {}
        for param in self.parameters():
            if param.create_field is False:
                continue

            name = param.name

            try:
                value = getattr(self, name)
            except AttributeError:
                continue

            if param.to_json is not None:
                value = param.to_json(value)
            if value is not None:
                json[name] = value
        return json

    @classmethod
    def from_json(cls, json: dict[str, Json]) -> Self:
        kwargs = {}
        for param in cls.parameters():
            name = param.name

            try:
                value = json[name]
            except KeyError:
                continue

            if param.from_json is not None:
                try:
                    value = param.from_json(value)
                except BaseException as error:
                    raise ValueError(f"invalid value for {name}: {value!r}") from error

            kwargs[name] = value

        return cls(**kwargs)

    @classmethod
    def parameters(cls) -> Collection[Parameter]:
        return cls._params_.values()

    @classmethod
    def get_parameter(cls, name: str) -> Parameter:
        return cls._params_[name]


## Validation Helpers

def yield_errors(errors: Iterable[ValidationError]) -> Iterable[ValidationError]:
    yield from (error for error in errors if error is not None)

def validate_type(value: Any, name: str, require_type: Type) -> Optional[ValidationError]:
    if not isinstance(value, require_type):
        message = (
            f"incorrect type, value must be of type {require_type.__name__} "
            f"but {type(value).__name__} was given instead"
        )
        return ValidationError(name, message)

def validate_range(
        value: Any, name: str,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
) -> Optional[ValidationError]:
    if min_value is not None and value < min_value:
        return ValidationError(name, f"value must be greater than or equal to {min_value}")
    if max_value is not None and value > max_value:
        return ValidationError(name, f"value must be less than or equal to {max_value}")

def validate_data_range(value: Any, name: str, data_range: DataRange) -> Optional[ValidationError]:
    if value not in data_range:
        return ValidationError(name, f"value not in range: {data_range}")

def validate_len(value: Any, name: str, required_len: int) -> Optional[ValidationError]:
    try:
        length = len(value)
    except TypeError:
        return ValidationError(name, "incorrect type, value must have a length")

    if length != required_len:
        return ValidationError(name, f"value must contain exactly {required_len} elements")

@dataclass(frozen=True)
class DataRange:
    """Describe data range for numeric values."""
    min_value: Optional[Number]
    max_value: Optional[Number]

    # strict means the value must be strictly greater than the min and less than the max otherwise greater or equal is applied.
    # i.e. strict min,max on both sides is (n,m) and not strict on both sides is [n,m]
    min_strict: bool = field(default=False, kw_only=True)
    max_strict: bool = field(default=False, kw_only=True)

    def __str__(self) -> str:
        match self.min_value, self.max_value:
            case None, None:
                return "(..)"
            case min_value, None:
                if self.min_strict:
                    return f"> {min_value}"
                return f">= {min_value}"
            case None, max_value:
                if self.max_strict:
                    return f"< {max_value}"
                return f"<= {max_value}"
            case min_value, max_value:
                lower = "(" if self.min_strict else "["
                upper = ")" if self.max_strict else "]"
                return f"{lower}{min_value}..{max_value}{upper}"

    def __contains__(self, value: Number) -> bool:
        return (
            self._compare_lower_bound(value) <= 0
            and self._compare_upper_bound(value) <= 0
        )

    def clamp(self, value: Number) -> Number:
        if self._compare_lower_bound(value) > 0:
            return self.min_value
        if self._compare_upper_bound(value) > 0:
            return self.max_value
        return value

    def _compare_lower_bound(self, value: Optional[Number]) -> int:
        """Return 1 if value is outside, -1 if inside, and 0 if equal."""
        if value is None:
            return 0 if self.min_value is None else 1
        if self.min_value is None or self.min_value < value:
            return -1
        if not self.min_strict and self.min_value == value:
            return 0
        return 1

    def _compare_upper_bound(self, value: Optional[Number]) -> int:
        """Return 1 if value is outside, -1 if inside, and 0 if equal."""
        if value is None:
            return 0 if self.max_value is None else 1
        if self.max_value is None or value < self.max_value:
            return -1
        if not self.max_strict and self.max_value == value:
            return 0
        return 1

    def __eq__(self, other: Any) -> Any:
        if not isinstance(other, DataRange):
            return NotImplemented
        
        self_min = None if self.min_value is None else (self.min_value, self.min_strict)
        other_min = None if other.min_value is None else (other.min_value, other.min_strict)
        
        self_max = None if self.max_value is None else (self.max_value, self.max_strict)
        other_max = None if other.max_value is None else (other.max_value, other.max_strict)
        
        return (self_min, self_max) == (other_min, other_max)
