import io
import os

import requests
from django.db import models, IntegrityError
from neomodel import classproperty, RelationshipFrom, ZeroOrMore
from neomodel import StringProperty, RelationshipTo, One, ArrayProperty, FloatProperty
from tenacity import retry, wait_random_exponential, stop_after_attempt

from graphutils.models import UIDDjangoNode, EmbeddingNodeSet
from matgraph.models.embeddings import ModelEmbedding
from django.contrib.postgres.fields import JSONField



class ImportingReport(models.Model):
    """
    Model to store reports of data importing processes.
    """
    date = models.DateTimeField(auto_now_add=True)
    report = models.TextField(default='None given')
    html_report = models.TextField(default='None given')
    context = models.TextField(null=True, blank=True, max_length= 140, default='None given')
    file_link = models.CharField(max_length= 100, default='None given')
    report_file_link = models.CharField(max_length= 100, default='None given')
    file_name = models.CharField(max_length= 100, default='None given')

    class Meta:
        abstract = True

    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None, save_to_file_server = True):
        if save_to_file_server:
            # Upload report logic
            file_obj = io.StringIO()
            self.report.to_csv(file_obj, index=False)
            file_obj.seek(0)



            url = f"{os.environ.get('FILESERVER_URL_POST')}{self.file_name}"
            payload = {'user': os.environ.get('FILE_SERVER_USER'), 'password': os.environ.get('FILE_SERVER_PASSWORD')}
            files = [('files', (f"{self.file_name}_classification_report", file_obj.read()))]
            headers = {'Accept': '*/*'}
            # resp_data = requests.post(url, headers=headers, data=payload, files=files).json()
            resp_data = requests.post(url, headers=headers, data=payload, files=files)
            response = resp_data.json()
            self.report_file_link = f"{os.environ.get('FILESERVER_URL_GET')}{response['filename'][0]}"
        else:
            self.file_link = "None given"
        super().save()

    def delete(self, force_insert=False, force_update=False, using=None,
             update_fields=None, save_to_file_server = True):
        print("delete")
        url = f"{os.environ.get('FILESERVER_URL_DEL')}{self.report_file_link.split('/')[-1]}"
        print("URL before request:", url)  # Add a print statement to log the URL
        payload = {'user': os.environ.get('FILE_SERVER_USER'), 'password': os.environ.get('FILE_SERVER_PASSWORD')}
        headers = {'Accept': '*/*'}
        resp_data = requests.delete(url, headers=headers, data=payload)
        print(resp_data.text)
        super().delete()

    def delete_selected(self, **kwargs):
        print("delete")
        super().delete_selected

    def __str__(self):
        """Return a readable representation of the importing report."""
        return f'Importing Report ({self.type}, {self.date})'

class LabelClassificationReport(ImportingReport):
    """
    Model to store reports of data importing processes.
    """


    class Meta:
            verbose_name = 'Label Classification Report'
            verbose_name_plural = 'Label Classification Reports'


    def __str__(self):
        """Return a readable representation of the importing report."""
        return f'LabelExtraction Report: ({self.file_link}, {self.date})'

class AttributeClassificationReport(ImportingReport):
    """
    Model to store reports of data importing processes.
    """

    class Meta:
        verbose_name = 'Attribute Classification Report'
        verbose_name_plural = 'Attribute Classification Reports'



    def __str__(self):
        """Return a readable representation of the importing report."""
        return f'LabelExtraction Report: ({self.file_link}, {self.date})'


class NodeExtractionReport(ImportingReport):
    """
    Model to store reports of data importing processes.
    """

    class Meta:
        verbose_name = 'Node Extraction Report'
        verbose_name_plural = 'Node Extraction Reports'



    def __str__(self):
        """Return a readable representation of the importing report."""
        return f'NodeExtraction Report: ({self.file_link}, {self.date})'

class NodeLabel(UIDDjangoNode):
    """
    Neo4j Node representing a label with a unique name and associated nodes.
    """
    name = StringProperty(required=True, unique_index=True)

    @classproperty
    def nodes(cls):
        """Return the set of nodes associated with this label."""
        return EmbeddingNodeSet(cls)

    @classproperty
    def embedding(cls):
        """Return the embedding of the node label."""
        return "label-embeddings"

    label = RelationshipFrom('importing.models.NodeLabelEmbedding', 'FOR', ZeroOrMore)  # This should be a self-relation


