import os
import json
import logging
import requests
from django.conf import settings

from importing.models import ImportProcess, ImportProcessStatus, ImportProcessKeys

logger = logging.getLogger(__name__)

def send_importing_callback(process_id, key) -> None:
    logger.info("Sending importing callback")
    try:
        process = ImportProcess.objects.get(process_id=process_id)

        try:
            user_id = int(process.user_id)
        except (ValueError, TypeError):
            logger.error(f"Cannot cast user_id to int, got {process.user_id!r}")
            user_id = process.user_id

        status = process.status
        message = process.error_message

        results = None
        if status == ImportProcessStatus.COMPLETED and key != ImportProcessKeys.IMPORT:
            results = getattr(process, key, None)

        payload = {
            "user_id": user_id,
            "process_id": process_id,
            "key": key,
            "status": status,
            "results": results,
            "message": message,
        }

        headers = {"Content-Type": "application/json"}
        secret = getattr(settings, 'VIMI_SECRET', None)
        if secret:
            headers["X-API-KEY"] = secret

        resp = requests.post(
            f"{settings.VIMI_URL}webhooks/matgraph-import",
            headers=headers,
            json=payload,
            timeout=5,
        )
        resp.raise_for_status()
        logger.info(f"Callback sent for {process_id}/{key} with status {status}")

    except ImportProcess.DoesNotExist:
        logger.error(f"No ImportProcess found for process_id={process_id}")
    except requests.RequestException as e:
        logger.error(f"Failed to send callback for {process_id}/{key}: {e}", exc_info=True)
    except Exception as e:
        logger.exception("Uncaught error in send_importing_callback")
