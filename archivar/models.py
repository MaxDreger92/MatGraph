from django.db import models
from neomodel import RelationshipTo, ZeroOrOne, ZeroOrMore

from matgraph.models.processes import Process


# Create your models here.
class Experiment(Process):
    measurement = RelationshipTo('matgraph.models.processes.Measurement', 'HAS_PART', ZeroOrMore)
    sample = RelationshipTo('matgraph.models.matter.Matter', 'HAS_PART', ZeroOrMore)
    manufacturing = RelationshipTo('matgraph.models.processes.Manufacturing', 'HAS_PART', ZeroOrMore)

class Campaign(Process):
    experiment = RelationshipTo(Experiment, 'HAS_PART', ZeroOrMore)

    def __str__(self):
        return self.name