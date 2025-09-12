from matching.models import ExtractProcess
from tasks.models import ProcessStatus
import logging

logger = logging.getLogger(__name__)


def create_extract_process(process_id, user_id, graph, callback_url):
    try:
        new_process = ExtractProcess.safe_create(
            process_id=process_id,
            user_id=user_id,
            callback_url=callback_url,
            graph=graph,
            status=ProcessStatus.READY,
        )
    except Exception as e:
        logger.exception("Error occurred during process creation: %s", e, exc_info=True)
        raise
    return new_process