class NodeAttribute(UIDDjangoNode):
    """
    Neo4j Node representing an attribute with a unique name and associated nodes.
    """
    name = StringProperty(required=True, unique_index=True)

    @classproperty
    def nodes(cls):
        """Return the set of nodes associated with this attribute."""
        return EmbeddingNodeSet(cls)

    @classproperty
    def embedding(cls):
        """Return the embedding of the node attribute."""
        return "attribute-embeddings"

    label = RelationshipTo('importing.models.NodeAttribute', 'FOR', One)  # Assuming this should point to a NodeLabel

class MatterAttribute(NodeAttribute):
    label = RelationshipFrom('importing.models.MatterAttributeEmbedding', 'FOR', ZeroOrMore)  # Points at NodeAttribute
    @classproperty
    def embedding(cls):
        """Return the embedding of the node attribute."""
        return "matter-attribute-embeddings"
    pass

class PropertyAttribute(NodeAttribute):
    label = RelationshipFrom('importing.models.PropertyAttributeEmbedding', 'FOR', ZeroOrMore)  # Points at NodeAttribute
    @classproperty
    def embedding(cls):
        """Return the embedding of the node attribute."""
        return "property-attribute-embeddings"
    pass

class ParameterAttribute(NodeAttribute):
    label = RelationshipFrom('importing.models.ParameterAttributeEmbedding', 'FOR', ZeroOrMore)  # Points at NodeAttribute
    @classproperty
    def embedding(cls):
        """Return the embedding of the node attribute."""
        return "parameter-attribute-embeddings"
    pass

class MeasurementAttribute(NodeAttribute):
    label = RelationshipFrom('importing.models.MeasurementAttributeEmbedding', 'FOR', ZeroOrMore)  # Points at NodeAttribute
    @classproperty
    def embedding(cls):
        """Return the embedding of the node attribute."""
        return "measurement-attribute-embeddings"
    pass
class ManufacturingAttribute(NodeAttribute):
    label = RelationshipFrom('importing.models.ManufacturingAttributeEmbedding', 'FOR', ZeroOrMore)  # Points at NodeAttribute
    @classproperty
    def embedding(cls):
        """Return the embedding of the node attribute."""
        return "manufacturing-attribute-embeddings"
    pass
class MetadataAttribute(NodeAttribute):
    label = RelationshipFrom('importing.models.MetadataAttributeEmbedding', 'FOR', ZeroOrMore)  # Points at NodeAttribute
    @classproperty
    def embedding(cls):
        """Return the embedding of the node attribute."""
        return "metadata-attribute-embeddings"
    pass
class NodeLabelEmbedding(ModelEmbedding):
    """
    Django model to store embeddings of node labels.
    """
    vector = ArrayProperty(FloatProperty(), required=False)

    class Meta:
        verbose_name = 'Node label embedding'
        verbose_name_plural = 'Node label embeddings'

    def __str__(self):
        """Return a readable representation of the node label embedding."""
        return f'Node Label Embedding for {self.label.name}'


class NodeAttributeEmbedding(ModelEmbedding):
    """
    Django model to store embeddings of node attributes.
    """
    label = RelationshipTo('importing.models.NodeAttribute', 'FOR', One)  # Points at NodeAttribute
    vector = ArrayProperty(FloatProperty(), required=False)


    def __str__(self):
        """Return a readable representation of the node attribute embedding."""
        return f'Node Attribute Embedding for {self.label.name}'




class MatterAttributeEmbedding(NodeAttributeEmbedding):
    class Meta:
        verbose_name = 'Matter attribute embedding'
        verbose_name_plural = 'Matter attribute embeddings'
    label = RelationshipTo('importing.models.MatterAttribute', 'FOR', One)  # Points at NodeAttribute

class PropertyAttributeEmbedding(NodeAttributeEmbedding):
    class Meta:
        verbose_name = 'Property attribute embedding'
        verbose_name_plural = 'Property attribute embeddings'
    label = RelationshipTo('importing.models.PropertyAttribute', 'FOR', One)  # Points at NodeAttribute

class ParameterAttributeEmbedding(NodeAttributeEmbedding):
    class Meta:
        verbose_name = 'Parameter attribute embedding'
        verbose_name_plural = 'Parameter attribute embeddings'
    label = RelationshipTo('importing.models.ParameterAttribute', 'FOR', One)  # Points at NodeAttribute


class MeasurementAttributeEmbedding(NodeAttributeEmbedding):
    class Meta:
        verbose_name = 'Measurement attribute embedding'
        verbose_name_plural = 'Measurement attribute embeddings'
    label = RelationshipTo('importing.models.MeasurementAttribute', 'FOR', One)  # Points at NodeAttribute


