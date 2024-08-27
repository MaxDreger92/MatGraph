from neomodel import (RelationshipTo, StringProperty, RelationshipFrom,
                      BooleanProperty, OneOrMore, ZeroOrMore, DateTimeProperty)

from matgraph.models.abstractclasses import CausalObject
from matgraph.models.matter import Material, Molecule, Component, Device
from matgraph.models.relationships import (ByResearcherRel, ByRel,
                                             HasFileOutputRel, IsManufacturingInputRel,
                                             HasMeasurementOutputRel, HasPartRel,
                                             IsManufacturingOutputRel, IsARel, HasParameterRel, IsMeasurementInputRel)


class Process(CausalObject):
    """
    Abstract base class representing processes in the knowledge graph.
    """
    # Organizational Data
    run_title = StringProperty(unique=True)
    run_id = StringProperty(unique=True)
    time_started = DateTimeProperty()
    time_completed = DateTimeProperty()
    public_access = BooleanProperty()

    # Relationships
    is_a = RelationshipTo('matgraph.models.ontology.EMMOProcess', "IS_A",
                          model=IsARel, cardinality=ZeroOrMore)
    parameter = RelationshipTo('matgraph.models.properties.Parameter', "HAS_PARAMETER",
                               model=HasParameterRel, cardinality=ZeroOrMore)
    researcher = RelationshipTo('matgraph.models.metadata.Metadata', "BY",
                                model=ByResearcherRel, cardinality=ZeroOrMore)
    instrument = RelationshipTo('matgraph.models.metadata.Instrument', "BY_INSTRUMENT",
                                model=ByRel, cardinality=ZeroOrMore)
    subprocess_measurement = RelationshipTo("Measurement", "HAS_PART",
                                            model=HasPartRel, cardinality=ZeroOrMore)
    next_step_measurement = RelationshipTo("Measurement", "HAS_PART",
                                           model=HasPartRel, cardinality=ZeroOrMore)
    subprocess_manufacturing = RelationshipTo("Manufacturing", "HAS_PART",
                                              model=HasPartRel, cardinality=ZeroOrMore)
    next_step_manufacturing = RelationshipTo("Manufacturing", "HAS_PART",
                                             model=HasPartRel, cardinality=ZeroOrMore)
    publication = RelationshipTo('matgraph.models.metadata.Publication', "PUBLISHED_IN",
                                 model=HasPartRel, cardinality=ZeroOrMore)
    institution = RelationshipTo('matgraph.models.metadata.Institution', "PUBLISHED_IN",
                                 model=HasPartRel, cardinality=ZeroOrMore)

    class Meta:
        app_label = 'matgraph'


class Manufacturing(Process):
    """
    Class representing manufacturing processes in the knowledge graph.
    """

    def __str__(self):
        if self.name:
            return f"Manufacturing {self.name} with uid {self.uid}"
        return f"Manufacturing with uid {self.uid}"

    material_output = RelationshipTo(Material, 'IS_MANUFACTURING_OUTPUT', model=IsManufacturingOutputRel)
    molecule_output = RelationshipTo(Molecule, 'IS_MANUFACTURING_OUTPUT', model=IsManufacturingOutputRel)
    component_output = RelationshipTo(Component, 'IS_MANUFACTURING_OUTPUT', model=IsManufacturingOutputRel)
    device_output = RelationshipTo(Device, 'IS_MANUFACTURING_OUTPUT', model=IsManufacturingOutputRel)

    material_input = RelationshipFrom('matgraph.models.matter.Material', 'IS_MANUFACTURING_INPUT',
                                      model=IsManufacturingInputRel, cardinality=ZeroOrMore)
    molecule_input = RelationshipFrom('matgraph.models.matter.Molecule', "IS_MANUFACTURING_INPUT",
                                      model=IsManufacturingInputRel, cardinality=ZeroOrMore)
    component_input = RelationshipFrom('matgraph.models.matter.Component', "IS_MANUFACTURING_INPUT",
                                       model=IsManufacturingInputRel, cardinality=ZeroOrMore)
    device_input = RelationshipFrom('matgraph.models.matter.Device', "IS_MANUFACTURING_INPUT",
                                    model=IsManufacturingInputRel, cardinality=ZeroOrMore)

