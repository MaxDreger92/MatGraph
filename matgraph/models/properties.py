from neomodel import RelationshipTo, RelationshipFrom
from matgraph.models.abstractclasses import CausalObject


class PhysicalDimension(CausalObject):
    """
    Class representing a physical dimension in the knowledge graph.
    """
    class Meta:
        app_label = 'matgraph'



class Property(PhysicalDimension):
    """
    Class representing a property in the knowledge graph.
    """
    class Meta:
        verbose_name_plural = 'properties'
        app_label = 'matgraph'

    derived_property = RelationshipTo('Property', "derivedFrom")
    property = RelationshipFrom('matgraph.models.processes.Measurement', "YIELDS_PROPERTY")

    pass


class Parameter(PhysicalDimension):
    """
    Class representing a parameter in the knowledge graph.
    """
    parameter = RelationshipFrom('matgraph.models.processes.Process', "HAS_PARAMETER")

    pass
