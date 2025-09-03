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
            process_id = request.query_params.get("process_id")
            user_id = request.query_params.get("user_id")
            graph = request.data.get("graph")
            
            if not process_id:
                return Response(
                    {"status": ProcessStatus.FAILED, "message": "No process id provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not user_id:
                return Response(
                    {"status": ProcessStatus.FAILED, "message": "No user id provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if graph is None:
                return Response(
                    {"status": ProcessStatus.FAILED, "message": "No graph provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
                
            if isinstance(graph, str):
                import json
                try:
                    graph = json.loads(graph)
                except json.JSONDecodeError as e:
                    logger.exception("Loading JSON failed: %s", e, exc_info=True)
                    return Response(
                        {"status": ProcessStatus.FAILED, "message": "Invalid JSON in 'graph'"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                    
            logger.info(graph)
                    
            try:
                try:
                    process = ExtractProcess.objects.get(process_id=process_id, user_id=user_id)
                    process.graph = graph
                    process.error_message = None
                    process.save()
                    logger.info("Reusing existing extract process %s for user %s", process_id, user_id)
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
                    status=status.HTTP_202_ACCEPTED
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
