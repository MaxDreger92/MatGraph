"""Typed request contracts for matching API adapter layer."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class WorkflowMatchRequest:
    process_id: str
    user_id: str
    graph: Any
    callback_url: str
