from django_neomodel import classproperty
from neomodel import RelationshipTo, RelationshipFrom, ZeroOrMore

from graphutils.models import EmbeddingNodeSet
from matgraph.models.abstractclasses import OntologyNode
from matgraph.models.relationships import IsARel


class EMMOQuantity(OntologyNode):
    """
    Class representing EMMO quantity in the knowledge graph. This node is part of the European Materials Modelling
    Ontology (EMMO).
    """

    @classproperty
    def nodes(cls):
        """Return the set of nodes associated with this label."""
        return EmbeddingNodeSet(cls)

    @classproperty
    def embedding(cls):
        """
        Returns the embedding of the node as a numpy array.
        :return: numpy array
        """
        return "quantity-embeddings"

    # Relationships
    property = RelationshipFrom("matgraph.models.properties.Property", "IS_A",
                               model=IsARel)  # Represents "IS_A" relationship to another EMMOQuantity
    parameter = RelationshipFrom("matgraph.models.properties.Parameter", "IS_A",
                          model=IsARel)
    emmo_subclass = RelationshipTo('matgraph.models.ontology.EMMOQuantity', 'EMMO__IS_A',
                                   cardinality=ZeroOrMore)
    emmo_parentclass = RelationshipFrom('matgraph.models.ontology.EMMOQuantity', 'EMMO__IS_A',
                                      cardinality=ZeroOrMore)  # Represents the possibility of having zero or more subclasses.
    model_embedding = RelationshipFrom('matgraph.models.embeddings.QuantityEmbedding', 'FOR', cardinality=ZeroOrMore)



class EMMOMatter(OntologyNode):
    """
    Class representing EMMO matter in the knowledge graph. This node is also part of the European Materials Modelling
    Ontology (EMMO).
    """
    # Properties
    @classproperty
    def embedding(cls):
        """
        Returns the embedding of the node as a numpy array.
        :return: numpy array
        """
        return "matter-embeddings"




    class Meta:
        verbose_name_plural = 'EMMO Matter'  # Plural name for admin interface


    # Relationships
    is_a_material = RelationshipFrom('matgraph.models.matter.Material', "IS_A", model=IsARel, cardinality=ZeroOrMore)  # "IS_A" relationship from Matter model
    is_a_component = RelationshipFrom('matgraph.models.matter.Component', "IS_A", model=IsARel, cardinality=ZeroOrMore)
    is_a_device = RelationshipFrom('matgraph.models.matter.Device', "IS_A", model=IsARel, cardinality=ZeroOrMore)
    is_a_molecule = RelationshipFrom('matgraph.models.matter.Molecule', "IS_A", model=IsARel, cardinality=ZeroOrMore)

    model_embedding = RelationshipFrom('matgraph.models.embeddings.MatterEmbedding', 'FOR', cardinality=ZeroOrMore)
    # Relationships
    matter = RelationshipFrom("matgraph.models.matter.Matter", "IS_A",
                                 model=IsARel)

    emmo_subclass = RelationshipTo('matgraph.models.ontology.EMMOMatter', 'EMMO__IS_A',
                                   cardinality=ZeroOrMore)
    emmo_parentclass = RelationshipFrom('matgraph.models.ontology.EMMOMatter', 'EMMO__IS_A',
                                        cardinality=ZeroOrMore)



class EMMOProcess(OntologyNode):
    """
    Class representing EMMO process in the knowledge graph. This node is a component of the European Materials Modelling Ontology (EMMO).
    """
    @classproperty
    def embedding(cls):
        """
        Returns the embedding of the node as a numpy array.
        :return: numpy array
        """
        return "process-embeddings"
    class Meta:
        verbose_name_plural = 'EMMO Processes'  # Plural name for admin interface


    # Relationships

    is_a = RelationshipFrom('matgraph.models.processes.Process', "IS_A",
                            model=IsARel)  # "IS_A" relationship from Process model

    model_embedding = RelationshipFrom('matgraph.models.embeddings.ProcessEmbedding', 'FOR', cardinality=ZeroOrMore)

    emmo_subclass = RelationshipTo('matgraph.models.ontology.EMMOProcess', 'EMMO__IS_A',
                                   cardinality=ZeroOrMore)
    emmo_parentclass = RelationshipFrom('matgraph.models.ontology.EMMOProcess', 'EMMO__IS_A',
                                        cardinality=ZeroOrMore)  # Represents the possibility of having zero or more subclasses.
