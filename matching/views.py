import uuid
import logging
import json
from django.db import close_old_connections, connection

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import response, status
from django.http import JsonResponse
from rest_framework.views import APIView

from .utils.process_management import create_extract_process
from tasks.models import ProcessStatus

from .tasks import match_workflow
from tasks.task_manager import submit_task

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name="dispatch")
class WorkflowMatcher(APIView):
    def post(self, request):
        close_old_connections()
        try:
            if "user_id" not in request.GET:
                return response.Response(
                    {"error": "No user id provided"}, status=status.HTTP_400_BAD_REQUEST
                )
            if "graph" not in request.POST:
                return response.Response(
                    {"error": "No graph provided"}, status=status.HTTP_400_BAD_REQUEST
                )

            user_id = request.GET["user_id"]
            graph = json.loads(request.POST["graph"])

            try:
                process_id = str(uuid.uuid4())
                process = create_extract_process(process_id, user_id, graph)
            except Exception as e:
                return JsonResponse(
                    {"error": f"Process creation failed with exception: {e}"}
                )
                
            try:
                process.status = ProcessStatus.PROCESSING
                process.save()
                submit_task(process_id, match_workflow, process)
                return JsonResponse(
                    {"process_id": process_id, "status": process.status},
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                import traceback
                logger.error(
                    f"Exception occurred while submitting task: {e}", exc_info=True
                )
                process.status = ProcessStatus.FAILED
                process.error_message = traceback.format_exc()
                process.save()
                return response.Response(
                    {"error": "Data extraction failed"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        finally:
            connection.close()
