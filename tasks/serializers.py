from rest_framework import serializers
import json


class SmartJSONField(serializers.JSONField):
    """
    Accepts either a Python dict/list or a JSON-encoded string.
    Always returns a normalized Python object, raising a clean
    ValidationError on malformed JSON.
    """
    def to_internal_value(self, data):
        if isinstance(data, (dict, list)) or data is None:
            return super().to_internal_value(data)

        if isinstance(data, str):
            s = data.strip()
            if s == "":
                return None
            try:
                data = json.loads(s)
            except json.JSONDecodeError as e:
                raise serializers.ValidationError(f"Invalid JSON: {e.msg}")
        return super().to_internal_value(data)


class BaseProcessSerializer(serializers.Serializer):
    process_id = serializers.CharField(max_length=255)
    user_id = serializers.CharField(max_length=255)
    callback_url = serializers.URLField(required=False, allow_blank=True)
