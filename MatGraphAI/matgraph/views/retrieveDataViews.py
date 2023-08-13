from django.http import FileResponse
from django.shortcuts import render
from neomodel import db
from rest_framework import views
import requests
from wsgiref.util import FileWrapper
import re
import csv
from collections import defaultdict
from django.http import HttpResponse, JsonResponse


from django.contrib.auth.decorators import login_required

@login_required
def download_data_form(request, PID):
    return render(request, 'PIDA.html', {'PID': PID})



@login_required
def download_data(request, PID):
    # Connect to Neo4j database

    # Query to fetch data by PID and include relationships between connected nodes
    query = '''
    MATCH (n:PIDA {pida: $PID})-[:CONTAINS]->(connected_nodes)
    WITH connected_nodes, labels(connected_nodes) as node_labels, properties(connected_nodes) as node_properties
    OPTIONAL MATCH (connected_nodes)-[r]-()
    WITH connected_nodes, node_labels, node_properties, type(r) as rel_type, properties(r) as rel_properties
    UNWIND node_labels as label
    RETURN label, node_properties, rel_type, rel_properties
    ORDER BY label
    '''

    # Execute query and fetch data
    results = db.cypher_query(query, {'PID': PID})
    print(results)

    # Choose output format: 'csv' or 'json'
    output_format = request.GET.get('format', 'csv').lower()

    # Process the results into a nested dictionary
    data = []
    for row in results[0]:
        node_label = row[0]
        node_properties = row[1]
        rel_type = row[2]
        rel_properties = row[3]

        record = defaultdict(lambda: defaultdict(str))

        for key, value in node_properties.items():
            record[node_label][key] = value

        if rel_type and rel_properties:
            for key, value in rel_properties.items():
                record[f"{node_label}_{rel_type}"][key] = value

        data.append(record)

    # Get all unique fieldnames
    fieldnames = set()
    for record in data:
        for primary_label, properties in record.items():
            for key in properties.keys():
                fieldnames.add((primary_label, key))

    # Sort fieldnames for consistency
    fieldnames = sorted(fieldnames)

    if output_format == 'csv':
        # Prepare CSV file
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="data_{PID}.csv"'

        writer = csv.writer(response)

        # Write primary header
        primary_header = [primary_label for primary_label, _ in fieldnames]
        writer.writerow(primary_header)

        # Write secondary header
        secondary_header = [key for _, key in fieldnames]
        writer.writerow(secondary_header)

        # Write data rows
        for record in data:
            row = []
            for primary_label, key in fieldnames:
                row.append(record[primary_label][key])
            writer.writerow(row)

        return response
    elif output_format == 'json':
        # Prepare JSON file
        json_data = []

        for record in data:
            json_row = defaultdict(str)
            for primary_label, properties in record.items():
                for key, value in properties.items():
                    json_row[f"{primary_label}_{key}"] = value
            json_data.append(json_row)

        response = JsonResponse(json_data, safe=False)
        response['Content-Disposition'] = f'attachment; filename="data_{PID}.json"'
        return response
    else:
        # Return an error response for invalid formats
        return HttpResponse("Invalid format. Supported formats: 'csv' and 'json'.", status=400)


class FileRetrieveView(views.APIView):
    """
    A Django view that retrieves a file from a remote server and serves it
    as a download to the user.
    """

    @login_required
    def get(self, request, uid, *args, **kwargs):
        # Construct the remote URL using the given uid
        url = f"http://134.94.199.40/{uid}"
        # Define payload and headers for the request
        payload = 'user=TLxtWQZbhc&password=50PVZNIO5Q'
        headers = {
            'Accept': '*/*',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        # Make the GET request to the remote server with stream=True to download the file
        response = requests.get(url, headers=headers, data=payload, stream=True)

        # Extract the filename from the Content-Disposition header
        content_disposition = response.headers.get('Content-Disposition')
        match = re.search(r'filename="(.+)"', content_disposition)
        filename = match.group(1) if match else 'download.bin'

        # Create an HttpResponse object with the content and content type from the external response
        django_response = FileResponse(
            FileWrapper(response.raw),
            content_type=response.headers.get('Content-Type')
        )

        # Set the Content-Disposition header to trigger a download with the extracted filename
        django_response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return django_response
