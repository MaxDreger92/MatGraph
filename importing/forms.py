# Standard library imports
from neomodel import db, RelationshipManager
from django import forms

# Local application imports
from graphutils.embeddings import request_embedding
from graphutils.forms import NeoModelForm, RelationMultipleChoiceField, RelationSingleChoiceField
from importing.models import ImporterCache


class ClassifierAdminForm(NeoModelForm):
    """
    Base admin form for Node classifiers that provides a template for cleaning data
    and saving instances with relation handling.
    """

    def clean(self):
        """
        Extends the base clean method to include vector calculation from input data.

        Returns:
            dict: The cleaned data dictionary after including the vector if present.
        """
        cleaned_data = super().clean()  # Clean data using the base class method
        input_data = cleaned_data.get('input')

        # If there is input data, request its embedding vector and add it to cleaned data
        if input_data is not None:
            cleaned_data['vector'] = request_embedding(input_data)

        return cleaned_data

    def save(self, commit=True):
        """
        Saves the form's instance and handles the relationship saving for neo4j models.

        Args:
            commit (bool): Whether to commit the changes to the database.

        Returns:
            instance: The saved instance of the model.
        """
        instance = super().save(commit=commit)

        if commit:
            with db.transaction:
                instance.save()
                for field_name in self.changed_data:
                    if hasattr(instance, field_name):
                        field = getattr(instance, field_name)
                        if isinstance(field, RelationshipManager):
                            self.fields[field_name].save(field_name, instance, self.cleaned_data[field_name])

        return instance


class NodeLabelClassifierAdminForm(ClassifierAdminForm):
    """
    Admin form specific to Node Label Classifiers with customized fieldsets
    and relation fields for managing NodeLabel entities.
    """

    # Define a single choice field for the NodeLabel relation
    label = RelationSingleChoiceField("NodeLabel", primary_key="uid", label_field='name')

    # Define the layout of admin form fields
    fieldsets = [
        (None, {"fields": ("uid", "input", "label")}),
        ("Advanced options", {"fields": ["vector"]})
    ]


class NodeAttributeClassifierAdminForm(ClassifierAdminForm):
    """
    Admin form specific to Node Attribute Classifiers with customized fieldsets
    and relation fields for managing NodeAttribute entities.
    """

    # Define a single choice field for the NodeAttribute relation
    label = RelationSingleChoiceField("NodeAttribute", primary_key="uid", label_field='name')

    # Define the layout of admin form fields
    fieldsets = [
        (None, {"fields": ("uid", "input", "label")}),
        ("Advanced options", {"fields": ["vector"]})
    ]


class MatterAttributeClassifierAdminForm(NodeAttributeClassifierAdminForm):
    # Define a single choice field for the NodeAttribute relation
    label = RelationSingleChoiceField("MatterAttribute", primary_key="uid", label_field='name')

class PropertyAttributeClassifierAdminForm(NodeAttributeClassifierAdminForm):
    # Define a single choice field for the NodeAttribute relation
    label = RelationSingleChoiceField("PropertyAttribute", primary_key="uid", label_field='name')

class ParameterAttributeClassifierAdminForm(NodeAttributeClassifierAdminForm):
    # Define a single choice field for the NodeAttribute relation
    label = RelationSingleChoiceField("ParameterAttribute", primary_key="uid", label_field='name')

class MeasurementAttributeClassifierAdminForm(NodeAttributeClassifierAdminForm):
    # Define a single choice field for the NodeAttribute relation
    label = RelationSingleChoiceField("MeasurementAttribute", primary_key="uid", label_field='name')

class ManufacturingAttributeClassifierAdminForm(NodeAttributeClassifierAdminForm):
    # Define a single choice field for the NodeAttribute relation
    label = RelationSingleChoiceField("ManufacturingAttribute", primary_key="uid", label_field='name')

class MetadataAttributeClassifierAdminForm(NodeAttributeClassifierAdminForm):
    # Define a single choice field for the NodeAttribute relation
    label = RelationSingleChoiceField("MetadataAttribute", primary_key="uid", label_field='name')


