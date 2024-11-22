import os
import tempfile
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import ExcelUploadForm
from .csv_split import load_and_split_file  # Import your csv_split function here
import pandas as pd

from .ingestionquery import ingest_data


def upload_file(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']

            # Create a temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = os.path.join(temp_dir, file.name)

                # Save the uploaded file to the temporary directory
                with open(temp_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

                # Process the file with csv_split
                load_and_split_file(temp_path)
                ingest_data(temp_path)

                # Respond with success or list of generated files
                return HttpResponse("File processed and CSVs stored.")
    else:
        form = ExcelUploadForm()
    return render(request, 'schema_ingestion/upload.html', {'form': form})
