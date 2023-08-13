from datetime import date

import requests
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from rest_framework import views, status, parsers
from rest_framework.response import Response

from matgraph.serializers import UploadedFileSerializer

import os

import pandas as pd
from neomodel import db
from fuzzywuzzy import process
from matgraph.models.metadata import *  # Import your models here
from django.shortcuts import render
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
    db.cypher_query("CREATE (f:File {uid: $uid, file_name: $file_name, file_path: $file_path})",
                    {"uid": uid, "file_name": file_name, "file_path": file_path})


@login_required
def file_upload_form(request):
    """
    A Django view for rendering the file upload form and handling file uploads.

    :param request: The HTTP request object.
    :return: The rendered file upload form or the JSON response after processing a file upload.
    """

    if request.method == 'POST':
        file_upload_view = FileUploadView.as_view()
        response = file_upload_view(request)

        if response.status_code == 201:
            # Redirect the user to the success page
            return HttpResponseRedirect(response.data['redirect_url'])
        else:
            return JsonResponse(response.data, status=response.status_code)

    return render(request, 'file_upload_form.html')


@login_required
class FileUploadView(views.APIView):
    """
    A Django view that receives a file uploaded by the user, saves it locally,
    and uploads it to a remote server.
    """
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)

    def post(self, request):
        # Retrieve the uploaded file from the request
        file_obj = request.FILES['file']
        file_name = file_obj.name
        # Save the uploaded file to local storage
        file_path = default_storage.save(file_name, file_obj)

        # Construct the remote URL using the file_name
        url = f"http://134.94.199.40/{file_name}"

        # Define payload and headers for the request
        payload = {'user': 'TLxtWQZbhc', 'password': '50PVZNIO5Q'}

        # Reset the file pointer to the beginning of the file
        file_obj.seek(0)

        # Prepare the files dictionary for the request
        files = [
            ('files', (file_name, file_obj.read()))
        ]
        headers = {
            'Accept': '*/*'
        }

        # Make the POST request to the remote server to upload the file
        response = requests.request("POST", url, headers=headers, data=payload, files=files)

        today = date.today()
        file_id = response.json()['id']

        # Save the uploaded file information in the database
        uploaded_file = File(name=file_name, date_added=today, path=file_path, uid=file_id)
        uploaded_file.save()
        if response.status_code == 200:
            create_file_node(uploaded_file.id, file_name, file_path)
            serializer = UploadedFileSerializer(uploaded_file)
            return Response({'success': True, 'redirect_url': reverse('upload_success')},
                            status=status.HTTP_201_CREATED)
        else:
            try:
                json_data = response.json()
            except ValueError:
                json_data = {'error': 'Invalid JSON response from the file server'}

            return Response(json_data, status=response.status_code)


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
