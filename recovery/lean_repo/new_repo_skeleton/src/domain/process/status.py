"""Canonical process statuses and keys for the lean extraction runtime."""

from enum import IntEnum


class ProcessStatus(IntEnum):
    READY = 1
    PENDING = 2
    PROCESSING = 3
    COMPLETED = 4
    FAILED = 5
    PAUSED = 6
    CANCELLED = 7
    SKIPPED = 8
    TIMED_OUT = 9


class ProcessKey:
    LABELS = "labels"
    ATTRIBUTES = "attributes"
    NODES = "nodes"
    GRAPH = "graph"
    IMPORT = "import"
    DATASET = "dataset"
