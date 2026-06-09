"""Service boundaries for importing endpoints.

These adapters are intentionally thin and map one endpoint to one use-case function.
Implementation should be ported from importing/views.py and importing/tasks.py.
"""

from typing import Any

from domain.process.contracts import ProcessMessage
from domain.process.status import ProcessStatus

from .contracts import (
    AttributeExtractRequest,
    GraphExtractRequest,
    GraphImportRequest,
    LabelExtractRequest,
    NodeExtractRequest,
    ProcessControlRequest,
    ProcessReportRequest,
)


def start_label_extract(request: LabelExtractRequest, file_obj: Any) -> ProcessMessage:
    """POST /api/import/label-extract"""
    return ProcessMessage(status=ProcessStatus.PENDING, message="TODO: implement label extraction orchestration")


def start_attribute_extract(request: AttributeExtractRequest) -> ProcessMessage:
    """POST /api/import/attribute-extract"""
    return ProcessMessage(status=ProcessStatus.PENDING, message="TODO: implement attribute extraction orchestration")


def start_node_extract(request: NodeExtractRequest) -> ProcessMessage:
    """POST /api/import/node-extract"""
    return ProcessMessage(status=ProcessStatus.PENDING, message="TODO: implement node extraction orchestration")


def start_graph_extract(request: GraphExtractRequest) -> ProcessMessage:
    """POST /api/import/graph-extract"""
    return ProcessMessage(status=ProcessStatus.PENDING, message="TODO: implement graph extraction orchestration")


def start_graph_import(request: GraphImportRequest, session_first_line: str | None) -> ProcessMessage:
    """POST /api/import/graph-import"""
    return ProcessMessage(status=ProcessStatus.PENDING, message="TODO: implement graph import orchestration")


def cancel_process(request: ProcessControlRequest) -> ProcessMessage:
    """PATCH /api/import/cancel"""
    return ProcessMessage(status=ProcessStatus.PENDING, message="TODO: implement process cancellation")


def get_process_report(request: ProcessReportRequest) -> ProcessMessage:
    """GET /api/import/report"""
    return ProcessMessage(status=ProcessStatus.PENDING, message="TODO: implement process report retrieval")


def delete_process(request: ProcessControlRequest) -> ProcessMessage:
    """DELETE /api/import/delete"""
    return ProcessMessage(status=ProcessStatus.PENDING, message="TODO: implement process deletion")
