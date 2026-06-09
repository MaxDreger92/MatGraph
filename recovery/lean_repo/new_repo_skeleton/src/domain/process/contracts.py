"""Domain contracts used by API adapters and task infrastructure."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ProcessRef:
    process_id: str
    user_id: str


@dataclass(frozen=True)
class ProcessMessage:
    status: int
    message: str = ""
    payload: Any = None
