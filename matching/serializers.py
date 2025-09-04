from tasks.serializers import BaseProcessSerializer, SmartJSONField

class WorkflowMatchSerializer(BaseProcessSerializer):
    graph = SmartJSONField(required=True)