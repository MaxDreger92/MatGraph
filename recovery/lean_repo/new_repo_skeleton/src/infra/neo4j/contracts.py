"""Minimal graph query/result contracts used by matching and importing."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CypherQuery:
    query: str
    params: dict[str, Any]


@dataclass(frozen=True)
class CypherResult:
    rows: list[list[Any]]
    columns: list[str]
