import csv
import json
import math
import requests
from io import StringIO
import asyncio
import httpx
from concurrent.futures import ThreadPoolExecutor
import logging

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
from matgraph.models.metadata import File

executor = ThreadPoolExecutor()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


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

        data = {"csvTable": csv_table, "fileId": file_id}
        url = "http://localhost:8080/api/users/uploads/create"
        headers = {
            "Authorization": f"Bearer {user_token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                create_response = await client.post(url, headers=headers, json=data)
                create_response.raise_for_status()
            except httpx.RequestError as e:
                print(f"error: {e}")
                return response.Response(
                    {"error": "Failed to create upload process!"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        create_response_data = create_response.json()

        return JsonResponse(
            {
                "upload": create_response_data.get("upload"),
                "message": create_response_data.get(
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
        await sync_to_async(
            file_record.save
        )()  # Ensure the save method supports async if you use an async ORM
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

        # file_record = await sync_to_async(File.nodes.get)(uid=file_id)
        # file_obj_bytes = await sync_to_async(file_record.get_file)()
        # file_obj_str = file_obj_bytes.decode('utf-8')
        # file_obj = StringIO(file_obj_str)
        # file_obj.seek(0)
        # first_line = str(file_obj.readline().strip().lower())

        # cached = await sync_to_async(FullTableCache.fetch)(first_line)
        # if cached:
        #     cached = str(cached).replace("'", "\"")
        #     sanitized_cached = self.sanitize_data(cached)
        #     return response.Response({
        #         'graph_json': sanitized_cached,
        #         'file_id': file_id,
        #     })

        url = f"http://localhost:8080/api/users/uploads/{upload_id}"
        headers = {
            "Authorization": f"Bearer {user_token}",
            "Content-Type": "application/json",
        }
        updates = {"processing": True, "context": context}

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                update_response = await client.patch(url, headers=headers, json=updates)
                update_response.raise_for_status()
            except httpx.RequestError as e:
                logger.error(f"HTTP error during update: {e}")
                return response.Response(
                    {"error": "Failed to set upload to processing"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            response_data = update_response.json()
            if response_data.get("updateSuccess") is False:
                return JsonResponse({"processing": False})

        loop = asyncio.get_event_loop()
        loop.run_in_executor(
            executor, self.extract_labels, upload_id, context, file_id, user_token
        )

        return JsonResponse({"processing": True})

    def extract_labels(self, upload_id, context, file_id, user_token):
        asyncio.run(self.async_extract_labels(upload_id, context, file_id, user_token))

    async def async_extract_labels(self, upload_id, context, file_id, user_token):
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
            endpoint = f"http://localhost:8080/api/users/uploads/{upload_id}"
            headers = {
                "Authorization": f"Bearer {user_token}",
                "Content-Type": "application/json",
            }

            async with httpx.AsyncClient() as client:
                try:
                    response = await client.patch(
                        endpoint, headers=headers, json=updates
                    )
                    response.raise_for_status()
                except httpx.RequestError as e:
                    print(f"Error during HTTP PATCH request: {e}")
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

        url = f"http://localhost:8080/api/users/uploads/{upload_id}"
        headers = {
            "Authorization": f"Bearer {user_token}",
            "Content-Type": "application/json",
        }
        updates = {"processing": True, "context": context, "labelDict": labels_str}

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                update_response = await client.patch(url, headers=headers, json=updates)
                update_response.raise_for_status()
            except httpx.RequestError as e:
                logger.error(f"HTTP error during update: {e}")
                return response.Response(
                    {"error": "Failed to set upload to processing"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            response_data = update_response.json()
            if response_data.get("updateSuccess") is False:
                return JsonResponse({"processing": False})

        label_input = self.prepare_data(labels)

        loop = asyncio.get_event_loop()
        loop.run_in_executor(
            executor,
            self.extract_attributes,
            upload_id,
            context,
            file_id,
            user_token,
            label_input,
        )
        
        return JsonResponse({"processing": True})

    def extract_attributes(self, upload_id, context, file_id, user_token, label_input):
        asyncio.run(
            self.async_extract_attributes(
                upload_id, context, file_id, user_token, label_input
            )
        )

    async def async_extract_attributes(
        self, upload_id, context, file_id, user_token, label_input
    ):
        file_record = await sync_to_async(File.nodes.get)(uid=file_id)
        file_link = file_record.link
        file_name = file_record.name

        try:
            attribute_classifier = AttributeClassifier(
                label_input, context=context, file_link=file_link, file_name=file_name
            )
            await sync_to_async(attribute_classifier.run)()
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
            endpoint = f"http://localhost:8080/api/users/uploads/{upload_id}"
            headers = {
                "Authorization": f"Bearer {user_token}",
                "Content-Type": "application/json",
            }
            
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.patch(
                        endpoint, headers=headers, json=updates
                    )
                    response.raise_for_status()
                except httpx.RequestError as e:
                    print(f"Error during HTTP PATCH request: {e}")
        except Exception as e:
            print(f"Error during attribute extraction: {e}", exc_info=True)

    def prepare_data(self, labels):
        input_data = [
            {"column_values": value["1"], "header": key, "1_label": value["Label"]}
            for key, value in labels.items()
        ]
        for index, key in enumerate(input_data):
            key["index"] = index
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
            
        url = f"http://localhost:8080/api/users/uploads/{upload_id}"
        headers = {
            "Authorization": f"Bearer {user_token}",
            "Content-Type": "application/json",
        }
        updates = {"processing": True, "context": context, "attributeDict": attributes_str}

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                update_response = await client.patch(url, headers=headers, json=updates)
                update_response.raise_for_status()
            except httpx.RequestError as e:
                logger.error(f"HTTP error during update: {e}")
                return response.Response(
                    {"error": "Failed to set upload to processing"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            response_data = update_response.json()
            if response_data.get("updateSuccess") is False:
                return JsonResponse({"processing": False})

        attribute_input = await self.prepare_data(file_id, attributes)
        
        loop = asyncio.get_event_loop()
        loop.run_in_executor(
            executor,
            self.extract_nodes,
            upload_id,
            context,
            file_id,
            user_token,
            attribute_input,
        )
        
        return JsonResponse({"processing": True})

    def extract_nodes(self, upload_id, context, file_id, user_token, attribute_input):
        asyncio.run(
            self.async_extract_nodes(
                upload_id, context, file_id, user_token, attribute_input
            )
        )
    
    async def async_extract_nodes(self, upload_id, context, file_id, user_token, attribute_input):
        file_record = await sync_to_async(File.nodes.get)(uid=file_id)
        file_link = file_record.link
        file_name = file_record.name
        
        try:
            node_extractor = NodeExtractor(
                context=context,
                file_link=file_link,
                file_name=file_name,
                data=attribute_input,
            )
            await sync_to_async(node_extractor.run)()
            nodes = str(node_extractor.results).replace("'", '"')
            nodes_str = json.dumps(nodes)
            
            updates = {
                "workflow": nodes_str,
                "progress": 4,
                "processing": False,
            }
            endpoint = f"http://localhost:8080/api/users/uploads/{upload_id}"
            headers = {
                "Authorization": f"Bearer {user_token}",
                "Content-Type": "application/json",
            }
            
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.patch(
                        endpoint, headers=headers, json=updates
                    )
                    response.raise_for_status()
                except httpx.RequestError as e:
                    print(f"Error during HTTP PATCH request: {e}")
        except Exception as e:
            print(f"Error during attribute extraction: {e}", exc_info=True)

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
                "1_label": attributes[header]["Label"],
                "1_attribute": attributes[header]["Attribute"],
            }
            for i, header in enumerate(first_line)
        ]
        return input


@method_decorator(csrf_exempt, name="dispatch")
class GraphExtractView(APIView):

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        node_json = data["params"]["node_json"]
        context = data["params"]["context"]
        file_link = data["params"]["file_link"]
        file_name = data["params"]["file_name"]

        required_fields = ["node_json", "context", "file_link", "file_name"]
        if not all(field in data["params"] for field in required_fields):
            return response.Response(
                {"error": "Missing required data"}, status=status.HTTP_400_BAD_REQUEST
            )
        header, first_row = self.prepare_data(file_link)
        graph = self.extract_relationships(node_json, context, header, first_row)
        graph = (
            str(graph)
            .replace("'", '"')
            .replace("has_manufacturing_output", "is_manufacturing_output")
        )
        return response.Response({"graph_json": graph})

    def prepare_data(self, file_link):
        file = File.nodes.get(link=file_link)
        file_obj_bytes = file.get_file()

        # Decode the bytes object to a string
        file_obj_str = file_obj_bytes.decode("utf-8")

        # Use StringIO on the decoded string
        file_obj = StringIO(file_obj_str)
        csv_reader = csv.reader(file_obj)
        header = next(csv_reader)
        first_row = next(csv_reader)

        return header, first_row

    def extract_relationships(self, nodes, context, header, first_row):
        relationships_extractor = fullRelationshipsExtractor(
            nodes, context, header, first_row
        )
        relationships_extractor.run()
        relationships = relationships_extractor.results
        return relationships


@method_decorator(csrf_exempt, name="dispatch")
class GraphImportView(APIView):

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        print("GraphImporter")
        data = json.loads(request.body)
        graph = json.loads(data["params"]["graph_json"])
        file_link = data["params"]["file_link"]
        file_name = data["params"]["file_name"]
        context = data["params"]["context"]

        required_fields = ["graph_json", "file_link"]
        if not all(field in data["params"] for field in required_fields):
            return response.Response(
                {"error": "Missing required data"}, status=status.HTTP_400_BAD_REQUEST
            )

        self.import_graph(file_link, graph, context)
        FullTableCache.update(self.request.session.get("first_line"), graph)
        return response.Response(
            {"success": True, "message": "Graph imported successfully"}
        )

    def import_graph(self, file_link, graph, context):
        importer = TableImporter(graph, file_link, context)
        importer.run()
