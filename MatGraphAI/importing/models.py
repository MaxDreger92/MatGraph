from django.db import models
from django_neomodel import classproperty
from neomodel import StringProperty, RelationshipTo, One, ArrayProperty, FloatProperty

from graphutils.models import UIDDjangoNode, EmbeddingNodeSet
from matgraph.models.embeddings import ModelEmbedding


class ImportingReport(models.Model):
    """
    Model to store reports of data importing processes.
    """
    type = models.CharField(max_length=60)
    date = models.DateTimeField(auto_now_add=True)
    report = models.TextField()

    class Meta:
        verbose_name = 'Importing Report'
        verbose_name_plural = 'Importing Reports'

    def __str__(self):
        """Return a readable representation of the importing report."""
        return f'Importing Report ({self.type}, {self.date})'


class NodeLabel(UIDDjangoNode):
    """
    Neo4j Node representing a label with a unique name and associated nodes.
    """
    name = StringProperty(required=True, unique_index=True)

    @classproperty
    def nodes(cls):
        """Return the set of nodes associated with this label."""
        return EmbeddingNodeSet(cls)

    @classmethod
    def embedding(cls):
        """Return the embedding of the node label."""
        return "label-embeddings"

    label = RelationshipTo('importing.models.NodeLabel', 'FOR', One)  # This should be a self-relation


class NodeAttribute(UIDDjangoNode):
    """
    Neo4j Node representing an attribute with a unique name and associated nodes.
    """
    name = StringProperty(required=True, unique_index=True)

    @classproperty
    def nodes(cls):
        """Return the set of nodes associated with this attribute."""
        return EmbeddingNodeSet(cls)

    @classmethod
    def embedding(cls):
        """Return the embedding of the node attribute."""
        return "attribute-embeddings"

    label = RelationshipTo('importing.models.NodeAttribute', 'FOR', One)  # Assuming this should point to a NodeLabel


class NodeLabelEmbedding(ModelEmbedding):
    """
    Django model to store embeddings of node labels.
    """
    label = RelationshipTo('importing.models.NodeLabel', 'FOR', One)  # Points at NodeLabel
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

    class Meta:
        verbose_name = 'Node attribute embedding'
        verbose_name_plural = 'Node attribute embeddings'

    def __str__(self):
        """Return a readable representation of the node attribute embedding."""
        return f'Node Attribute Embedding for {self.label.name}'
