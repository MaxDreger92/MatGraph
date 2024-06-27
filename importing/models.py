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
        url = f"{os.environ.get('FILESERVER_URL_DEL')}{self.report_file_link.split('/')[-1]}"
        payload = {'user': os.environ.get('FILE_SERVER_USER'), 'password': os.environ.get('FILE_SERVER_PASSWORD')}
        headers = {'Accept': '*/*'}
        resp_data = requests.delete(url, headers=headers, data=payload)
        super().delete()

    def delete_selected(self, **kwargs):
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
            new_record = cls.objects.get_or_create(
                header=str(header)[:200]
                )[0]
            new_record.sample_column=column_value[:200]
            new_record.save()
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



class ImporterCache(models.Model, Cache):
    column_label = models.CharField(max_length=200, null = True, blank=True)  # List of labels
    LABEL_CHOICES = [
        ('Matter', 'Matter'),
        ('Property', 'Property'),
        ('Parameter', 'Parameter'),
        ('Measurement', 'Measurement'),
        ('Manufacturing', 'Manufacturing'),
        ('Metadata', 'Metadata'),
        ('No label', 'No label'),
        ('Simulation', 'Simulation'),
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

{"Processing Temperature (Value)": {"Label": "Parameter", "Attribute": "value"}, "Processing Temperature (Error)": {"Label": "Parameter", "Attribute": "error"}, "Processing Temperature Unit": {"Label": "Parameter", "Attribute": "name"}, "Average of Processing Temperature": {"Label": "Parameter", "Attribute": "value"}, "StdDev of Processing Temperature": {"Label": "Parameter", "Attribute": "std"}, "Processing Pressure_Value": {"Label": "Parameter", "Attribute": "value"}, "Processing Pressure_Error": {"Label": "Parameter", "Attribute": "error"}, "Processing Pressure Unit": {"Label": "Parameter", "Attribute": "value"}, "Processing Pressure_Average": {"Label": "Parameter", "Attribute": "value"}, "Processing Pressure_StdDev": {"Label": "Parameter", "Attribute": "std"}, "Processing Time (Value)": {"Label": "Parameter", "Attribute": "average"}, "Processing Time_Uncertainty": {"Label": "Parameter", "Attribute": "average"}, "Processing Time_Measure": {"Label": "Parameter", "Attribute": "name"}, "Average of Processing Time": {"Label": "Parameter", "Attribute": "average"}, "Processing Time_StandardDeviation": {"Label": "Parameter", "Attribute": "std"}, "Cooling Rate_Value": {"Label": "Parameter", "Attribute": "value"}, "Cooling Rate_Error": {"Label": "Parameter", "Attribute": "error"}, "Cooling Rate Unit": {"Label": "Parameter", "Attribute": "unit"}, "Cooling Rate_Average": {"Label": "Parameter", "Attribute": "value"}, "Cooling Rate_StandardDeviation": {"Label": "Parameter", "Attribute": "std"}, "Value of Heating Rate": {"Label": "Parameter", "Attribute": "average"}, "Heating Rate_Error": {"Label": "Parameter", "Attribute": "error"}, "Unit of Heating Rate": {"Label": "Parameter", "Attribute": "unit"}, "Heating Rate_Average": {"Label": "Parameter", "Attribute": "average"}, "Heating Rate StdDev": {"Label": "Parameter", "Attribute": "std"}, "Annealing Time_Measurement": {"Label": "Parameter", "Attribute": "value"}, "Error of Annealing Time": {"Label": "Parameter", "Attribute": "error"}, "Annealing Time_Measure": {"Label": "Parameter", "Attribute": "value"}, "Annealing Time_Average": {"Label": "Parameter", "Attribute": "value"}, "Annealing Time (StdDev)": {"Label": "Parameter", "Attribute": "std"}, "Value of Annealing Temperature": {"Label": "Parameter", "Attribute": "value"}, "Annealing Temperature (Error)": {"Label": "Parameter", "Attribute": "error"}, "Annealing Temperature Unit": {"Label": "Parameter", "Attribute": "unit"}, "Annealing Temperature Average": {"Label": "Parameter", "Attribute": "average"}, "Annealing Temperature_StdDev": {"Label": "Parameter", "Attribute": "std"}, "Value of Extrusion Speed": {"Label": "Parameter", "Attribute": "value"}, "Extrusion Speed_Error": {"Label": "Parameter", "Attribute": "error"}, "Extrusion Speed (Unit)": {"Label": "Parameter", "Attribute": "unit"}, "Average of Extrusion Speed": {"Label": "Parameter", "Attribute": "average"}, "Extrusion Speed StdDev": {"Label": "Parameter", "Attribute": "std"}, "Rolling Speed Value": {"Label": "Parameter", "Attribute": "value"}, "Error of Rolling Speed": {"Label": "Parameter", "Attribute": "error"}, "Rolling Speed Unit": {"Label": "Parameter", "Attribute": "unit"}, "Rolling Speed (Average)": {"Label": "Parameter", "Attribute": "average"}, "StdDev of Rolling Speed": {"Label": "Parameter", "Attribute": "std"}, "Molding Pressure_Value": {"Label": "Parameter", "Attribute": "average"}, "Molding Pressure_Error": {"Label": "Parameter", "Attribute": "error"}, "Unit of Molding Pressure": {"Label": "Parameter", "Attribute": "value"}, "Molding Pressure_Average": {"Label": "Parameter", "Attribute": "average"}, "StdDev of Molding Pressure": {"Label": "Parameter", "Attribute": "std"}, "Curing Time_Value": {"Label": "Parameter", "Attribute": "value"}, "Curing Time_Uncertainty": {"Label": "Parameter", "Attribute": "average"}, "Curing Time_Unit": {"Label": "Parameter", "Attribute": "unit"}, "Curing Time Average": {"Label": "Parameter", "Attribute": "average"}, "StdDev of Curing Time": {"Label": "Parameter", "Attribute": "std"}, "Curing Temperature_Value": {"Label": "Parameter", "Attribute": "value"}, "Curing Temperature Error": {"Label": "Parameter", "Attribute": "error"}, "Curing Temperature (Unit)": {"Label": "Parameter", "Attribute": "unit"}, "Curing Temperature Average": {"Label": "Parameter", "Attribute": "error"}, "Curing Temperature_StdDev": {"Label": "Parameter", "Attribute": "std"}, "Mixing Speed_Measurement": {"Label": "Parameter", "Attribute": "value"}, "Error of Mixing Speed": {"Label": "Parameter", "Attribute": "value"}, "Mixing Speed_Unit": {"Label": "Parameter", "Attribute": "unit"}, "Mixing Speed_Mean": {"Label": "Parameter", "Attribute": "name"}, "Mixing Speed (StdDev)": {"Label": "Parameter", "Attribute": "name"}, "Mixing Time Value": {"Label": "Parameter", "Attribute": "value"}, "Mixing Time_Error": {"Label": "Parameter", "Attribute": "error"}, "Mixing Time_Measure": {"Label": "Parameter", "Attribute": "name"}, "Mixing Time_Average": {"Label": "Parameter", "Attribute": "average"}, "Mixing Time_StdDev": {"Label": "Parameter", "Attribute": "std"}, "Casting Temperature_Measurement": {"Label": "Parameter", "Attribute": "value"}, "Casting Temperature_Uncertainty": {"Label": "Parameter", "Attribute": "std"}, "Casting Temperature Unit": {"Label": "Parameter", "Attribute": "unit"}, "Average of Casting Temperature": {"Label": "Parameter", "Attribute": "average"}, "Casting Temperature_StdDev": {"Label": "Parameter", "Attribute": "std"}, "Quenching Temperature (Value)": {"Label": "Parameter", "Attribute": "value"}, "Quenching Temperature_Uncertainty": {"Label": "Parameter", "Attribute": "average"}, "Unit of Quenching Temperature": {"Label": "Parameter", "Attribute": "unit"}, "Quenching Temperature Average": {"Label": "Parameter", "Attribute": "average"}, "Quenching Temperature_StandardDeviation": {"Label": "Parameter", "Attribute": "std"}, "Quenching Time Value": {"Label": "Parameter", "Attribute": "value"}, "Quenching Time (Error)": {"Label": "Parameter", "Attribute": "error"}, "Quenching Time (Unit)": {"Label": "Parameter", "Attribute": "unit"}, "Quenching Time Average": {"Label": "Parameter", "Attribute": "value"}, "StdDev of Quenching Time": {"Label": "Parameter", "Attribute": "std"}, "Aging Temperature Value": {"Label": "Parameter", "Attribute": "value"}, "Error of Aging Temperature": {"Label": "Parameter", "Attribute": "error"}, "Unit of Aging Temperature": {"Label": "Parameter", "Attribute": "unit"}, "Aging Temperature (Average)": {"Label": "Parameter", "Attribute": "average"}, "Aging Temperature StdDev": {"Label": "Parameter", "Attribute": "std"}, "Aging Time Value": {"Label": "Parameter", "Attribute": "value"}, "Error of Aging Time": {"Label": "Parameter", "Attribute": "error"}, "Aging Time (Unit)": {"Label": "Parameter", "Attribute": "unit"}, "Average of Aging Time": {"Label": "Parameter", "Attribute": "average"}, "Aging Time_StandardDeviation": {"Label": "Parameter", "Attribute": "std"}, "Value of Sintering Temperature": {"Label": "Parameter", "Attribute": "value"}, "Sintering Temperature Error": {"Label": "Parameter", "Attribute": "error"}, "Sintering Temperature_Unit": {"Label": "Parameter", "Attribute": "unit"}, "Sintering Temperature (Average)": {"Label": "Parameter", "Attribute": "average"}, "StdDev of Sintering Temperature": {"Label": "Parameter", "Attribute": "std"}, "Sintering Time (Value)": {"Label": "Parameter", "Attribute": "value"}, "Sintering Time_Uncertainty": {"Label": "Parameter", "Attribute": "value"}, "Sintering Time Unit": {"Label": "Parameter", "Attribute": "unit"}, "Sintering Time Average": {"Label": "Parameter", "Attribute": "value"}, "Sintering Time (StdDev)": {"Label": "Parameter", "Attribute": "std"}, "Milling Speed Value": {"Label": "Parameter", "Attribute": "value"}, "Error of Milling Speed": {"Label": "Parameter", "Attribute": "value"}, "Milling Speed_Measure": {"Label": "Parameter", "Attribute": "value"}, "Milling Speed_Mean": {"Label": "Parameter", "Attribute": "value"}, "Milling Speed_StandardDeviation": {"Label": "Parameter", "Attribute": "std"}, "Value of Milling Time": {"Label": "Parameter", "Attribute": "value"}, "Milling Time Error": {"Label": "Parameter", "Attribute": "error"}, "Milling Time_Unit": {"Label": "Parameter", "Attribute": "unit"}, "Milling Time_Average": {"Label": "Parameter", "Attribute": "average"}, "Milling Time StdDev": {"Label": "Parameter", "Attribute": "std"}, "Spray Rate_Value": {"Label": "Parameter", "Attribute": "value"}, "Spray Rate_Error": {"Label": "Parameter", "Attribute": "error"}, "Spray Rate (Unit)": {"Label": "Parameter", "Attribute": "name"}, "Spray Rate_Mean": {"Label": "Parameter", "Attribute": "std"}, "Spray Rate (StdDev)": {"Label": "Parameter", "Attribute": "std"}, "Value of Deposition Rate": {"Label": "Parameter", "Attribute": "std"}, "Deposition Rate Error": {"Label": "Parameter", "Attribute": "error"}, "Unit of Deposition Rate": {"Label": "Parameter", "Attribute": "unit"}, "Deposition Rate Average": {"Label": "Parameter", "Attribute": "average"}, "Deposition Rate (StdDev)": {"Label": "Parameter", "Attribute": "std"}, "Deposition Temperature_Value": {"Label": "Parameter", "Attribute": "name"}, "Deposition Temperature Error": {"Label": "Parameter", "Attribute": "error"}, "Deposition Temperature (Unit)": {"Label": "Parameter", "Attribute": "unit"}, "Deposition Temperature_Average": {"Label": "Parameter", "Attribute": "average"}, "Deposition Temperature_StandardDeviation": {"Label": "Parameter", "Attribute": "std"}, "Etching Time_Value": {"Label": "Parameter", "Attribute": "value"}, "Error of Etching Time": {"Label": "Parameter", "Attribute": "error"}, "Etching Time_Unit": {"Label": "Parameter", "Attribute": "unit"}, "Etching Time_Mean": {"Label": "Parameter", "Attribute": "value"}, "Etching Time (StdDev)": {"Label": "Parameter", "Attribute": "std"}, "Etching Temperature Value": {"Label": "Parameter", "Attribute": "value"}, "Etching Temperature Error": {"Label": "Parameter", "Attribute": "error"}, "Etching Temperature (Unit)": {"Label": "Parameter", "Attribute": "unit"}, "Etching Temperature_Average": {"Label": "Parameter", "Attribute": "average"}, "Etching Temperature_StandardDeviation": {"Label": "Parameter", "Attribute": "std"}, "Plasma Power Value": {"Label": "Parameter", "Attribute": "average"}, "Error of Plasma Power": {"Label": "Parameter", "Attribute": "error"}, "Plasma Power_Measure": {"Label": "Parameter", "Attribute": "unit"}, "Average of Plasma Power": {"Label": "Parameter", "Attribute": "average"}, "Plasma Power_StdDev": {"Label": "Parameter", "Attribute": "std"}, "Plasma Duration_Value": {"Label": "Parameter", "Attribute": "value"}, "Plasma Duration_Error": {"Label": "Parameter", "Attribute": "error"}, "Unit of Plasma Duration": {"Label": "Parameter", "Attribute": "unit"}, "Plasma Duration Average": {"Label": "Parameter", "Attribute": "average"}, "Plasma Duration StdDev": {"Label": "Parameter", "Attribute": "std"}, "Value of Vapor Pressure": {"Label": "Parameter", "Attribute": "average"}, "Vapor Pressure Error": {"Label": "Parameter", "Attribute": "error"}, "Unit of Vapor Pressure": {"Label": "Parameter", "Attribute": "unit"}, "Vapor Pressure (Average)": {"Label": "Parameter", "Attribute": "average"}, "Vapor Pressure StdDev": {"Label": "Parameter", "Attribute": "std"}, "Value of Vapor Temperature": {"Label": "Parameter", "Attribute": "value"}, "Vapor Temperature (Error)": {"Label": "Parameter", "Attribute": "error"}, "Vapor Temperature (Unit)": {"Label": "Parameter", "Attribute": "unit"}, "Vapor Temperature Average": {"Label": "Parameter", "Attribute": "average"}, "Vapor Temperature StdDev": {"Label": "Parameter", "Attribute": "std"}, "Filtration Rate_Measurement": {"Label": "Parameter", "Attribute": "value"}, "Error of Filtration Rate": {"Label": "Parameter", "Attribute": "error"}, "Filtration Rate (Unit)": {"Label": "Parameter", "Attribute": "unit"}, "Filtration Rate_Average": {"Label": "Parameter", "Attribute": "value"}, "Filtration Rate (StdDev)": {"Label": "Parameter", "Attribute": "std"}, "Drying Temperature Value": {"Label": "Parameter", "Attribute": "value"}, "Error of Drying Temperature": {"Label": "Parameter", "Attribute": "error"}, "Drying Temperature_Unit": {"Label": "Parameter", "Attribute": "unit"}, "Drying Temperature_Average": {"Label": "Parameter", "Attribute": "average"}, "Drying Temperature_StdDev": {"Label": "Parameter", "Attribute": "std"}, "Drying Time_Measurement": {"Label": "Parameter", "Attribute": "value"}, "Drying Time Error": {"Label": "Parameter", "Attribute": "error"}, "Drying Time_Measure": {"Label": "Parameter", "Attribute": "name"}, "Drying Time Average": {"Label": "Parameter", "Attribute": "average"}, "StdDev of Drying Time": {"Label": "Parameter", "Attribute": "std"}, "Humidity Value": {"Label": "Parameter", "Attribute": "value"}, "Error of Humidity": {"Label": "Parameter", "Attribute": "error"}, "Humidity (Unit)": {"Label": "Parameter", "Attribute": "unit"}, "Humidity_Average": {"Label": "Parameter", "Attribute": "average"}, "Humidity_StdDev": {"Label": "Parameter", "Attribute": "std"}, "pH Value": {"Label": "Property", "Attribute": "value"}, "pH (Error)": {"Label": "Parameter", "Attribute": "error"}, "pH Unit": {"Label": "Parameter", "Attribute": "unit"}, "pH_Average": {"Label": "Parameter", "Attribute": "average"}, "pH_StdDev": {"Label": "Parameter", "Attribute": "std"}, "Solvent Concentration Value": {"Label": "Property", "Attribute": "value"}, "Solvent Concentration Error": {"Label": "Property", "Attribute": "error"}, "Solvent Concentration_Unit": {"Label": "Property", "Attribute": "name"}, "Average of Solvent Concentration": {"Label": "Property", "Attribute": "value"}, "Solvent Concentration_StdDev": {"Label": "Property", "Attribute": "std"}, "Impurity Level_Measurement": {"Label": "Property", "Attribute": "value"}, "Impurity Level Error": {"Label": "Property", "Attribute": "error"}, "Impurity Level (Unit)": {"Label": "Property", "Attribute": "value"}, "Impurity Level Average": {"Label": "Property", "Attribute": "value"}, "Impurity Level StdDev": {"Label": "Property", "Attribute": "std"}, "Value of Purification Time": {"Label": "Property", "Attribute": "value"}, "Purification Time_Uncertainty": {"Label": "Parameter", "Attribute": "value"}, "Purification Time_Measure": {"Label": "Parameter", "Attribute": "name"}, "Purification Time (Average)": {"Label": "Parameter", "Attribute": "average"}, "Purification Time_StandardDeviation": {"Label": "Parameter", "Attribute": "std"}}
