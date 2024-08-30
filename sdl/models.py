import os
import uuid
from datetime import datetime
from django.db import models
from neomodel import UniqueIdProperty, FloatProperty, StringProperty, RelationshipTo, IntegerProperty, DateTimeProperty, \
    RelationshipFrom

from neomodel import db
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from matgraph.models.metadata import Metadata
from matgraph.models.relationships import HasPartRel, InLocationRel


# Create your models here.

class Well(BaseModel):
    depth: float
    totalLiquidVolume: float
    shape: str
    diameter: Optional[float] = None
    xDimension: Optional[float] = None
    yDimension: Optional[float] = None
    x: float
    y: float
    z: float


class Module(BaseModel):
    ordering: List[List[str]]
    brand: Dict[str, Any]
    metadata: Dict[str, Any]
    dimensions: Dict[str, float]
    wells: Dict[str, Well]
    groups: List[Dict[str, Any]]
    parameters: Dict[str, Any]
    namespace: str
    version: int
    schemaVersion: int
    cornerOffsetFromSlot: Dict[str, float]

    @classmethod
    def from_json(cls, data: Dict[str, Any]):
        wells_data = {well_id: Well(**well_attr) for well_id, well_attr in data.pop('wells').items()}
        return cls(wells=wells_data, **data)


class Well(Metadata):
    uid = UniqueIdProperty()
    depth = FloatProperty()
    totalLiquidVolume = FloatProperty()
    shape = StringProperty()
    diameter = FloatProperty()
    xDimension = FloatProperty()
    yDimension = FloatProperty()
    x = FloatProperty()
    y = FloatProperty()
    z = FloatProperty()
    well_id = StringProperty()

    def __str__(self):
        return f"Well {self.uid}"

    class Meta(Metadata.Meta):
        pass


class Opentron_Module(Metadata):
    """
    Abstract base class representing a Module in the knowledge graph.

    name: The name of the module.
    """
    name = StringProperty()
    date_added = StringProperty(required=True)
    wells = RelationshipTo('Well', 'HAS_PART', model=HasPartRel)
    module_id = StringProperty(unique=True)

    def __str__(self):
        return self.name

    @classmethod
    def from_json(cls, data: Dict[str, Any]):
        module_instance = cls(name=data["metadata"]["displayName"], date_added="2024-07-13")
        module_instance.save()

        wells_data = data.pop('wells')
        for well_id, well_attr in wells_data.items():
            well_instance = Well(well_id=well_id, **well_attr)
            well_instance.save()
            module_instance.wells.connect(well_instance)

        return module_instance

    def add_slot(self, ExperimentID, slot):
        query = f'''
            MATCH (o:Opentrons {{setup_id: '{ExperimentID}'}})-[:HAS_PART]->(s:Slot {{number: '{str(slot)}'}})
            MATCH (m:Opentron_Module {{uid: '{self.uid}'}})
            WITH DISTINCT s, m
            CREATE (m)<-[:HAS_PART]-(s)
        '''
        res, _ = db.cypher_query(query, {})

    class Meta(Metadata.Meta):
        pass

class Pipette(Opentron_Module):
    pass


class Slot(Metadata):
    number = StringProperty(unique=True, required=True)

    def __str__(self):
        return f"Slot {self.number}"


class Opentrons(Metadata):
    setup_id = StringProperty(unique=True, required=True)
    date_added = DateTimeProperty(default=datetime.now())
    slots = RelationshipTo('Slot', 'HAS_PART', model=HasPartRel)
    pipettes = RelationshipTo('Pipette', 'HAS_PART', model=HasPartRel)

    def save(self):
        super().save()
        for i in range(1, 13):
            slot = Slot(number=str(i))
            slot.save()
            self.slots.connect(slot)

    def __str__(self):
        return f"Opentron_O2 {self.experiment_id}"

    class Meta(Metadata.Meta):
        pass


