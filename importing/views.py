from io import StringIO
import logging
import json

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import Http404

from django.db import connection, close_old_connections

from .models import FullTableCache, ImportProcess
from .tasks import (
    extract_labels,
    extract_attributes,
    extract_nodes,
    extract_relationships,
    import_graph,
)
from .utils.file_processing import store_file
from .utils.process_management import create_import_process
from matgraph.models.metadata import File

from tasks.task_manager import submit_task, cancel_task
from tasks.models import ProcessStatus
# from .utils.data_processing import sanitize_data

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class LabelExtractView(APIView):
    def post(self, request):
        close_old_connections()
        try:
            from importing.serializers import CsvFileSerializer, LabelExtractSerializer

            file_ser = CsvFileSerializer(data={"file": request.FILES.get("file")})
            file_ser.is_valid(raise_exception=True)
            file = file_ser.validated_data["file"]

            raw_payload = request.data.get("payload")

            if raw_payload and isinstance(raw_payload, str):
                try:
                    raw_payload = json.loads(raw_payload)
                except json.JSONDecodeError:
                    raw_payload = {}
            elif not raw_payload:
                raw_payload = {}

            ser = LabelExtractSerializer(data=raw_payload)
            ser.is_valid(raise_exception=True)
            data = ser.validated_data

            process_id = data["process_id"]
            user_id = data["user_id"]
            context = data["context"]
            callback_url = data.get("callback_url")

            try:
                file_record = store_file(file)
            except Exception as e:
                logger.exception("Exception occurred while storing file: %s", e, exc_info=True)
                return Response(
                    {"status": ProcessStatus.FAILED, "message": "File storage failed"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            file_id = file_record.uid

            # TODO
            # cached = await self.try_cache(file_id)

            try:
                process = ImportProcess.objects.get(process_id=process_id, user_id=user_id)
                process.file_id = file_id
                process.context = context
                process.callback_url = callback_url
                process.error_message = None
                process.save()
            except ImportProcess.DoesNotExist:
                process = create_import_process(process_id, user_id, file_id, context, callback_url)
            except Exception as e:
                logger.exception("Process creation failed: %s", e, exc_info=True)
                return Response(
                    {"status": ProcessStatus.FAILED, "message": "Process creation failed"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            try:
                process.status = ProcessStatus.PROCESSING
                process.save()
                submit_task(process_id, extract_labels, process)
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
                    {"status": ProcessStatus.FAILED, "message": "Label extraction failed"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        finally:
            connection.close()

    def try_cache(self, file_id):
        close_old_connections()
        try:
            file_record = File.nodes.get(uid=file_id)
            file_obj_bytes = file_record.get_file()
            file_obj_str = file_obj_bytes.decode("utf-8")
            file_obj = StringIO(file_obj_str)
            file_obj.seek(0)
            first_line = str(file_obj.readline().strip().lower())

            cached = FullTableCache.fetch(first_line)
            if cached:
                # cached = str(cached).replace("'", '"')
                # sanitized_cached = sanitize_data(cached)
                # sanitized_cached_str = json.dumps(sanitized_cached)

                # send back
                return True
            return False
        finally:
            connection.close()


@method_decorator(csrf_exempt, name="dispatch")
class AttributeExtractView(APIView):
    def post(self, request):
        close_old_connections()
        try:
            from importing.serializers import AttributeExtractSerializer

            raw_payload = request.data.get("payload")

            if raw_payload and isinstance(raw_payload, str):
                try:
                    raw_payload = json.loads(raw_payload)
                except json.JSONDecodeError:
                    raw_payload = {}
            elif not raw_payload:
                raw_payload = {}

            ser = AttributeExtractSerializer(data=raw_payload)
            ser.is_valid(raise_exception=True)
            data = ser.validated_data

            process_id = data["process_id"]
            user_id = data["user_id"]
            labels = data.get("labels")
            callback_url = data.get("callback_url")

            try:
                process = ImportProcess.objects.get(process_id=process_id, user_id=user_id)
                process.error_message = None
                process.callback_url = callback_url
                process.save()
            except Exception as e:
                logger.exception("Process not found: %s", e, exc_info=True)
                return Response(
                    {"status": ProcessStatus.FAILED, "message": "Process not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            try:
                if process.status == ProcessStatus.PROCESSING:
                    return Response(
                        {"status": process.status, "message": "Not ready"},
                        status=status.HTTP_202_ACCEPTED,
                    )

                if labels is not None:
                    process.labels = labels
                elif not process.labels:
                    return Response(
                        {"status": ProcessStatus.FAILED, "message": "No labels provided"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                process.status = ProcessStatus.PROCESSING
                process.save()

                submit_task(process_id, extract_attributes, process)

                return Response(
                    {"status": ProcessStatus.PROCESSING, "message": "Process started"},
                    status=status.HTTP_202_ACCEPTED,
                )
            except Exception as e:
                import traceback

                logger.exception("Exception occurred while submitting attribute extraction task: %s", e, exc_info=True)
                process.status = ProcessStatus.FAILED
                process.error_message = traceback.format_exc()
                process.save()
                return Response(
                    {"status": ProcessStatus.FAILED, "message": "Attribute extraction failed"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        finally:
            connection.close()


@method_decorator(csrf_exempt, name="dispatch")
class NodeExtractView(APIView):
    def post(self, request):
        close_old_connections()
        try:
            from importing.serializers import NodeExtractSerializer

            raw_payload = request.data.get("payload")

            if raw_payload and isinstance(raw_payload, str):
                try:
                    raw_payload = json.loads(raw_payload)
                except json.JSONDecodeError:
                    raw_payload = {}
            elif not raw_payload:
                raw_payload = {}

            ser = NodeExtractSerializer(data=raw_payload)
            ser.is_valid(raise_exception=True)
            data = ser.validated_data

            process_id = data["process_id"]
            user_id = data["user_id"]
            attributes = data.get("attributes")
            callback_url = data.get("callback_url")

            try:
                process = ImportProcess.objects.get(process_id=process_id, user_id=user_id)
                process.error_message = None
                process.callback_url = callback_url
                process.save()
            except Exception as e:
                logger.exception("Process not found: %s", e, exc_info=True)
                return Response(
                    {"status": ProcessStatus.FAILED, "message": "Process not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            try:
                if process.status == ProcessStatus.PROCESSING:
                    return Response(
                        {"status": process.status, "message": "Not ready"},
                        status=status.HTTP_202_ACCEPTED,
                    )

                if attributes is not None:
                    process.attributes = attributes
                elif not process.attributes:
                    return Response(
                        {"status": ProcessStatus.FAILED, "message": "No attributes provided"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                process.status = ProcessStatus.PROCESSING
                process.save()

                submit_task(process_id, extract_nodes, process)

                return Response(
                    {"status": ProcessStatus.PROCESSING, "message": "Process started"},
                    status=status.HTTP_202_ACCEPTED,
                )
            except Exception as e:
                import traceback

                logger.exception("Exception occurred while submitting node extraction task: %s", e, exc_info=True)
                process.status = ProcessStatus.FAILED
                process.error_message = traceback.format_exc()
                process.save()
                return Response(
                    {"status": ProcessStatus.FAILED, "message": "Node extraction failed"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        finally:
            connection.close()


@method_decorator(csrf_exempt, name="dispatch")
class GraphExtractView(APIView):
    def post(self, request):
        close_old_connections()
        try:
            from importing.serializers import GraphExtractSerializer

            raw_payload = request.data.get("payload")

            if raw_payload and isinstance(raw_payload, str):
                try:
                    raw_payload = json.loads(raw_payload)
                except json.JSONDecodeError:
                    raw_payload = {}
            elif not raw_payload:
                raw_payload = {}

            ser = GraphExtractSerializer(data=raw_payload)
            ser.is_valid(raise_exception=True)
            data = ser.validated_data

            process_id = data["process_id"]
            user_id = data["user_id"]
            nodes = data.get("nodes")
            callback_url = data.get("callback_url")

            try:
                process = ImportProcess.objects.get(process_id=process_id, user_id=user_id)
                process.error_message = None
                process.callback_url = callback_url
                process.save()
            except Exception as e:
                logger.exception("Process not found: %s", e, exc_info=True)
                return Response(
                    {"status": ProcessStatus.FAILED, "message": "Process not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            try:
                if process.status == ProcessStatus.PROCESSING:
                    return Response(
                        {"status": process.status, "message": "Not ready"},
                        status=status.HTTP_202_ACCEPTED,
                    )

                if nodes is not None:
                    process.nodes = nodes
                elif not process.nodes:
                    return Response(
                        {"status": ProcessStatus.FAILED, "message": "No nodes provided"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                process.status = ProcessStatus.PROCESSING
                process.save()

                submit_task(process_id, extract_relationships, process)

                return Response(
                    {"status": ProcessStatus.PROCESSING, "message": "Process started"},
                    status=status.HTTP_202_ACCEPTED,
                )
            except Exception as e:
                import traceback

                logger.exception("Exception occurred while submitting graph extraction task: %s", e, exc_info=True)
                process.status = ProcessStatus.FAILED
                process.error_message = traceback.format_exc()
                process.save()
                return Response(
                    {"status": ProcessStatus.FAILED, "message": "Graph extraction failed"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        finally:
            connection.close()


@method_decorator(csrf_exempt, name="dispatch")
class GraphImportView(APIView):
    def post(self, request):
        close_old_connections()
        try:
            from importing.serializers import GraphImportSerializer

            raw_payload = request.data.get("payload")

            if raw_payload and isinstance(raw_payload, str):
                try:
                    raw_payload = json.loads(raw_payload)
                except json.JSONDecodeError:
                    raw_payload = {}
            elif not raw_payload:
                raw_payload = {}

            ser = GraphImportSerializer(data=raw_payload)
            ser.is_valid(raise_exception=True)
            data = ser.validated_data

            process_id = data["process_id"]
            user_id = data["user_id"]
            graph = data.get("graph")
            callback_url = data.get("callback_url")

            try:
                process = ImportProcess.objects.get(process_id=process_id, user_id=user_id)
                process.error_message = None
                process.callback_url = callback_url
                process.save()
            except Exception as e:
                logger.exception("Process not found: %s", e, exc_info=True)
                return Response(
                    {"status": ProcessStatus.FAILED, "message": "Process not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            try:
                if process.status == ProcessStatus.PROCESSING:
                    return Response(
                        {"status": process.status, "message": "Not ready"},
                        status=status.HTTP_202_ACCEPTED,
                    )

                if graph is not None:
                    process.graph = graph
                elif not process.graph:
                    return Response(
                        {"status": ProcessStatus.FAILED, "message": "No graph provided"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                process.status = ProcessStatus.PROCESSING
                process.save()

                submit_task(
                    process_id,
                    import_graph,
                    process,
                    {"session": request.session.get("first_line")},
                )

                return Response(
                    {"status": ProcessStatus.PROCESSING, "message": "Process started"},
                    status=status.HTTP_202_ACCEPTED,
                )
            except Exception as e:
                import traceback

                logger.exception("Error during graph import task submission: %s", e, exc_info=True)
                process.status = ProcessStatus.FAILED
                process.error_message = traceback.format_exc()
                process.save()
                return Response(
                    {"status": ProcessStatus.FAILED, "message": "Graph import failed"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        finally:
            connection.close()


@method_decorator(csrf_exempt, name="dispatch")
class CancelTaskView(APIView):
    def patch(self, request):
        close_old_connections()
        try:
            user_id = request.query_params.get("user_id")
            process_id = request.query_params.get("process_id")

            if not user_id:
                return Response(
                    {"status": ProcessStatus.FAILED, "message": "No user id provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not process_id:
                return Response(
                    {"status": ProcessStatus.FAILED, "message": "No process id provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                process = get_object_or_404(ImportProcess, user_id=user_id, process_id=process_id)
            except Http404 as e:
                logger.exception("Process not found: %s", e, exc_info=True)
                return Response(
                    {"status": ProcessStatus.FAILED, "message": "Process not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            try:
                success = cancel_task(process_id)
                if success:
                    process.status = ProcessStatus.CANCELLED
                    process.save()
                    return Response(
                        {"status": ProcessStatus.CANCELLED, "message": "Task cancelled"},
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {"status": ProcessStatus.FAILED, "message": "Task not found or already completed"},
                        status=status.HTTP_404_NOT_FOUND,
                    )
            except Exception as e:
                import traceback

                logger.exception("Exception occurred while cancelling task: %s", e, exc_info=True)
                process.status = ProcessStatus.FAILED
                process.error_message = traceback.format_exc()
                process.save()
                return Response(
                    {"status": ProcessStatus.FAILED, "message": "Failed to cancel task"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        finally:
            connection.close()


@method_decorator(csrf_exempt, name="dispatch")
class ProcessReportView(APIView):
    def get(self, request):
        close_old_connections()
        try:
            user_id = request.query_params.get("user_id")
            process_id = request.query_params.get("process_id")
            key = request.query_params.get("key")

            if not user_id:
                return Response(
                    {"status": ProcessStatus.FAILED, "message": "No user_id provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not process_id:
                return Response(
                    {"status": ProcessStatus.FAILED, "message": "No process_id provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not key:
                return Response(
                    {"status": ProcessStatus.FAILED, "message": "No key provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                process = get_object_or_404(ImportProcess, user_id=user_id, process_id=process_id)
                process_status = process.status

                key_to_field_map = {
                    "labels": "labels",
                    "attributes": "attributes",
                    "nodes": "nodes",
                    "graph": "graph",
                    "import": "import",
                }

                if key not in key_to_field_map:
                    return Response(
                        {"status": ProcessStatus.FAILED, "message": "Invalid key provided"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                response_data = {
                    "status": process_status,
                    "message": process.error_message,
                }

                if key == "import":
                    return Response(response_data, status=status.HTTP_200_OK)

                data_field = key_to_field_map[key]
                data_value = getattr(process, data_field)
                data_available = data_value is not None

                if process_status == ProcessStatus.PROCESSING or not data_available:
                    response_data["message"] = "Data not available yet"
                    return Response(response_data, status=status.HTTP_200_OK)

                response_key = "graph" if key == "nodes" else key
                response_data[response_key] = data_value
                response_data["status"] = ProcessStatus.COMPLETED

                return Response(response_data, status=status.HTTP_200_OK)

            except Exception as e:
                logger.exception("Error during writing report: %s", e, exc_info=True)
                return Response(
                    {"status": ProcessStatus.FAILED, "message": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        finally:
            connection.close()


@method_decorator(csrf_exempt, name="dispatch")
class ProcessDeleteView(APIView):
    def delete(self, request):
        close_old_connections()
        try:
            user_id = request.query_params.get("user_id")
            process_id = request.query_params.get("process_id")

            if not user_id:
                return Response(
                    {"status": ProcessStatus.FAILED, "message": "No user_id provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not process_id:
                return Response(
                    {"status": ProcessStatus.FAILED, "message": "No process_id provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                process = get_object_or_404(ImportProcess, user_id=user_id, process_id=process_id)
                process.delete()

                return Response(
                    {"status": ProcessStatus.CANCELLED, "message": "Process deleted"},
                    status=status.HTTP_200_OK,
                )
            except Http404 as e:
                logger.exception("Process not found: %s", e, exc_info=True)
                return Response(
                    {"status": ProcessStatus.FAILED, "message": "Process not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            except Exception as e:
                logger.exception("Error during deleting process: %s", e, exc_info=True)
                return Response(
                    {"status": ProcessStatus.FAILED, "message": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        finally:
            connection.close()
