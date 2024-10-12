import json
from io import StringIO
import uuid
import logging

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from rest_framework import response, status
from rest_framework.views import APIView
from django.http import JsonResponse
from django.http import Http404

from importing.models import FullTableCache, ImportProcess
from importing.tasks import (
    extract_labels,
    extract_attributes,
    extract_nodes,
    extract_relationships,
    import_graph,
)
from importing.utils.file_processing import store_file
from importing.utils.process_management import create_import_process
from matgraph.models.metadata import File

from .task_manager import submit_task, cancel_task

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class LabelExtractView(APIView):
    def post(self, request):
        if "userId" not in request.POST:
            return response.Response(
                {"error": "No context provided"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "file" not in request.FILES:
            return response.Response(
                {"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "context" not in request.POST:
            return response.Response(
                {"error": "No context provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        file = request.FILES["file"]
        if not file.name.endswith(".csv"):
            return response.Response(
                {"error": "Invalid file type"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            file_record = store_file(file)
        except Exception as e:
            logger.error(f"Exception occurred while storing file: {e}", exc_info=True)
            return response.Response(
                {"error": "File storage failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        process_id = str(uuid.uuid4())
        user_id = request.POST["userId"]
        file_id = file_record.uid
        context = request.POST["context"]

        # TODO
        # cached = await self.try_cache(file_id)

        try:
            process = create_import_process(process_id, user_id, file_id, context)
            submit_task(process_id, extract_labels, process)
        except Exception as e:
            logger.error(
                f"Exception occurred while creating import process: {e}", exc_info=True
            )
            process.delete()
            return response.Response(
                {"error": "Failed to create import process"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return JsonResponse(
            {"process_id": process_id, "status": process.status},
            status=status.HTTP_201_CREATED,
        )

    def try_cache(self, file_id):
        file_record = File.nodes.get(uid=file_id)
        file_obj_bytes = file_record.get_file()
        file_obj_str = file_obj_bytes.decode("utf-8")
        file_obj = StringIO(file_obj_str)
        file_obj.seek(0)
        first_line = str(file_obj.readline().strip().lower())

        cached = FullTableCache.fetch(first_line)
        if cached:
            cached = str(cached).replace("'", '"')
            sanitized_cached = self.sanitize_data(cached)
            sanitized_cached_str = json.dumps(sanitized_cached)

            # send back
            return True
        return False


@method_decorator(csrf_exempt, name="dispatch")
class AttributeExtractView(APIView):

    def post(self, request):
        if "userId" not in request.POST:
            return response.Response(
                {"error": "No context provided"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "processId" not in request.POST:
            return response.Response(
                {"error": "No context provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        user_id = request.POST["userId"]
        process_id = request.POST["processId"]

        try:
            process = get_object_or_404(
                ImportProcess, user_id=user_id, process_id=process_id
            )
            if process.status is not "idle":
                return JsonResponse({"status": process.status})

            if "labels" in request.POST:
                labels = request.POST["labels"]
                process.labels = labels
            else:
                labels = process.labels

            process.status = "processing_attributes"
            process.save()

            submit_task(process_id, extract_attributes, process)

            return JsonResponse({"status": process.status})
        except Exception as e:
            process.status = "error"
            process.save()
            logger.error(f"Error during task submission: {e}", exc_info=True)


@method_decorator(csrf_exempt, name="dispatch")
class NodeExtractView(APIView):

    def post(self, request):
        if "userId" not in request.POST:
            return response.Response(
                {"error": "No context provided"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "processId" not in request.POST:
            return response.Response(
                {"error": "No context provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        user_id = request.POST["userId"]
        process_id = request.POST["processId"]

        try:
            process = get_object_or_404(
                ImportProcess, user_id=user_id, process_id=process_id
            )

            if "attributes" in request.POST:
                attributes = request.POST["attributes"]
                process.attributes = attributes
            else:
                attributes = process.attributes

            process.status = "processing_nodes"
            process.save()

            submit_task(process_id, extract_nodes, process)

            return JsonResponse({"status": process.status})
        except Exception as e:
            process.status = "error"
            process.save()
            logger.error(f"Error during task submission: {e}", exc_info=True)


@method_decorator(csrf_exempt, name="dispatch")
class GraphExtractView(APIView):

    def post(self, request):
        if "userId" not in request.POST:
            return response.Response(
                {"error": "No context provided"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "processId" not in request.POST:
            return response.Response(
                {"error": "No context provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        user_id = request.POST["userId"]
        process_id = request.POST["processId"]

        try:
            process = get_object_or_404(
                ImportProcess, user_id=user_id, process_id=process_id
            )

            if "graph" in request.POST:
                graph = request.POST["graph"]
                process.graph = graph
            else:
                graph = process.graph

            process.status = "processing_graph"
            process.save()

            submit_task(process_id, extract_relationships, process)

            return JsonResponse({"status": process.status})
        except Exception as e:
            process.status = "error"
            process.save()
            logger.error(f"Error during task submission: {e}", exc_info=True)


@method_decorator(csrf_exempt, name="dispatch")
class GraphImportView(APIView):

    def post(self, request):
        if "userId" not in request.POST:
            return response.Response(
                {"error": "No context provided"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "processId" not in request.POST:
            return response.Response(
                {"error": "No context provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        user_id = request.POST["userId"]
        process_id = request.POST["processId"]

        try:
            process = get_object_or_404(
                ImportProcess, user_id=user_id, process_id=process_id
            )

            if "graph" not in request.POST:
                graph = request.POST["graph"]
                process.graph = graph
            else:
                graph = process.graph

            process.status = "processing_import"
            process.save()

            submit_task(process_id, import_graph, process)

            return JsonResponse({"status": process.status})
        except Exception as e:
            process.status = "error"
            process.save()
            logger.error(f"Error during task submission: {e}", exc_info=True)


@method_decorator(csrf_exempt, name="dispatch")
class CancelTaskView(APIView):

    def post(self, request):
        if "userId" not in request.POST:
            return response.Response(
                {"error": "No context provided"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "processId" not in request.POST:
            return response.Response(
                {"error": "No context provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        user_id = request.POST["userId"]
        process_id = request.POST["processId"]

        process = get_object_or_404(
            ImportProcess, user_id=user_id, process_id=process_id
        )
        if process:
            success = cancel_task(process_id)
            if success:
                return JsonResponse({"status": ""})
        else:
            return JsonResponse(
                {
                    "cancelled": False,
                    "error": "Task not found or already completed",
                },
                status=404,
            )


@method_decorator(csrf_exempt, name="dispatch")
class ProcessReportView(APIView):

    def get(self, request):
        if "userId" not in request.POST:
            return response.Response(
                {"error": "No user_id provided"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "processId" not in request.POST:
            return response.Response(
                {"error": "No process_id provided"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "key" not in request.POST:
            return response.Response(
                {"error": "No key provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        user_id = request.POST["userId"]
        process_id = request.POST["processId"]
        key = request.POST["key"]

        try:
            process = get_object_or_404(
                ImportProcess, user_id=user_id, process_id=process_id
            )

            key_to_field_map = {
                "labels": "labels",
                "attributes": "attributes",
                "graph": "graph",
                "import": "import"
            }

            if key not in key_to_field_map:
                return response.Response(
                    {"error": "Invalid key provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            process_status = process.status
            response_data = {}

            data_field = key_to_field_map[key]
            data_value = getattr(process, data_field)
            data_available = data_value is not None

            if process_status == "error":
                response_data["status"] = process_status
                return response.Response(response_data, status=status.HTTP_200_OK)
            elif process_status == f"processing_{key}":
                response_data["status"] = "processing"
                return response.Response(response_data, status=status.HTTP_200_OK)
            elif process_status == "cancelled":
                response_data["status"] = "cancelled"
                return response.Response(response_data, status=status.HTTP_200_OK)
            elif process_status == "idle" and data_available:
                response_data["status"] = "success"
                response_data[key] = getattr(process, data_field)
                return response.Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data["status"] = process_status
                response_data["message"] = "Data not available yet"
                return response.Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error during writing report: {e}", exc_info=True)
            return response.Response(
                {f"error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name="dispatch")
class ProcessDeleteView(APIView):

    def post(self, request):
        if "userId" not in request.POST:
            return response.Response(
                {"error": "No user_id provided"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "processId" not in request.POST:
            return response.Response(
                {"error": "No process_id provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        user_id = request.POST["userId"]
        process_id = request.POST["processId"]

        try:
            process = get_object_or_404(
                ImportProcess, user_id=user_id, process_id=process_id
            )
            process.delete()
            
            return response.Response(
                {"message": "Process deleted successfully"},
                status=status.HTTP_200_OK,
            )
        except Http404:
            return response.Response(
                {"error": "Process not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error during deleting process: {e}", exc_info=True)
            return response.Response(
                {f"error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
