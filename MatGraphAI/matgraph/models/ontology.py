from neomodel import RelationshipTo, RelationshipFrom, ArrayProperty, FloatProperty, One, ZeroOrMore, \
    StringProperty

from matgraph.models.abstractclasses import OntologyNode, UIDDjangoNode
from matgraph.models.relationships import IsARel


class EMMOQuantity(OntologyNode):
    """
    Class representing EMMO quantity in the knowledge graph. This node is part of the European Materials Modelling
    Ontology (EMMO).
    """
    # Relationships
    emmo_is_a = RelationshipTo("Property", "EMMO__IS_A",
                               model=IsARel)  # Represents "IS_A" relationship to another EMMOQuantity
    emmo_subclass = RelationshipTo('matgraph.models.ontology.EMMOQuantity', 'EMMO__IS_A',
                                   cardinality=ZeroOrMore)


class EMMOMatter(OntologyNode):
    """
    Class representing EMMO matter in the knowledge graph. This node is also part of the European Materials Modelling
    Ontology (EMMO).
    """

    class Meta:
        verbose_name_plural = 'EMMO Matter'  # Plural name for admin interface

    app_label = 'matgraph'  # App label for django

    # Relationships
    is_a_material = RelationshipFrom('matgraph.models.matter.Material', "IS_A", model=IsARel, cardinality=ZeroOrMore)  # "IS_A" relationship from Matter model
    is_a_component = RelationshipFrom('matgraph.models.matter.Component', "IS_A", model=IsARel, cardinality=ZeroOrMore)
    is_a_device = RelationshipFrom('matgraph.models.matter.Device', "IS_A", model=IsARel, cardinality=ZeroOrMore)
    is_a_molecule = RelationshipFrom('matgraph.models.matter.Molecule', "IS_A", model=IsARel, cardinality=ZeroOrMore)

    emmo_subclass = RelationshipTo('matgraph.models.ontology.EMMOMatter', 'EMMO__IS_A', cardinality=ZeroOrMore)
    is_a = RelationshipFrom('matgraph.models.matter.Matter', "IS_A", model=IsARel, cardinality=ZeroOrMore)
    # def is_a(self):
    #     """Returns True if this node is related to other_node via any of the IS_A relationships."""
    #     return (
    #             self.is_a_material and
    #             self.is_a_component and
    #             self.is_a_device and
    #             self.is_a_molecule
    #     )




class EMMOProcess(OntologyNode):
    """
    Class representing EMMO process in the knowledge graph. This node is a component of the European Materials Modelling Ontology (EMMO).
    """

    class Meta:
        verbose_name_plural = 'EMMO Processes'  # Plural name for admin interface

    app_label = 'matgraph'  # App label for django

    # Relationships
    emmo_subclass = RelationshipTo('matgraph.models.ontology.EMMOProcess', 'EMMO__IS_A',
                                   cardinality=ZeroOrMore)  # Represents the possibility of having zero or more subclasses.
    is_a = RelationshipFrom('matgraph.models.processes.Process', "IS_A",
                            model=IsARel)  # "IS_A" relationship from Process model


class ModelEmbedding(UIDDjangoNode):
    """
    This class represents a Model Embedding, which holds a vector representation of some object or concept for
    machine learning purposes.
    """

    class Meta:
        app_label = "matgraph"  # App label for django

    # Relationships
    ontology_node = RelationshipTo('graphutils.models.AlternativeLabel', 'FOR', One)  # Points at OntologyNode

    # Properties
    vector = ArrayProperty(
        base_property=FloatProperty(),  # The vector is composed of floats
        required=True  # This field must be populated
    )
    input = StringProperty(required=True)  # The original input used to generate the vector
