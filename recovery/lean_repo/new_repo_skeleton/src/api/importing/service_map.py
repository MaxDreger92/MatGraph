"""Endpoint to service-function mapping for importing API migration."""

ROUTE_TO_SERVICE = {
    ("POST", "/api/import/label-extract"): "start_label_extract",
    ("POST", "/api/import/attribute-extract"): "start_attribute_extract",
    ("POST", "/api/import/node-extract"): "start_node_extract",
    ("POST", "/api/import/graph-extract"): "start_graph_extract",
    ("POST", "/api/import/graph-import"): "start_graph_import",
    ("PATCH", "/api/import/cancel"): "cancel_process",
    ("GET", "/api/import/report"): "get_process_report",
    ("DELETE", "/api/import/delete"): "delete_process",
}
