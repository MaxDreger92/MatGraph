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

from importing.models import FullTableCache, ImportProcess, ImportProcessStatus
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
from .utils.data_processing import sanitize_data

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class LabelExtractView(APIView):
    def post(self, request):
        if "user_id" not in request.GET:
            return response.Response(
                {"error": "No user id provided"}, status=status.HTTP_400_BAD_REQUEST
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
        user_id = request.GET["user_id"]
        file_id = file_record.uid
        context = request.POST["context"]

        # TODO
        # cached = await self.try_cache(file_id)

        try:
            process = create_import_process(process_id, user_id, file_id, context)
        except Exception as e:
            return JsonResponse(
                {"error": f"Process creation failed with exception: {e}"})
        try:
            submit_task(process_id, extract_labels, process)
            return JsonResponse(
                {"process_id": process.process_id, "status": process.status},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            import traceback
            logger.error(
                f"Exception occurred while creating import process: {e}", exc_info=True
            )
            process.status = "error"
            process.error_message = traceback.format_exc()
            process.save()
            return response.Response(
                {"error": "Label extraction failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
            sanitized_cached = sanitize_data(cached)
            sanitized_cached_str = json.dumps(sanitized_cached)

            # send back
            return True
        return False


@method_decorator(csrf_exempt, name="dispatch")
class AttributeExtractView(APIView):

    def post(self, request):
        if "user_id" not in request.GET:
            return response.Response(
                {"error": "No context provided"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "process_id" not in request.GET:
            return response.Response(
                {"error": "No context provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        user_id = request.GET["user_id"]
        process_id = request.GET["process_id"]

        try:
            process = get_object_or_404(
                ImportProcess, user_id=user_id, process_id=process_id
            )
            process.error_message = None
        except Http404 as not_found:
            return JsonResponse({"error": "Process not found"}, status=404)
        try:
            if process.status == ImportProcessStatus.PROCESSING:
                return JsonResponse({"status": process.status, "message": "Not ready"})

            if "labels" in request.POST:
                process.labels = json.loads(request.POST["labels"])
            elif not process.labels:
                    return JsonResponse({"error": "No labels provided"}, status=400)

            process.status = ImportProcessStatus.PROCESSING
            process.save()

            submit_task(process_id, extract_attributes, process)

            return JsonResponse({"status": process.status})
        except Exception as e:
            import traceback
            process.status = ImportProcessStatus.FAILED
            process.error_message = traceback.format_exc()
            process.save()
            return JsonResponse({"error": "Attribute extraction failed"}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class NodeExtractView(APIView):

    def post(self, request):
        if "user_id" not in request.GET:
            return response.Response(
                {"error": "No context provided"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "process_id" not in request.GET:
            return response.Response(
                {"error": "No context provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        user_id = request.GET["user_id"]
        process_id = request.GET["process_id"]

        try:
            process = get_object_or_404(
                ImportProcess, user_id=user_id, process_id=process_id
            )
            process.error_message = None
        except Http404 as not_found:
            return JsonResponse({"error": "Process not found"}, status=404)
        try:
            if process.status == ImportProcessStatus.PROCESSING:
                return JsonResponse({"status": process.status, "message": "Not ready"})

            if "attributes" in request.POST:
                process.attributes = json.loads(request.POST["attributes"])
            elif not process.attributes:
                    return JsonResponse({"error": "No attributes provided"}, status=400)

            process.status = ImportProcessStatus.PROCESSING
            process.save()

            submit_task(process_id, extract_nodes, process)

            return JsonResponse({"status": process.status})
        except Exception as e:
            import traceback
            process.status = ImportProcessStatus.FAILED
            process.error_message = traceback.format_exc()
            process.save()
            return JsonResponse({"error": "Node extraction failed"}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class GraphExtractView(APIView):

    def post(self, request):
        if "user_id" not in request.GET:
            return response.Response(
                {"error": "No context provided"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "process_id" not in request.GET:
            return response.Response(
                {"error": "No context provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        user_id = request.GET["user_id"]
        process_id = request.GET["process_id"]

        try:
            process = get_object_or_404(
                ImportProcess, user_id=user_id, process_id=process_id
            )
            process.error_message = None
        except Http404 as not_found:
            return JsonResponse({"error": "Process not found"}, status=404)
        try:
            if process.status == ImportProcessStatus.PROCESSING:
                return JsonResponse({"status": process.status, "message": "Not ready"})

            if "graph" in request.POST:
                process.nodes = json.loads(request.POST["graph"])
            elif not process.nodes:
                    return JsonResponse({"error": "No graph provided"}, status=400)

            process.status = ImportProcessStatus.PROCESSING
            process.save()

            submit_task(process_id, extract_relationships, process)

            return JsonResponse({"status": process.status})
        except Exception as e:
            import traceback
            process.status = ImportProcessStatus.FAILED
            process.error_message = traceback.format_exc()
            process.save()
            return JsonResponse({"error": "Graph extraction failed"}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class GraphImportView(APIView):

    def post(self, request):
        if "user_id" not in request.GET:
            return response.Response(
                {"error": "No context provided"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "process_id" not in request.GET:
            return response.Response(
                {"error": "No context provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        user_id = request.GET["user_id"]
        process_id = request.GET["process_id"]

        try:
            process = get_object_or_404(
                ImportProcess, user_id=user_id, process_id=process_id
            )
            process.error_message = None
        except Http404 as not_found:
            return JsonResponse({"error": "Process not found"}, status=404)
        try:
            if process.status == ImportProcessStatus.PROCESSING:
                return JsonResponse({"status": process.status, "message": "Not ready"})

            if "graph" in request.POST:
                process.graph = json.loads(request.POST["graph"])
            elif not process.graph:
                    return JsonResponse({"error": "No graph provided"}, status=400)

            process.status = ImportProcessStatus.PROCESSING
            process.save()

            submit_task(process_id, import_graph, process, {"session": request.session.get("first_line")})
            return JsonResponse({"status": process.status})
        except Exception as e:
            import traceback
            process.status = ImportProcessStatus.FAILED
            process.error_message = traceback.format_exc()
            process.save()
            logger.error(f"Error during task submission: {e}", exc_info=True)
            return JsonResponse({"error": "Graph import failed"}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class CancelTaskView(APIView):

    def patch(self, request):
        if "user_id" not in request.GET:
            return response.Response(
                {"error": "No context provided"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "process_id" not in request.GET:
            return response.Response(
                {"error": "No context provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        user_id = request.GET["user_id"]
        process_id = request.GET["process_id"]

        process = get_object_or_404(
            ImportProcess, user_id=user_id, process_id=process_id
        )
        if process:
            success = cancel_task(process_id)
            if success:
                return JsonResponse({"status": ImportProcessStatus.CANCELLED})
        else:
            return JsonResponse(
                {
                    "error": "Task not found or already completed",
                },
                status=404,
            )


@method_decorator(csrf_exempt, name="dispatch")
class ProcessReportView(APIView):

    def get(self, request):
        if "user_id" not in request.GET:
            return response.Response(
                {"error": "No user_id provided"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "process_id" not in request.GET:
            return response.Response(
                {"error": "No process_id provided"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "key" not in request.GET:
            return response.Response(
                {"error": "No key provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        user_id = request.GET["user_id"]
        process_id = request.GET["process_id"]
        key = request.GET["key"]

        try:
            process = get_object_or_404(
                ImportProcess, user_id=user_id, process_id=process_id
            )
            process_status = process.status
            # if process_status in ["error", "cancelled"]:
            #     return response.Response({"status": process_status}, status=status.HTTP_200_OK)

            key_to_field_map = {
                "labels": "labels",
                "attributes": "attributes",
                "nodes": "nodes",
                "graph": "graph",
                "import": "import",
            }

            if key not in key_to_field_map:
                return response.Response(
                    {"error": "Invalid key provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            response_data = {}
            response_data["status"] = process_status
            response_data["error"] = process.error_message

            if key == "import":
                return response.Response(response_data, status=status.HTTP_200_OK)
            
            data_field = key_to_field_map[key]
            data_value = getattr(process, data_field)
            data_available = data_value is not None
            
            if process_status == ImportProcessStatus.PROCESSING or not data_available:
                response_data["message"] = "Data not available yet"
                return response.Response(response_data, status=status.HTTP_200_OK)

            response_key = key
            if key == "nodes":
                response_key = "graph"
                
            response_data[response_key] = data_value
            response_data["status"] = ImportProcessStatus.COMPLETED
            return response.Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error during writing report: {e}", exc_info=True)
            return response.Response(
                {f"error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name="dispatch")
class ProcessDeleteView(APIView):

    def delete(self, request):
        if "user_id" not in request.GET:
            return response.Response(
                {"error": "No user_id provided"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "process_id" not in request.GET:
            return response.Response(
                {"error": "No process_id provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        user_id = request.GET["user_id"]
        process_id = request.GET["process_id"]

        try:
            process = get_object_or_404(
                ImportProcess, user_id=user_id, process_id=process_id
            )
            process.delete()

            return response.Response(
                {"status": ImportProcessStatus.CANCELLED},
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
