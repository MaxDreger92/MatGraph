"""Task and callback contracts for lean extraction runtime."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CallbackEnvelope:
    user_id: int | str
    process_id: str
    key: str
    status: int
    message: str = ""
    results: Any = None
