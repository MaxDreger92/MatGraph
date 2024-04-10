"""
The graphutils library contains classes that are needed to extend the django functionality on neo4j.

graphutils serializer classes:
 - LabeledDjangoNodeSerializer
 - QuotaSerializer
 - UploadedDocuments
"""

from rest_framework import serializers


class LabeledDjangoNodeSerializer(serializers.Serializer):

    label = serializers.CharField(read_only=True)
    uid = serializers.UUIDField()


class QuotaSerializer(serializers.Serializer):

    min = serializers.IntegerField(min_value=10, max_value=100)
    max = serializers.IntegerField(min_value=10, max_value=100)


class UploadedDocuments(serializers.Serializer):

    uid = serializers.UUIDField()
