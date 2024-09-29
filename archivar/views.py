from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from archivar.archivar import ExperimentImporter


class ExperimentImportView(APIView):
    def post(self, request, format=None):
        json_data = request.data
        importer = ExperimentImporter()
        try:
            exp = importer.import_experiment(json_data)
            return Response({'status': 'success', 'experiment_uid': exp.uid}, status=status.HTTP_201_CREATED)
        except Exception as e:
            # Log the exception as needed
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
