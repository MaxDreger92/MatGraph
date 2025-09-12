from django.db import models, IntegrityError, connection
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


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
    callback_url = models.URLField(null=True, blank=True)

    status = models.PositiveSmallIntegerField(
        choices=ProcessStatus.DJANGO_CHOICES,
        default=ProcessStatus.PENDING,
    )
    error_message = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    @classmethod
    def reset_pk_sequence(cls):
        """
        Reset the primary key sequence for this model's table.
        """
        table = cls._meta.db_table
        pk = cls._meta.pk.name

        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT setval(
                    pg_get_serial_sequence('"{table}"', '{pk}'),
                    COALESCE((SELECT MAX({pk}) FROM "{table}"), 1),
                    true
                );
            """)
        logger.warning(f"Sequence for table {table} reset to match current max({pk}).")

    @classmethod
    def safe_create(cls, **kwargs):
        """
        Attempts to create a record.
        If a duplicate key occurs due to a sequence mismatch, we fix the sequence and retry.
        """
        try:
            return cls.objects.create(**kwargs)
        except IntegrityError:
            logger.warning(f"IntegrityError on {cls.__name__} creation — resetting sequence and retrying...")
            cls.reset_pk_sequence()
            return cls.objects.create(**kwargs)
