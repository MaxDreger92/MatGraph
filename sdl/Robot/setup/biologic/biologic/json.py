"""
| Author: Mike Werezak <mike.werezak@nrcan-rncan.gc.ca>
| Created: 2024/03/01
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from biologic.deviceinfo import Json

if TYPE_CHECKING:
    pass

__all__ = (
    'Json',
    'to_json',
    'from_json',
    'FromJson',
    'ToJson',
)


## Helpers for defining from_json, and to_json conversions using decorators

ToJson = Callable[[Any], Json]
FromJson = Callable[[Json], Any]

def to_json(param: Any) -> Callable:
    """Decorator to define the function used to pack a parameter or field."""
    def decorator(func: ToJson) -> ToJson:
        param.to_json = func
        return func
    return decorator

def from_json(param: Any) -> Callable:
    """Decorator to define the function used to pack a parameter or field."""
    def decorator(func: FromJson) -> FromJson:
        param.to_json = func
        return func
    return decorator
