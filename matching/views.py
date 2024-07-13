from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .fabricationworkflows import FabricationWorkflowMatcher
import json
from django.shortcuts import render

@csrf_exempt  # This decorator allows for POST requests from all origins, not recommended in production environment.
def workflow_matcher_view(request):
    print("miau")
    return render(request, 'index.html')

def workflow_matcher(request):
    print("miau")

    if request.method == 'GET':
        # Retrieve the 'jsonData' from the GET query parameters instead of request body
        string_data = request.GET.get('workflow', None)

        if not string_data:
            return JsonResponse({'error': 'jsonData is required.'}, status=400)

        data = json.loads(string_data)

        matcher = FabricationWorkflowMatcher(data, force_report=True)
        matcher.run()

        # Convert the DataFrame to CSV and create an HTTP response with it
        csv_content = matcher.result.to_csv(index=False)
        matcher.result.to_csv('output_filename.csv', index=False)
        response = HttpResponse(csv_content, content_type='text/csv',
                                headers = {'Content-Disposition': 'attachment; filename=workflows.csv'})
        return response
    else:
        return JsonResponse({'error': 'Only GET method is allowed.'}, status=405)




