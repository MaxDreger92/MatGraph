from django.db import models

class ProcessKeys:
    LABELS = "labels"
    ATTRIBUTES = "attributes"
    NODES = "nodes"
    GRAPH = "graph"
    IMPORT = "import"
    DATASET = "dataset"
    
class ProcessStatus:
    READY = 1
    PENDING = 2
    PROCESSING = 3
    COMPLETED = 4
    FAILED = 5
    PAUSED = 6
    CANCELLED = 7
    SKIPPED = 8
    TIMED_OUT = 9

    CHOICES = {
        READY: "Ready",
        PENDING: "Pending",
        PROCESSING: "Processing",
        COMPLETED: "Completed",
        FAILED: "Failed",
        PAUSED: "Paused",
        CANCELLED: "Cancelled",
        SKIPPED: "Skipped",
        TIMED_OUT: "Timed Out",
    }

    DJANGO_CHOICES = [(k, v) for k, v in CHOICES.items()]
    
class Process(models.Model):
    process_id = models.CharField(max_length=255, unique=True)
    user_id = models.CharField(max_length=255)
    
    status = models.PositiveSmallIntegerField(
        choices=ProcessStatus.DJANGO_CHOICES,
        default=ProcessStatus.PENDING,
    )
    error_message = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)