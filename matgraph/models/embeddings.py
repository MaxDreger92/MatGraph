from django_neomodel import classproperty
from neomodel import StringProperty, FloatProperty, ArrayProperty, RelationshipTo, OneOrMore

from graphutils.models import UIDDjangoNode, EmbeddingNodeSet


class ModelEmbedding(UIDDjangoNode):
    """
    This class represents a Model Embedding, which holds a vector representation of some object or concept for
    machine learning purposes.
    """

    class Meta:
        app_label = "matgraph"  # App label for django


    # Properties
    vector = ArrayProperty(
        base_property=FloatProperty(),  # The vector is composed of floats
        required=True  # This field must be populated
    )
    input = StringProperty(required=True)  # The original input used to generate the vector



class MatterEmbedding(ModelEmbedding):
    """
    This class represents a Matter Embedding, which holds a vector representation of some matter for machine learning
    purposes.
    """

    class Meta:
        app_label = "matgraph"  # App label for django

    # Relationships
    matter = RelationshipTo('matgraph.models.ontology.EMMOMatter', 'FOR', OneOrMore)  # Points at Matter


class QuantityEmbedding(ModelEmbedding):
    """
    This class represents a Matter Embedding, which holds a vector representation of some matter for machine learning
    purposes.
    """

    class Meta:
        app_label = "matgraph"  # App label for django

    # Relationships
    quantity = RelationshipTo('matgraph.models.ontology.EMMOQuantity', 'FOR', OneOrMore)


class ProcessEmbedding(ModelEmbedding):
    """
    This class represents a Matter Embedding, which holds a vector representation of some matter for machine learning
    purposes.
    """

    class Meta:
        app_label = "matgraph"  # App label for django

    # Relationships
    process = RelationshipTo('matgraph.models.ontology.EMMOProcess', 'FOR', OneOrMore)
