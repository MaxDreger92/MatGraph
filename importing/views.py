import csv
import json
import math
import requests
from io import StringIO
import asyncio
import httpx
from concurrent.futures import ThreadPoolExecutor

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from neomodel import DateTimeProperty
from rest_framework import response, status
from rest_framework.views import APIView
from django.http import JsonResponse
from asgiref.sync import sync_to_async, async_to_sync

from importing.NodeAttributeExtraction.attributeClassifier import AttributeClassifier
from importing.NodeExtraction.nodeExtractor import NodeExtractor
from importing.NodeLabelClassification.labelClassifier import NodeClassifier
from importing.RelationshipExtraction.completeRelExtractor import (
    fullRelationshipsExtractor,
)
from importing.importer import TableImporter
from importing.models import FullTableCache
from importing.utils.user_db_requests import user_db_request
from matgraph.models.metadata import File

from .task_manager import submit_task, cancel_task


@method_decorator(csrf_exempt, name="dispatch")
class FileImportView(APIView):
    def post(self, request):
        return async_to_sync(self.handle_post)(request)

    async def handle_post(self, request):
        if "file" not in request.FILES:
            return response.Response(
                {"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "csvTable" not in request.POST:
            return response.Response(
                {"error": "No CSV Table provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        csv_table = request.POST["csvTable"]
        user_token = request.user_token

        file_obj = request.FILES["file"]
        if not file_obj.name.endswith(".csv"):
            return response.Response(
                {"error": "Invalid file type"}, status=status.HTTP_400_BAD_REQUEST
            )
        file_record = await self.store_file(file_obj)
        file_id = file_record.uid

        request_data = {
            "csvTable": csv_table,
            "fileId": file_id,
            "fileName": file_obj.name,
        }
        response_data = await user_db_request(request_data, None, user_token, "post")

        return JsonResponse(
            {
                "upload": response_data.get("upload"),
                "message": response_data.get(
                    "message", "Upload process saved successfully!"
                ),
            }
        )

    async def store_file(self, file_obj):
        """Store the uploaded file and return the file record."""
        file_name = file_obj.name
        file_record = File(
            name=file_name, date_added=DateTimeProperty(default_now=True)
        )
        file_record.file = file_obj
        await sync_to_async(file_record.save)()
        return file_record


@method_decorator(csrf_exempt, name="dispatch")
class LabelExtractView(APIView):

    def post(self, request):
        return async_to_sync(self.handle_post)(request)

    async def handle_post(self, request, *args, **kwargs):
        user_token = request.user_token
        data = json.loads(request.body)
        params = data["params"]

        upload_id = params["uploadId"]
        context = params["context"]
        file_id = params["fileId"]

        cached = await self.try_cache(upload_id, user_token, file_id)
        if cached:
            return JsonResponse({"cached": True})

        updates = {"processing": True, "context": context}
        response_data = await user_db_request(updates, upload_id, user_token)
        if response_data.get("updateSuccess") is False:
            return JsonResponse({"processing": False})

        submit_task(
            upload_id, self.extract_labels, upload_id, context, file_id, user_token
        )

        return JsonResponse({"processing": True})

    def extract_labels(self, task, upload_id, context, file_id, user_token):
        asyncio.run(
            self.async_extract_labels(task, upload_id, context, file_id, user_token)
        )

    async def async_extract_labels(self, task, upload_id, context, file_id, user_token):
        file_record = await sync_to_async(File.nodes.get)(uid=file_id)
        file_obj_bytes = await sync_to_async(file_record.get_file)()
        file_obj_str = file_obj_bytes.decode("utf-8")
        file_obj = StringIO(file_obj_str)

        try:
            node_classifier = NodeClassifier(
                data=file_obj,
                context=context,
                file_link=file_record.link,
                file_name=file_record.name,
            )
            await sync_to_async(node_classifier.run)()

            if task.is_cancelled():
                return

            labels = {
                element["header"]: [element["1_label"], element["column_values"][0]]
                for element in node_classifier.results
            }
            sanitized_labels = self.sanitize_data(labels)
            sanitized_labels_str = json.dumps(sanitized_labels)

            updates = {
                "labelDict": sanitized_labels_str,
                "progress": 2,
                "processing": False,
            }
            await user_db_request(updates, upload_id, user_token)
        except Exception as e:
            print(f"Error during label extraction: {e}", exc_info=True)
            raise

    def sanitize_data(self, data):
        if isinstance(data, dict):
            i = 0
            sanitized_dict = {}
            for k, v in data.items():
                i += 1
                if isinstance(k, float) and (math.isnan(k) or math.isinf(k)):
                    k = f"column_{str(i)}"  # Use an appropriate placeholder
                sanitized_dict[k] = self.sanitize_data(v)
            return sanitized_dict
        elif isinstance(data, list):
            return [self.sanitize_data(i) for i in data]
        elif isinstance(data, float):
            if math.isinf(data) or math.isnan(data):
                return None  # or some other appropriate value
            return data
        return data

    async def try_cache(self, upload_id, user_token, file_id):
        file_record = await sync_to_async(File.nodes.get)(uid=file_id)
        file_obj_bytes = await sync_to_async(file_record.get_file)()
        file_obj_str = file_obj_bytes.decode("utf-8")
        file_obj = StringIO(file_obj_str)
        file_obj.seek(0)
        first_line = str(file_obj.readline().strip().lower())

        cached = await sync_to_async(FullTableCache.fetch)(first_line)
        if cached:
            cached = str(cached).replace("'", '"')
            sanitized_cached = self.sanitize_data(cached)
            sanitized_cached_str = json.dumps(sanitized_cached)

            updates = {
                "processing": False,
                "graph": sanitized_cached_str,
                "progress": 6,
            }
            await user_db_request(updates, upload_id, user_token)
            return True
        return False


@method_decorator(csrf_exempt, name="dispatch")
class AttributeExtractView(APIView):

    def post(self, request):
        return async_to_sync(self.handle_post)(request)

    async def handle_post(self, request, *args, **kwargs):
        user_token = request.user_token
        data = json.loads(request.body)
        params = data["params"]

        upload_id = params["uploadId"]
        context = params["context"]
        file_id = params["fileId"]
        labels = params["labelDict"]
        labels_str = json.dumps(labels)

        if not upload_id or not context or not file_id or not labels:
            return response.Response(
                {"error": "Missing params"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updates = {"processing": True, "context": context, "labelDict": labels_str}

        response_data = await user_db_request(updates, upload_id, user_token)
        if response_data.get("updateSuccess") is False:
            return JsonResponse({"processing": False})

        label_input = self.prepare_data(labels)

        submit_task(
            upload_id,
            self.extract_attributes,
            upload_id,
            context,
            file_id,
            user_token,
            label_input,
        )

        return JsonResponse({"processing": True})

    def extract_attributes(
        self, task, upload_id, context, file_id, user_token, label_input
    ):
        asyncio.run(
            self.async_extract_attributes(
                task, upload_id, context, file_id, user_token, label_input
            )
        )

    async def async_extract_attributes(
        self, task, upload_id, context, file_id, user_token, label_input
    ):
        try:
            file_record = await sync_to_async(File.nodes.get)(uid=file_id)
            file_link = file_record.link
            file_name = file_record.name

            attribute_classifier = AttributeClassifier(
                label_input, context=context, file_link=file_link, file_name=file_name
            )
            await sync_to_async(attribute_classifier.run)()

            if task.is_cancelled():
                return

            attributes = {
                element["header"]: {
                    "Label": element["1_label"],
                    "Attribute": element["1_attribute"],
                }
                for element in attribute_classifier.results
            }
            attributes_str = json.dumps(attributes)

            updates = {
                "attributeDict": attributes_str,
                "progress": 3,
                "processing": False,
            }
            await user_db_request(updates, upload_id, user_token)
        except Exception as e:
            print(f"Error during attribute extraction: {e}", exc_info=True)

    def prepare_data(self, labels):
        input_data = [
            {"column_values": [value[1]], "header": key, "1_label": value[0]}
            for key, value in labels.items()
        ]
        for index, item in enumerate(input_data):
            item["index"] = index
        return input_data

    ATTRIBUTE_MAPPER = {
        "Matter": ["name", "ratio", "concentration", "batch_number", "identifier"],
        "Parameter": ["value", "unit", "average", "std", "error"],
        "Measurement": ["name", "identifier"],
        "Manufacturing": ["name", "identifier"],
        "Metadata": ["name", "identifier"],
    }


@method_decorator(csrf_exempt, name="dispatch")
class NodeExtractView(APIView):

    def post(self, request):
        return async_to_sync(self.handle_post)(request)

    async def handle_post(self, request):
        user_token = request.user_token
        data = json.loads(request.body)
        params = data["params"]

        upload_id = params["uploadId"]
        context = params["context"]
        file_id = params["fileId"]
        attributes = params["attributeDict"]
        attributes_str = json.dumps(attributes)

        if not upload_id or not context or not file_id or not attributes:
            return response.Response(
                {"error:" "Missing params"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updates = {
            "processing": True,
            "context": context,
            "attributeDict": attributes_str,
        }
        response_data = await user_db_request(updates, upload_id, user_token)
        if response_data.get("updateSuccess") is False:
            return JsonResponse({"processing": False})

        attribute_input = await self.prepare_data(file_id, attributes)

        submit_task(
            upload_id,
            self.extract_nodes,
            upload_id,
            context,
            file_id,
            user_token,
            attribute_input,
        )

        return JsonResponse({"processing": True})

    def extract_nodes(
        self, task, upload_id, context, file_id, user_token, attribute_input
    ):
        asyncio.run(
            self.async_extract_nodes(
                task, upload_id, context, file_id, user_token, attribute_input
            )
        )

    async def async_extract_nodes(
        self, task, upload_id, context, file_id, user_token, attribute_input
    ):
        try:
            file_record = await sync_to_async(File.nodes.get)(uid=file_id)
            file_link = file_record.link
            file_name = file_record.name

            node_extractor = NodeExtractor(
                context=context,
                file_link=file_link,
                file_name=file_name,
                data=attribute_input,
            )
            await sync_to_async(node_extractor.run)()

            if task.is_cancelled():
                return

            graph = str(node_extractor.results).replace("'", '"')
            graph_str = json.dumps(graph)

            updates = {
                "graph": graph_str,
                "progress": 4,
                "processing": False,
            }
            await user_db_request(updates, upload_id, user_token)
        except Exception as e:
            print(f"Error during node extraction: {e}", exc_info=True)

    async def prepare_data(self, file_id, attributes):
        file_record = await sync_to_async(File.nodes.get)(uid=file_id)
        file_obj_bytes = await sync_to_async(file_record.get_file)()
        file_obj_str = file_obj_bytes.decode("utf-8")
        file_obj = StringIO(file_obj_str)
        csv_reader = csv.reader(file_obj)

        first_row = next(csv_reader)
        column_values = [[] for _ in range(len(first_row))]

        for row in csv_reader:
            for i, value in enumerate(row):
                if value != "" and len(column_values[i]) < 4:
                    column_values[i].append(value)

        file_obj.seek(0)

        first_line = file_obj.readline().strip()
        first_line = first_line.split(",")
        input = [
            {
                "index": i,
                "column_values": column_values[i],
                "header": header,
                "1_label": attributes[header][0],
                "1_attribute": attributes[header][1],
            }
            for i, header in enumerate(first_line)
        ]
        return input


@method_decorator(csrf_exempt, name="dispatch")
class GraphExtractView(APIView):

    def post(self, request):
        return async_to_sync(self.handle_post)(request)

    async def handle_post(self, request):
        user_token = request.user_token
        data = json.loads(request.body)
        params = data["params"]

        upload_id = params["uploadId"]
        context = params["context"]
        file_id = params["fileId"]
        graph = params["graph"]
        graph_str = json.dumps(graph)

        if not upload_id or not context or not file_id or not graph:
            return response.Response(
                {"error:" "Missing params"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updates = {"processing": True, "context": context, "graph": graph_str}
        response_data = await user_db_request(updates, upload_id, user_token)
        if response_data.get("updateSuccess") is False:
            return JsonResponse({"processing": False})

        header, first_row = await self.prepare_data(file_id)

        submit_task(
            upload_id,
            self.extract_relationships,
            upload_id,
            context,
            user_token,
            graph,
            header,
            first_row,
        )

        return JsonResponse({"processing": True})

    def extract_relationships(
        self, task, upload_id, context, user_token, graph, header, first_row
    ):
        asyncio.run(
            self.async_extract_relationships(
                task, upload_id, context, user_token, graph, header, first_row
            )
        )

    async def async_extract_relationships(
        self, task, upload_id, context, user_token, graph, header, first_row
    ):
        try:
            relationships_extractor = fullRelationshipsExtractor(
                graph, context, header, first_row
            )
            await sync_to_async(relationships_extractor.run)()

            if task.is_cancelled():
                return

            graph = relationships_extractor.results
            graph = (
                str(graph)
                .replace("'", '"')
                .replace("has_manufacturing_output", "is_manufacturing_output")
            )
            graph_str = json.dumps(graph)

            updates = {
                "graph": graph_str,
                "progress": 5,
                "processing": False,
            }
            await user_db_request(updates, upload_id, user_token)
        except Exception as e:
            print(f"Error during relationship extraction: {e}", exc_info=True)

    async def prepare_data(self, file_id):
        file_record = await sync_to_async(File.nodes.get)(uid=file_id)
        file_obj_bytes = await sync_to_async(file_record.get_file)()
        file_obj_str = file_obj_bytes.decode("utf-8")
        file_obj = StringIO(file_obj_str)
        csv_reader = csv.reader(file_obj)

        header = next(csv_reader)
        first_row = next(csv_reader)

        return header, first_row


@method_decorator(csrf_exempt, name="dispatch")
class GraphImportView(APIView):

    def post(self, request):
        return async_to_sync(self.handle_post)(request)

    async def handle_post(self, request):
        user_token = request.user_token
        data = json.loads(request.body)
        params = data["params"]

        upload_id = params["uploadId"]
        context = params["context"]
        file_id = params["fileId"]
        graph = params["graph"]
        graph_str = json.dumps(graph)

        if not upload_id or not context or not file_id or not graph:
            return response.Response(
                {"error:" "Missing params"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updates = {"processing": True, "context": context, "graph": graph_str}
        response_data = await user_db_request(updates, upload_id, user_token)
        if response_data.get("updateSuccess") is False:
            return JsonResponse({"processing": False})

        submit_task(
            upload_id,
            self.import_graph,
            upload_id,
            context,
            file_id,
            user_token,
            graph,
        )

        return JsonResponse({"processing": True})

    def import_graph(self, task, upload_id, context, file_id, user_token, graph):
        asyncio.run(
            self.async_import_graph(
                task, upload_id, context, file_id, user_token, graph
            )
        )

    async def async_import_graph(
        self, task, upload_id, context, file_id, user_token, graph
    ):
        try:
            file_record = await sync_to_async(File.nodes.get)(uid=file_id)
            file_link = file_record.link
            importer = TableImporter(graph, file_link, context)
            importer.run()

            if task.is_cancelled():
                return

            FullTableCache.update(self.request.session.get("first_line"), graph)

            updates = {
                "progress": 6,
                "processing": False,
            }
            await user_db_request(updates, upload_id, user_token)
        except Exception as e:
            print(f"Error during graph import: {e}", exc_info=True)


@method_decorator(csrf_exempt, name="dispatch")
class CancelTaskView(APIView):

    def post(self, request):
        return async_to_sync(self.handle_post)(request)

    async def handle_post(self, request):
        try:
            user_token = request.user_token
            data = json.loads(request.body)
            params = data.get("params", {})
            upload_id = params.get("uploadId")

            if not upload_id:
                return JsonResponse(
                    {"cancelled": False, "error": "uploadId is required"}, status=400
                )

            success = cancel_task(upload_id)
            updates = {"processing": False}
            await user_db_request(updates, upload_id, user_token)
            if success:

                return JsonResponse({"cancelled": True})
            else:
                return JsonResponse(
                    {
                        "cancelled": False,
                        "error": "Task not found or already completed",
                    },
                    status=404,
                )
        except Exception as e:
            return JsonResponse({"cancelled": False, "error": str(e)}, status=500)
