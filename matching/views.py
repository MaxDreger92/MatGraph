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
        
        if "graph" not in request.POST:
            return Response(
                {"error": "No graph provided"}, status=status.HTTP_400_BAD_REQUEST
            )
            
        graph = request.POST["graph"]
        graph = json.loads(graph)

        matcher = FabricationWorkflowMatcher(graph, force_report=True)
        matcher.run()
        
        csv_content = matcher.result.to_csv(index=False)
        # matcher.result.to_csv('output_filename.csv', index=False)
        
        response = HttpResponse(csv_content, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="workflows.csv"'
        return response