class ArduinoModule(Metadata):
    setup_id = StringProperty(unique=True, required=True)
    date_added = DateTimeProperty(default=datetime.now())
    relay = RelationshipTo('Relay', 'HAS_PART', model=HasPartRel)
    cartridge = RelationshipTo('Slot', 'HAS_PART', model=HasPartRel)

    def __str__(self):
        return f"ArduinoModule {self.experiment_id}"

    class Meta(Metadata.Meta):
        pass


class ArduinoBoard(Metadata):
    date_added = DateTimeProperty(default=datetime.now())
    relay = RelationshipTo('Relay', 'HAS_PART', model=HasPartRel)
    cartridge = RelationshipTo('Slot', 'HAS_PART', model=HasPartRel)
    baud_rate = IntegerProperty()
    port = StringProperty()

    def __str__(self):
        return f"ArduinoSetup {self.experiment_id}"

    class Meta(Metadata.Meta):
        pass


class Relay(Metadata):
    relay_id = StringProperty(required=True)
    name = StringProperty(required=True)
    device = RelationshipTo('Metadata', 'HAS_PART', model=HasPartRel)


class Pump(Metadata):
    name = StringProperty(required=True)
    pump_slope = FloatProperty()
    pump_intercept = FloatProperty()
    device = RelationshipTo('matgraph.models.metadata.Metadata', 'HAS_PART', model=HasPartRel)
    inlet = RelationshipTo('matgraph.models.metadata.Metadata', 'HAS_PART', model=HasPartRel)
    outlet = RelationshipTo('matgraph.models.metadata.Metadata', 'HAS_PART', model=HasPartRel)

    slope = FloatProperty()
    intercept = FloatProperty()


class Ultrasonic(Metadata):
    name = StringProperty(required=True)
    device = RelationshipTo('Metadata', 'HAS_PART', model=HasPartRel)
    slot = RelationshipTo('Metadata', 'HAS_PART', model=HasPartRel)
    connected_to = RelationshipTo('Metadata', 'HAS_PART', model=HasPartRel)


class Reservoir(Metadata):
    name = StringProperty(required=True)
    device = RelationshipTo('Metadata', 'HAS_PART', model=HasPartRel)
    slot = RelationshipTo('Metadata', 'HAS_PART', model=HasPartRel)
    connected_to = RelationshipTo('Metadata', 'HAS_PART', model=HasPartRel)
    material = RelationshipFrom('matgraph.models.matter.Matter', 'IN', model=InLocationRel)
    volume = FloatProperty()
    unit = StringProperty()


class Biologic(Metadata):
    name = StringProperty(default="Biologic Setup")
    device = RelationshipTo('Metadata', 'HAS_PART', model=HasPartRel)
    slot = RelationshipFrom('matgraph.models.metadata.Metadata', 'HAS_PART', model=HasPartRel)
    connected_to = RelationshipTo('Metadata', 'HAS_PART', model=HasPartRel)
    material = RelationshipFrom('matgraph.models.matter.Matter', 'IN', model=InLocationRel)
    volume = FloatProperty()
    unit = StringProperty()


class ExperimentModel(models.Model):
    STATUS_CHOICES = [("queued", 'QUEUED'), ("running", 'RUNNING'), ("completed", 'COMPLETED'), ("failed", 'FAILED')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    opentrons = models.JSONField()
    labware = models.JSONField()
    chemicals = models.JSONField()
    biologic = models.JSONField(null=True, blank=True)  # Allow NULL and empty values
    arduino = models.JSONField(null=True, blank=True)  # Allow NULL and empty values
    arduino_relays = models.JSONField(null=True, blank=True)  # Allow NULL and empty values
    workflow = models.JSONField()
    status = models.CharField(choices=STATUS_CHOICES, default="queued")
    description = models.TextField(null=True, blank=True)  # Allow NULL and empty values
    remarks = models.TextField(null=True, blank=True)  # Allow NULL and empty values
    results = models.JSONField(null=True, blank=True)  # Allow NULL and empty values

    def __str__(self):
        """Return a readable representation of the importing report."""
        return f'Queued Experiment ({self.id}, {self.date_created})'