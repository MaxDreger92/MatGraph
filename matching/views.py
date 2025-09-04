import json
import logging
from django.db import close_old_connections, connection

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .utils.process_management import create_extract_process
from tasks.models import ProcessStatus
from .models import ExtractProcess

from .tasks import match_workflow
from tasks.task_manager import submit_task

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name="dispatch")
class WorkflowMatcher(APIView):
    def post(self, request):
        close_old_connections()
        try:
            from matching.serializers import WorkflowMatchSerializer

            raw_payload = request.data.get("payload")

            if raw_payload and isinstance(raw_payload, str):
                try:
                    raw_payload = json.loads(raw_payload)
                except json.JSONDecodeError:
                    raw_payload = {}
            elif not raw_payload:
                raw_payload = {}

            ser = WorkflowMatchSerializer(data=raw_payload)
            ser.is_valid(raise_exception=True)
            data = ser.validated_data

            process_id = data["process_id"]
            user_id = data["user_id"]
            graph = data["graph"]

            try:
                process = ExtractProcess.objects.get(process_id=process_id, user_id=user_id)
                process.graph = graph
                process.error_message = None
                process.save()
            except ExtractProcess.DoesNotExist:
                process = create_extract_process(process_id, user_id, graph)
            except Exception as e:
                logger.exception("Process creation failed: %s", e, exc_info=True)
                return Response(
                    {"status": ProcessStatus.FAILED, "message": "Process creation failed"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            try:
                if process.status == ProcessStatus.PROCESSING:
                    return Response(
                        {"status": process.status, "message": "Already processing"},
                        status=status.HTTP_202_ACCEPTED,
                    )

                process.status = ProcessStatus.PROCESSING
                process.save()

                submit_task(process_id, match_workflow, process)

                return Response(
                    {"status": ProcessStatus.PROCESSING, "message": "Process started"},
                    status=status.HTTP_202_ACCEPTED,
                )
            except Exception as e:
                import traceback
                logger.exception("Exception occurred while submitting task: %s", e, exc_info=True)
                process.status = ProcessStatus.FAILED
                process.error_message = traceback.format_exc()
                process.save()
                return Response(
                    {"status": ProcessStatus.FAILED, "message": "Process submission failed"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        finally:
            connection.close()
