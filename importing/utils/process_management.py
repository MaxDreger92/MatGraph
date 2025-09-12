from importing.models import ImportProcess
from tasks.models import ProcessStatus
import logging

logger = logging.getLogger(__name__)


def create_import_process(process_id, user_id, file_id, context, callback_url):
    try:
        new_process = ImportProcess.safe_create(
            process_id=process_id,
            user_id=user_id,
            callback_url=callback_url,
            file_id=file_id,
            context=context,
            status=ProcessStatus.READY,
        )
    except Exception as e:
        logger.exception("Error occurred during process creation: %s", e, exc_info=True)
        raise
    return new_process
