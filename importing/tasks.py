import math
from io import StringIO
from celery import shared_task
import requests
from matgraph.models.metadata import File
from importing.NodeLabelClassification.labelClassifier import NodeClassifier

def sanitize_data(data):
    if isinstance(data, dict):
        i = 0
        sanitized_dict = {}
        for k, v in data.items():
            i += 1
            if isinstance(k, float) and (math.isnan(k) or math.isinf(k)):
                k = f'column_{str(i)}'
            sanitized_dict[k] = sanitize_data(v)
        return sanitized_dict
    elif isinstance(data, list):
        return [sanitize_data(i) for i in data]
    elif isinstance(data, float):
        if math.isinf(data) or math.isnan(data):
            return None
        return data
    return data

@shared_task
def extract_labels(upload_id, context, file_id, user_token):
    file_record = File.nodes.get(uid=file_id)
    file_obj_bytes = file_record.get_file()
    file_obj_str = file_obj_bytes.decode('utf-8')
    file_obj = StringIO(file_obj_str)
    
    node_classifier = NodeClassifier(data=file_obj,
                                     context=context,
                                     file_link=file_record.link,
                                     file_name=file_record.name)
    node_classifier.run()
    labels = {element['header']: [[element['1_label']], element['column_values'][0]] for element in node_classifier.results}
    sanitized_labels = sanitize_data(labels)

    updates = {
        'labelDict': sanitized_labels,
        'progress': 2,
        'processing': False
    }
    endpoint = f'http://localhost:8080/api/users/uploads/{upload_id}'
    headers = {
        'Authorization': f'Bearer {user_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.patch(endpoint, headers=headers, json=updates)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f'Error: {e}')
