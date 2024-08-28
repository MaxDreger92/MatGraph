from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .fabricationworkflows import FabricationWorkflowMatcher
import json
from django.shortcuts import render

@csrf_exempt
def workflow_matcher(request):
    print("miau")

    if request.method == 'POST':
        
        data = json.loads(request.body)
        params = data["params"]
        graph = params["graph"]
        parsedGraph = json.loads(graph)

        matcher = FabricationWorkflowMatcher(parsedGraph, force_report=True)
        matcher.run()

        # Convert the DataFrame to CSV and create an HTTP response with it
        csv_content = matcher.result.to_csv(index=False)
        matcher.result.to_csv('output_filename.csv', index=False)
        response = HttpResponse(csv_content, content_type='text/csv',
                                headers = {'Content-Disposition': 'attachment; filename=workflows.csv'})
        return response
    else:
        return JsonResponse({'error': 'Only POST method is allowed.'}, status=405)