class Measurement(Process):
    """
    Class representing measurement processes in the knowledge graph.
    """
    def __str__(self):
        return "Measurement " + self.uid

    property_output = RelationshipTo('matgraph.models.properties.Property', "HAS_MEASUREMENT_OUTPUT",
                                     model=HasMeasurementOutputRel, cardinality=OneOrMore)
    file_output = RelationshipTo('matgraph.models.metadata.File', "HAS_FILE_OUTPUT",
                                 model=HasFileOutputRel, cardinality=ZeroOrMore)

    material_input = RelationshipFrom('matgraph.models.matter.Material', 'IS_MEASUREMENT_INPUT',
                                      model=IsMeasurementInputRel, cardinality=ZeroOrMore)
    molecule_input = RelationshipFrom('matgraph.models.matter.Molecule', "IS_MEASUREMENT_INPUT",
                                      model=IsMeasurementInputRel, cardinality=ZeroOrMore)
    component_input = RelationshipFrom('matgraph.models.matter.Component', "IS_MEASUREMENT_INPUT",
                                       model=IsMeasurementInputRel, cardinality=ZeroOrMore)
    device_input = RelationshipFrom('matgraph.models.matter.Device', "IS_MEASUREMENT_INPUT",
                                    model=IsMeasurementInputRel, cardinality=ZeroOrMore)


class Simulation(Process):
    """
    Class representing measurement processes in the knowledge graph.
    """
    def __str__(self):
        return "Simulation " + self.uid
    property_output = RelationshipTo('matgraph.models.properties.Property', "HAS_SIMULATION_OUTPUT",
                                         model=HasMeasurementOutputRel, cardinality=OneOrMore)
    file_output = RelationshipTo('matgraph.models.metadata.File', "HAS_FILE_OUTPUT",
                                 model=HasFileOutputRel, cardinality=ZeroOrMore)
    file_input = RelationshipFrom('matgraph.models.metadata.File', "HAS_FILE_INPUT",
                                 model=HasFileOutputRel, cardinality=ZeroOrMore)

    material_input = RelationshipFrom('matgraph.models.matter.Material', 'IS_MEASUREMENT_INPUT',
                                      model=IsMeasurementInputRel, cardinality=ZeroOrMore)
    molecule_input = RelationshipFrom('matgraph.models.matter.Molecule', "IS_MEASUREMENT_INPUT",
                                      model=IsMeasurementInputRel, cardinality=ZeroOrMore)
    component_input = RelationshipFrom('matgraph.models.matter.Component', "IS_MEASUREMENT_INPUT",
                                       model=IsMeasurementInputRel, cardinality=ZeroOrMore)
    device_input = RelationshipFrom('matgraph.models.matter.Device', "IS_MEASUREMENT_INPUT",
                                    model=IsMeasurementInputRel, cardinality=ZeroOrMore)

class DataProcessing(Process):
    """
    Class representing measurement processes in the knowledge graph.
    """
    def __str__(self):
        return "DataProcessing " + self.uid

    is_a = None
    property_output = RelationshipTo('matgraph.models.properties.Property', "HAS_SIMULATION_OUTPUT",
                                     model=HasMeasurementOutputRel, cardinality=OneOrMore)
    file_output = RelationshipTo('matgraph.models.metadata.File', "HAS_FILE_OUTPUT",
                                 model=HasFileOutputRel, cardinality=ZeroOrMore)
    file_input = RelationshipFrom('matgraph.models.metadata.File', "HAS_FILE_INPUT",
                                  model=HasFileOutputRel, cardinality=ZeroOrMore)
