import io
import logging
import requests
from django.conf import settings

from importing.models import ImportProcess
from matching.models import ExtractProcess
from tasks.models import ProcessStatus, ProcessKeys

logger = logging.getLogger(__name__)


def _as_csv_bytes(value):
    try:
        import pandas as pd
    except Exception:
        pd = None
    if value is None:
        return b""
    if isinstance(value, bytes):
        return value
    if isinstance(value, str):
        return value.encode("utf-8")
    if pd is not None and isinstance(value, pd.DataFrame):
        return value.to_csv(index=False).encode("utf-8")
    try:
        return str(value).encode("utf-8")
    except Exception:
        return b""


def send_callback(process_id, key) -> None:
    logger.info("Sending callback")
    process = None

    try:
        process = ImportProcess.objects.get(process_id=process_id)
    except ImportProcess.DoesNotExist:
        try:
            process = ExtractProcess.objects.get(process_id=process_id)
        except Exception:
            logger.error(f"No process found for process_id={process_id}")
            return

    try:
        try:
            user_id = int(process.user_id)
        except (ValueError, TypeError):
            logger.error(f"Cannot cast user_id to int, got {getattr(process, 'user_id', None)!r}")
            user_id = process.user_id

        status = process.status
        message = getattr(process, "error_message", None)
        is_file = key == ProcessKeys.DATASET
        endpoint = "webhooks/matgraph"
        
        results = None
        if status == ProcessStatus.COMPLETED and not key == ProcessKeys.IMPORT:
            results = getattr(process, key, None)
            
        headers = {"X-API-KEY": settings.VIMI_SECRET}
        
        response_data = {
            "user_id": user_id,
            "process_id": process_id,
            "key": key,
            "status": status,
            "message": message or "",
        }

        if is_file:
            csv_bytes = _as_csv_bytes(results)
            files = None
            if csv_bytes:
                files = {"results": ("data_extract.csv", io.BytesIO(csv_bytes), "text/csv")}
            resp = requests.post(
                f"{settings.VIMI_URL}{endpoint}",
                headers=headers,
                data=response_data,
                files=files,
                timeout=15,
            )
        else:
            response_data["results"] = results
            resp = requests.post(
                f"{settings.VIMI_URL}{endpoint}",
                headers=headers,
                json=response_data,
                timeout=15,
            )

        resp.raise_for_status()
        logger.info(f"Callback sent for {process_id}/{key} with status {status}")
    except requests.RequestException as e:
        logger.error(f"Failed to send callback for {process_id}/{key}: {e}", exc_info=True)
    except Exception:
        logger.exception("Uncaught error in send_callback")
