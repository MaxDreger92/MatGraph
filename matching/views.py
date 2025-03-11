from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .fabricationworkflows import FabricationWorkflowMatcher
import json
from django.shortcuts import render

@method_decorator(csrf_exempt, name="dispatch")
class WorkflowMatcher(APIView):
    def post(self, request):
        print("Raw request body:", request.body)  # Debugging
        try:
            data = json.loads(request.body.decode("utf-8"))  # Load JSON from request body
        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)

        print("Parsed JSON data:", data)  # Debugging

        if "graph" not in data:
            return Response({"error": "No graph provided"}, status=status.HTTP_400_BAD_REQUEST)

        graph = data["graph"]
        print("Extracted graph:", graph)  # Debugging

        matcher = FabricationWorkflowMatcher(graph, force_report=True)
        matcher.run()

        csv_content = matcher.result.to_csv(index=False)

        response = HttpResponse(csv_content, content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="workflows.csv"'
        return response


