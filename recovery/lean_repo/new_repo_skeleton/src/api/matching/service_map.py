"""Endpoint to service-function mapping for matching API migration."""

ROUTE_TO_SERVICE = {
    ("POST", "/api/match/fabrication-workflow"): "start_fabrication_workflow_match",
}
