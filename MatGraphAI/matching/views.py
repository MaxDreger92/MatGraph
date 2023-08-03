from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .fabricationworkflows import FabricationWorkflowMatcher
import json
from django.shortcuts import render

@csrf_exempt  # This decorator allows for POST requests from all origins, not recommended in production environment.
def workflow_matcher_view(request):
    return render(request, 'workflow.html')

@csrf_exempt  # This decorator allows for POST requests from all origins, not recommended in production environment.
def workflow_matcher(request):
    print('workflow_matcher called')  # Add this line
    if request.method == 'POST':
        string_data = json.loads(request.body)['jsonData']
        data = json.loads(string_data)
        matcher = FabricationWorkflowMatcher(data, force_report= True)
        matcher.run()
        # Call relevant methods of the matcher here.
        # You might want to call matcher.build_query() or other methods and return their results.
        # In this example, let's suppose matcher.build_query() returns a dictionary.
        result = matcher.build_query()
        return JsonResponse(result, safe=False)
    else:
        return JsonResponse({'error': 'Only POST method is allowed.'}, status=405)