class ManufacturingAttributeEmbedding(NodeAttributeEmbedding):
    class Meta:
        verbose_name = 'Manufacturing attribute embedding'
        verbose_name_plural = 'Manufacturing attribute embeddings'
    label = RelationshipTo('importing.models.ManufacturingAttribute', 'FOR', One)  # Points at NodeAttribute


class MetadataAttributeEmbedding(NodeAttributeEmbedding):
    class Meta:
        verbose_name = 'Metadata attribute embedding'
        verbose_name_plural = 'Metadata attribute embeddings'
    label = RelationshipTo('importing.models.MetadataAttribute', 'FOR', One)  # Points at NodeAttribute


class Cache:

    def get_validation_state(self, attribute_type):
        # Construct the attribute name based on the attribute_type
        attribute_name = f"validated_{attribute_type}"

        # Return the attribute value if it exists in the class
        return getattr(self, attribute_name, None)

    @classmethod
    def fetch(cls, header, column_value, attribute_type):

        # Attempt to find an existing record
        cached = cls.objects.filter(header=header).first()

        if cached:
            if cached.get_validation_state(attribute_type):
                return (cached.sample_column, cached.column_label, cached.header_attribute, cached.column_attribute)
            return None
        else:
            # print("header:",header)
            # new_record = cls.objects.get_or_create(
            #     header=str(header)[:200]
            #     )[0]
            # new_record.sample_column=column_value[:200]
            # new_record.save()
            # return (new_record.sample_column, new_record.column_label, new_record.header_attribute, new_record.column_attribute)
            return None


    @classmethod
    def update(cls, header, attribute_type, **kwargs):
        if cached := cls.objects.filter(header=header).first():
            if not cached.get_validation_state(attribute_type):
                for key, value in kwargs.items():
                    if hasattr(cached, key):
                        setattr(cached, key, value)
                    else:
                        raise AttributeError(f"{cls.__name__} has no attribute '{key}'")
                cached.save()
            else:
                for key, value in kwargs.items():
                    if hasattr(cached, key):
                        setattr(cached, key, value)
                        setattr(cached, f"validated_{attribute_type}", False)
                    else:
                        raise AttributeError(f"{cls.__name__} has no attribute '{key}'")
                cached.save()



class ImporterCache(Cache, models.Model):
    LABEL_CHOICES = [
        ('Matter', 'Matter'),
        ('Property', 'Property'),
        ('Parameter', 'Parameter'),
        ('Measurement', 'Measurement'),
        ('Manufacturing', 'Manufacturing'),
        ('Metadata', 'Metadata'),
        ('No label', 'No label'),
        (None, 'None'),
    ]
    ATTRIBUTE_CHOICES = [
        ('identifier', 'Identifier'),
        ('name', 'Name'),
        ('value', 'Value'),
        ('unit', 'Unit'),
        ('error', 'Error'),
        ('std', 'Standard deviation'),
        ('min', 'Minimum'),
        ('max', 'Maximum'),
        ('mean', 'Mean'),
        ('median', 'Median'),
        ('concentration', 'Concentration'),
        ('ratio', 'Ratio'),
        ('batch_number', 'Batch'),
        ('No attribute', 'No attribute'),
        (None, 'None'),
        ]
    header = models.CharField(max_length=200,  db_index=True, unique=True)
    column_label = models.CharField(max_length=200,choices=LABEL_CHOICES, null = True, blank=True)  # List of labels
    header_attribute = models.CharField(max_length=200,choices=ATTRIBUTE_CHOICES, null = True, blank=True)  # List of header attributes
    column_attribute = models.CharField(max_length=200,choices=ATTRIBUTE_CHOICES, null = True, blank=True)  # List of column attributes
    sample_column = models.CharField(max_length=200)  # List of sample columns
    validated_column_label = models.BooleanField(default=False, verbose_name="Validated Col-label")
    validated_column_attribute = models.BooleanField(default=False, verbose_name="Validated Col-attribute")
    validated_header_attribute = models.BooleanField(default=False, verbose_name="Validated Header-attribute")


class FullTableCache(models.Model, Cache):
    header = models.CharField(db_index=True, unique=True, max_length=40000)
    validated_graph = models.BooleanField(default=False, verbose_name="Validated Graph")
    graph = models.JSONField(null = True)

    @classmethod
    def fetch(cls, header):

        # Attempt to find an existing record
        cached = cls.objects.filter(header=header).first()

        if cached:
            if cached.get_validation_state('graph'):
                return (cached.graph)
        else:
            new_record = cls.objects.create(
                header=header)
            new_record.save()