from neomodel import RelationshipTo, RelationshipFrom, StringProperty, FloatProperty, JSONProperty
from matgraph.models.abstractclasses import CausalObject


class PhysicalQuantity(CausalObject):
    """
    Class representing a physical dimension in the knowledge graph.
    """
    unit = StringProperty()
    value = FloatProperty()
    dataframe_json = JSONProperty()
    is_a = RelationshipTo('matgraph.models.ontology.EMMOQuantity', "IS_A")
    class Meta:
        app_label = 'matgraph'



class Property(PhysicalQuantity):
    """
    Class representing a property in the knowledge graph.
    """
    class Meta:
        verbose_name_plural = 'properties'
        app_label = 'matgraph'

    derived_property = RelationshipTo('Property', "derivedFrom")
    property = RelationshipFrom('matgraph.models.processes.Measurement', "YIELDS_PROPERTY")

    pass


class Parameter(PhysicalQuantity):
    """
    Class representing a parameter in the knowledge graph.
    """
    parameter = RelationshipFrom('matgraph.models.processes.Process', "HAS_PARAMETER")

    pass
