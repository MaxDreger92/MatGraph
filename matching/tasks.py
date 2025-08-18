import logging
import pandas as pd

from django.db import connection, close_old_connections

from tasks.models import ProcessStatus, ProcessKeys

from .fabricationworkflows import FabricationWorkflowMatcher

from tasks.utils.callback import send_callback

logger = logging.getLogger(__name__)


def match_workflow(task, process):
    close_old_connections()
    try:
        if task.is_cancelled():
            task_cancelled(process)
            return

        matcher = FabricationWorkflowMatcher(process.graph, force_report=True)

        if task.is_cancelled():
            task_cancelled(process)
            return

        matcher.run()

        if task.is_cancelled():
            task_cancelled(process)
            return
        
        if isinstance(matcher.result, pd.DataFrame):
            csv_content = matcher.result.to_csv(index=False)
        else:
            try:
                csv_content = str(matcher.result)
            except Exception:
                csv_content = ""

        process.dataset = csv_content
        process.status = ProcessStatus.COMPLETED
        process.save()
    except Exception as e:
        import traceback
        logger.error(f"Exception occurred while matching workflow: {e}", exc_info=True)
        process.status = ProcessStatus.FAILED
        process.error_message = traceback.format_exc()
        process.save()
    finally:
        send_callback(process.process_id, ProcessKeys.DATASET)
        connection.close()


def task_cancelled(process):
    process.status = ProcessStatus.CANCELLED
    process.error_message = "Task was cancelled by the user."
    process.save()
    logger.info(f"Task {process.process_id} was cancelled.")
