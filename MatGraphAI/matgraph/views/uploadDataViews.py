from datetime import date
from http.client import HTTPResponse
import magic
import requests
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from rest_framework import views, status, parsers
from rest_framework.response import Response

from graphutils.models import UploadedFile
from importing.importer import TableImporter, TableTransformer
from matgraph.serializers import UploadedFileSerializer

import os

import pandas as pd
from neomodel import db
from fuzzywuzzy import process
from matgraph.models.metadata import *  # Import your models here
from django.shortcuts import render, redirect
from matgraph.importer.import_pubchem_json import IMPORT_PUBCHEM


def upload_success(request):
    return render(request, 'upload_success.html')


@login_required
def create_file_node(uid, file_name, file_path):
    """
    Create a new node in the database representing a file.

    :param uid: The unique ID of the file.
    :param file_name: The name of the file.
    :param file_path: The path of the file in local storage.
    """
    print("create file node")

    db.cypher_query("CREATE (f:File {uid: $uid, file_name: $file_name, file_path: $file_path})",
                    {"uid": uid, "file_name": file_name, "file_path": file_path})


# @login_required
# def file_upload_form(request):
#     """
#     A Django view for rendering the file upload form and handling file uploads.
#
#     :param request: The HTTP request object.
#     :return: The rendered file upload form or the JSON response after processing a file upload.
#     """
#     print("file upload form")
#
#     if request.method == 'POST':
#         file_upload_view = FileUploadView.as_view()
#         response = file_upload_view(request)
#
#         if response.status_code == 201:
#             # Redirect the user to the success page
#             return HttpResponseRedirect(response.data['redirect_url'])
#         else:
#             return JsonResponse(response.data, status=response.status_code)
#
#     return render(request, 'file_upload_form.html')


class FileUploadView(views.APIView):
    """
    A Django view for handling file uploads.
    This view receives a file uploaded by the user, saves it locally,
    and uploads it to a remote server.
    """
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)

    def post(self, request):
        """Handle POST request to upload a file."""
        # Retrieve the uploaded file from the request
        file_obj = request.FILES['file']
        file_name = file_obj.name



        # Upload the file to the remote server
        file_obj.seek(0)  # Reset file pointer
        remote_upload_response = self.upload_to_remote_server(file_name, file_obj)


        if remote_upload_response.status_code == 200:
            # Parse response and save file record

            self.handle_successful_upload(remote_upload_response, file_name, request)
            return Response({'success': True}, status=status.HTTP_201_CREATED)
        else:
            return Response(self.parse_error(remote_upload_response), status=remote_upload_response.status_code)

    def upload_to_remote_server(self, file_name, file_obj):
        """Upload the file to a remote server and return the response."""
        url = f"http://134.94.199.40/{file_name}"
        payload = {'user': 'TLxtWQZbhc', 'password': '50PVZNIO5Q'}
        files = [('files', (file_name, file_obj.read()))]
        headers = {'Accept': '*/*'}
        return requests.post(url, headers=headers, data=payload, files=files)

    def handle_successful_upload(self, response, file_name, request):
        """Handle actions to be taken after successful file upload."""
        # Extract information from the response
        resp_data = response.json()
        file_link = f"http://134.94.199.40/neo4j/{resp_data['filename'][0]}"
        file_id = resp_data['id']

        # Retrieve additional information from the request
        context = request.POST.get('data_context', '')
        file_format = request.FILES['file'].content_type
        file_obj = request.FILES['file']

        # Save the uploaded file information in the database
        File(
            name=file_name,
            date_added=date.today(),
            uid=file_id,
            link=file_link,
            context=context,
            format=file_format
        ).save()
        print("file saved", file_format)
        if file_format == "text/csv":

            table_transformer = TableTransformer(file_obj, {"context": context, 'file_link': file_link, 'file_name': file_name})
            table_transformer.create_data()
            table_transformer.classify_node_labels()
            table_transformer.classify_attributes()
            table_transformer.create_node_list()

    def parse_error(self, response):
        """Parse error message from the response."""
        try:
            return response.json()
        except ValueError:
            return {'error': 'Invalid JSON response from the file server'}

def map_measurement_data(csv_data):
    # Implement your mapping logic for measurement data here
    return csv_data


def map_materials_data(csv_data):
    # Implement your mapping logic for materials data here
    return csv_data


def map_simulation_data(csv_data):
    # Implement your mapping logic for simulation data here
    return csv_data


def map_fabrication_data(csv_data):
    # Implement your mapping logic for fabrication data here
    return csv_data


def map_metadata(csv_data):
    # Implement your mapping logic for fabrication data here
    return csv_data


def find_best_match(name, choices):
    best_match, score = process.extractOne(name, choices)
    if score > 80:  # Adjust the threshold based on your requirements
        return best_match
    else:
        raise ValueError(f"No match found for '{name}'")


# Import your models here


DATA_TYPE_MAPPING = {
    'measurement': map_measurement_data,
    'materials': map_materials_data,
    'simulation': map_simulation_data,
    'fabrication': map_fabrication_data,
    'metadata': map_metadata
}


@login_required
def map_csv_data_to_graph(csv_data, data_type, header):
    """Analyze and map the CSV data to the graph database schema.

    Args:
        csv_data: A list of dictionaries representing the data from the CSV file.
        data_type: A string representing the selected data type.

    Returns:
        A list of dictionaries with the mapped data.
    """
    if data_type in DATA_TYPE_MAPPING:
        mapping_function = DATA_TYPE_MAPPING[data_type]
        mapped_data = mapping_function(csv_data, header)
        return str(mapped_data)
    else:
        raise ValueError(f"Unsupported data type: {data_type}")


@login_required
def upload_csv(request):
    if request.method == 'POST':
        # Get the uploaded CSV file and the selected data type
        csv_file = request.FILES['file']
        data_type = request.POST['data_type']

        # Parse the CSV data into a Pandas DataFrame
        data = pd.read_csv(csv_file)

        # Analyze and map the CSV data to the graph database schema
        mapped_data = map_csv_data_to_graph(data, data_type, data.columns)

        # Insert the mapped data into Neo4j using the appropriate Cypher query
        cypher_query = IMPORT_PUBCHEM.replace('$data', mapped_data)
        # print(cypher_query)
        db.cypher_query(cypher_query)

        # Save the uploaded CSV file to the server's media directory
        csv_file_name = csv_file.name
        csv_file_path = os.path.join('/home/mdreger/Documents/data/backup', csv_file_name)
        with open(csv_file_path, 'wb+') as destination:
            for chunk in csv_file.chunks():
                destination.write(chunk)

        # Pass the results to the results view function
        return render(request, 'results.html', {'data': json_data})
    else:
        # Render the upload form
        return render(request, 'upload.html')
