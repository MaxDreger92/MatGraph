"""Typed request contracts for importing API adapter layer."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LabelExtractRequest:
    process_id: str
    user_id: str
    context: str
    callback_url: str | None = None


@dataclass(frozen=True)
class AttributeExtractRequest:
    process_id: str
    user_id: str
    labels: Any = None
    callback_url: str | None = None


@dataclass(frozen=True)
class NodeExtractRequest:
    process_id: str
    user_id: str
    attributes: Any = None
    callback_url: str | None = None


@dataclass(frozen=True)
class GraphExtractRequest:
    process_id: str
    user_id: str
    nodes: Any = None
    callback_url: str | None = None


@dataclass(frozen=True)
class GraphImportRequest:
    process_id: str
    user_id: str
    graph: Any = None
    callback_url: str | None = None


@dataclass(frozen=True)
class ProcessControlRequest:
    process_id: str
    user_id: str


@dataclass(frozen=True)
class ProcessReportRequest(ProcessControlRequest):
    key: str
