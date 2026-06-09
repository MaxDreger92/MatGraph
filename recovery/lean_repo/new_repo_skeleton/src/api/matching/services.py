"""Service boundaries for matching endpoints.

Implementation should be ported from matching/views.py and matching/tasks.py.
"""

from domain.process.contracts import ProcessMessage
from domain.process.status import ProcessStatus

from .contracts import WorkflowMatchRequest


def start_fabrication_workflow_match(request: WorkflowMatchRequest) -> ProcessMessage:
    """POST /api/match/fabrication-workflow"""
    return ProcessMessage(status=ProcessStatus.PENDING, message="TODO: implement workflow matching orchestration")
