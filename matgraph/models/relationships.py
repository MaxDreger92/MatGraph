# knowledge_graph_relationships.py

from neomodel import StructuredRel, StringProperty, FloatProperty, IntegerProperty, ArrayProperty


# Researcher-related properties

class ByResearcherRel(StructuredRel):
    """
    Relationship between a research contribution and the researcher who made it.
    """
    CONTRIBUTION_LABEL_CHOICES = {
        'first_author': 'First Author',
        'author': 'Author',
        'conducted_experiment': 'Conducted Experiment',
        'instrument_scientist': 'Instrument Scientist',
        'contributor': 'Contributor',
        'planned_experiment': 'Planned Experiment'
    }
    label = StringProperty(choices=CONTRIBUTION_LABEL_CHOICES, default='contributor')


# Location-related properties

class InLocationRel(StructuredRel):
    """
    Relationship between an entity and its location.
    """
    test = StringProperty()


# Part-related properties

class HasPartRel(StructuredRel):
    """
    Relationship between a whole and its part.
    """
    pass

class HasPIDRel(StructuredRel):
    """
    Relationship between a whole and its part.
    """
    pass
# DirectPart properties

class DerivedFromRel(StructuredRel):
    """
    Relationship between a derived entity and its source entity.
    """
    pass


class IsProcessInputRel(StructuredRel):
    """
    Relationship between a process and its input entity.
    """
    pass


class IsManufacturingInputRel(IsProcessInputRel):
    """
    Relationship between a manufacturing process and its input entity.
    """
    pass


class IsMeasurementInputRel(IsProcessInputRel):
    """
    Relationship between a measurement process and its input entity.
    """
    pass


class IsManufacturingOutputRel(IsProcessInputRel):
    """
    Relationship between a manufacturing process and its output entity.
    """
    pass


class IsMeasurementOutputRel(IsProcessInputRel):
    """
    Relationship between a measurement process and its output entity.
    """
    pass


# hasParticipant properties

class HasValueRel(StructuredRel):
    """
    Abstract relationship between a property and its value.
    """
    float_value = FloatProperty()
    integer_value = IntegerProperty()
    array_value = ArrayProperty()
    float_error = FloatProperty()
    integer_error = IntegerProperty()
    array_error = ArrayProperty()
    float_accuracy = FloatProperty()
    integer_accuracy = IntegerProperty()
    array_accuracy = ArrayProperty()
    float_std = FloatProperty()
    integer_std = IntegerProperty()
    array_std = ArrayProperty()
    pass


class HasParameterRel(HasValueRel):
    """
    Relationship between a process and its parameter.
    """
    pass


class HasPropertyRel(HasValueRel):
    """
    Relationship between an entity and its property.
    """
    pass


# hasProcessOutput properties

class HasProcessOutputRel(StructuredRel):
    """
    Relationship between a process and its output entity.
    """
    pass


class HasManufacturingOutputRel(HasProcessOutputRel):
    """
    Relationship between a manufacturing process and its output entity.
    """
    pass


class HasMeasurementOutputRel(HasProcessOutputRel):
    """
    Relationship between a measurement process and its output entity.
    """
    pass

class HasFileOutputRel(HasProcessOutputRel):
    """
    Relationship between a process and its output file.
    """
    pass

# Other relationships

class FollowedByRel(StructuredRel):
    """
    Relationship between two entities in a sequence.
    """
    pass

class ByRel(StructuredRel):
    """
    Relationship between data and its metadata.
    """
    pass

class ResearcherOwnsRel(StructuredRel):
    """
    Relationship between data and its metadata.
    """
    pass

class EmmoIsARel(StructuredRel):
    """
    Relationship between two entities where one is a subtype of the other in the EMMO ontology.
    """
    pass


class IsARel(StructuredRel):
    """
    Relationship between two entities where one is a subtype of the other.
    """
    pass
