"""
| Author: Mike Werezak <mike.werezak@nrcan-rncan.gc.ca>
| Created: 2024/03/01
"""

from __future__ import annotations

from collections import ChainMap
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from biologic.json import from_json, to_json

if TYPE_CHECKING:
    from typing import Any, Optional, Type, Self, TypeVar
    from collections.abc import Collection
    from biologic.technique import Technique
    from biologic.json import Json, FromJson, ToJson

__all__ = (
    'Field',
    'TechniqueData',
    'TimeSeriesData',
    'from_json',
    'to_json',
)


if TYPE_CHECKING:
    _DataT = TypeVar('_DataT', bound='TechniqueData')

class Field:
    """Descriptor used to define the data fields of a technique.

    When used with TechniqueData, registers the field ID
    and replaces itself with a dataclasses.Field descriptor."""

    name: str = None  #: The attribute name used to access the field

    def __init__(
            self, *,
            to_json: Optional[ToJson] = None,
            from_json: Optional[FromJson] = None,

            units: Optional[str] = None,  #: unit tag, for informational purposes
    ):
        self.units = units

        self.to_json = to_json
        self.from_json = from_json

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}: {self.name!r}>'


class _DataMeta(type):
    """Metaclass for TechniqueParams data containers.

    Scans the class dict for TechParam instances and builds the _params_ attribute.
    Replaces the value of each found attribute with a dataclasses.Field descriptor so that
    TechniqueParams can be used with the dataclass decorator."""

    _fields_: ChainMap[str, Field]
    tech_type: Type[Technique]

    def __new__(cls, name: str, bases: tuple[Type, ...], cls_dict: dict[str, Any], **kwargs: Any):
        local_fields = {}
        for name, value in cls_dict.items():
            if isinstance(value, Field):
                value.name = name
                cls_dict[name] = field()  # replace with a dataclass field
                local_fields[name] = value

        # inherit fields from bases
        fields = [ local_fields ]
        for base in bases:
            base_fields = getattr(base, '_fields_', None)
            if base_fields:
                fields.append(base_fields)

        cls_obj = super().__new__(cls, name, bases, cls_dict, **kwargs)
        cls_obj._fields_ = ChainMap(*fields)

        return cls_obj


@dataclass(frozen=True)
class TechniqueData(metaclass=_DataMeta):
    """Base class for Technique parameter data containers."""

    def to_json(self) -> Json:
        json = {}
        for field in self.fields():
            name = field.name
            value = getattr(self, name)
            if field.to_json is not None:
                value = field.to_json(value)
            if value is not None:
                json[name] = value
        return json

    @classmethod
    def from_json(cls, json: dict[str, Json]) -> Self:
        kwargs = {}
        for field in cls.fields():
            name = field.name
            value = json.get(name)
            if field.from_json is not None:
                value = field.from_json(value)
            kwargs[name] = value
        # noinspection PyArgumentList
        return cls(**kwargs)

    @classmethod
    def fields(cls) -> Collection[Field]:
        return cls._fields_.values()

    @classmethod
    def get_field(cls, name: str) -> Field:
        return cls._fields_[name]


@dataclass(frozen=True)
class TimeSeriesData(TechniqueData):
    """Common base class for TechniqueData that has time information."""
    time: Optional[float] = Field(units="s")
    total_time: Optional[float] = Field(units="s")
