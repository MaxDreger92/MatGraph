from rest_framework import serializers
from tasks.serializers import BaseProcessSerializer, SmartJSONField


class CsvFileSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, f):
        name = getattr(f, "name", "")
        if not str(name).lower().endswith(".csv"):
            raise serializers.ValidationError("Invalid file type (expected .csv)")
        return f


class LabelExtractSerializer(BaseProcessSerializer):
    context = SmartJSONField(required=True)


class AttributeExtractSerializer(BaseProcessSerializer):
    labels = SmartJSONField(required=False, allow_null=True)


class NodeExtractSerializer(BaseProcessSerializer):
    attributes = SmartJSONField(required=False, allow_null=True)


class GraphExtractSerializer(BaseProcessSerializer):
    graph = SmartJSONField(required=False, allow_null=True)


class GraphImportSerializer(BaseProcessSerializer):
    graph = SmartJSONField(required=False, allow_null=True)