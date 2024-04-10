# serializers.py
from rest_framework import serializers
from matgraph.models.metadata import File

class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('uid', 'name', 'path')
