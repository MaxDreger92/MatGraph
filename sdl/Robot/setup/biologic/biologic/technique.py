"""
| Author: Mike Werezak <mike.werezak@nrcan-rncan.gc.ca>
| Created: 2024/02/22
"""

from __future__ import annotations

from numbers import Number
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, TypeVar

from kbio.tech_types import TECH_ID
from kbio.tech import make_ecc_parms

from biologic.json import (
    to_json,
    from_json,
)
from biologic.params import (
    TechniqueParams,
    Parameter,
    pack_parameter,
    ValidationError,
    yield_errors,
    validate_type,
    validate_range,
)
from biologic.data import TechniqueData, Field


if TYPE_CHECKING:
    from typing import Any, Type, ClassVar
    from collections.abc import Iterable, Collection, Mapping
    from kbio.types import EccParam, EccParams
    from biologic import BioLogic, DeviceFamily, DeviceInfo
    from biologic.channel import BLData

__all__ = (
    'TECH_ID',
    'Technique',
    'TechniqueParams',
    'TechniqueData',
    'UnpackDataError',
    'to_json',
    'from_json',
    'pack_parameter',
    'Parameter',
    'Field',
    'ValidationError',
    'yield_errors',
    'validate_type',
    'validate_range',
)


class UnpackDataError(Exception): pass


_ParamT = TypeVar('_ParamT', contravariant=True, bound=TechniqueParams)
_DataT = TypeVar('_DataT', covariant=True)

class Technique(ABC):
    """Base class for Techniques."""

    tech_id: ClassVar[TECH_ID] = None
    params_type: ClassVar[Type[TechniqueParams]] = None
    data_type: ClassVar[Type[TechniqueData]] = None

    _techniques = []

    # noinspection PyMethodOverriding
    def __init_subclass__(
            cls, tech_id: TECH_ID, params: Type[_ParamT], data: Type[_DataT], **kwargs: Any
    ):
        super().__init_subclass__(**kwargs)

        if not getattr(params, 'tech_type', None):
            params.tech_type = cls
        if not getattr(data, 'tech_type', None):
            data.tech_type = cls

        cls.tech_id = tech_id
        cls.params_type = params
        cls.data_type = data
        Technique._techniques.append(cls)

    @staticmethod
    def all_techniques() -> Iterable[Type[Technique]]:
        """Iterate all currently imported technique types."""
        return iter(Technique._techniques)

    def __init__(self, params: _ParamT):
        self.param_values = params

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.param_values!r})'

    @property
    @abstractmethod
    def timebase(self) -> float | Mapping[DeviceFamily, float]:
        """The technique timebase in **seconds**."""
        raise NotImplementedError

    def get_timebase(self, bl: BioLogic) -> float:
        """Get the technique timebase in **seconds**."""
        if isinstance(self.timebase, Number):
            return self.timebase

        device_family = bl.device_info.family
        timebase = self.timebase.get(device_family)
        if timebase is None:
            raise ValueError(f"technique does not support {device_family} devices")
        return timebase

    @property
    @abstractmethod
    def ecc_path(self) -> Mapping[DeviceFamily, str]:
        """The name of the ecc file used to load the technique."""
        raise NotImplementedError

    def get_ecc(self, bl: BioLogic) -> str:
        device_family = bl.device_info.family
        path = self.ecc_path.get(device_family)
        if path is None:
            raise ValueError(f"technique does not support {device_family} devices")
        return path

    def is_device_supported(self, device: DeviceInfo) -> bool:
        """Check if the device can run this technique."""
        return device.family in self.ecc_path

    def pack_parameters(self, bl: BioLogic) -> EccParams:
        return make_ecc_parms(bl.api, *self._iter_ecc_param(bl))

    def _iter_ecc_param(self, bl: BioLogic) -> Iterable[EccParam]:
        for param in self.params_type.parameters():
            yield from param.make_ecc_params(bl, self.param_values.get_value(param.name))

    @abstractmethod
    def unpack_data(self, bl: BioLogic, data: BLData) -> Iterable[_DataT]:
        raise NotImplementedError

    def validate(self, device_info: DeviceInfo) -> Iterable[ValidationError]:
        return self.param_values.validate(device_info)

    @classmethod
    def parameters(cls) -> Collection[Parameter]:
        return cls.params_type.parameters()
