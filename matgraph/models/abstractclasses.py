"""
This module contains Django-Neo4j node model classes for a knowledge graph application.

UIDDjangoNode is an abstract base class that provides a unique identifier (uid) as the primary key for
DjangoNode instances. It also includes an alias property to handle the Django primary key (pk) field,
which is commonly used in Django applications.

UniqueNode is another abstract base class for unique nodes in a Django-Neo4j graph, which also includes
a uid as a unique identifier.

CausalObject is an abstract base class representing causal objects in the knowledge graph. It inherits
from UIDDjangoNode and contains properties for the name and the date the object was added to the knowledge graph.

OntologyNode is an abstract base class representing ontology nodes in the knowledge graph. It inherits
from UIDDjangoNode and contains properties for the name, URI, description, and alternative_label relationship
of the ontology node according to the EMMO (European Materials & Modelling Ontology).
"""

from django.apps import apps
from django_neomodel import DjangoNode, classproperty
from neomodel import AliasProperty, StringProperty, UniqueIdProperty, RelationshipTo, ZeroOrMore, \
    RelationshipFrom, BooleanProperty

from graphutils.models import EmbeddingNodeSet, UIDDjangoNode


class CausalObject(UIDDjangoNode):
    """
    Abstract base class representing causal objects in the knowledge graph.

    name: The name of the causal object.
    date_added: The date the causal object was added to the knowledge graph.
    """
    name = StringProperty()
    __abstract_node__ = True

    date_added = StringProperty(required=True)

    def __str__(self):
        return self.name


class OntologyNode(UIDDjangoNode):
    """
    Abstract base class representing ontology nodes in the knowledge graph.

    name: The name of the ontology node according to the EMMO.
    uri: The unique URI of the ontology node according to the EMMO.
    """
    @classproperty
    def nodes(cls):
        return EmbeddingNodeSet(cls)




    def get_subclasses(self, uids):
        prompt = f"""
        // Part 1: Return details of `n`
        MATCH (n:{self._meta.object_name})
        WHERE n.uid IN {uids}
        RETURN n.uid AS uid, n.name AS name
        UNION ALL
        // Part 2: Return details of `m`
        MATCH (n:{self._meta.object_name})<-[:EMMO__IS_A*]-(m)
        WHERE n.uid IN {uids}
        RETURN DISTINCT m.uid AS uid, m.name AS name
        """
        results, meta = self.cypher(prompt)
        return [(node[0], node[1]) for node in results]
    def get_superclasses(self, uids):
        prompt = f"""
        // Part 1: Return details of `n`
        MATCH (n:{self._meta.object_name})
        WHERE n.uid IN {uids}
        RETURN n.uid AS uid, n.name AS name
        UNION ALL
        // Part 2: Return details of `m`
        MATCH (n:{self._meta.object_name})-[:EMMO__IS_A*]->(m)
        WHERE n.uid IN {uids}
        RETURN DISTINCT m.uid AS uid, m.name AS name
        """
        results, meta = self.cypher(prompt)
        return [(node[0], node[1]) for node in results]



    name = StringProperty()
    uri = StringProperty()
    description = StringProperty()
    alternative_label =RelationshipTo('graphutils.models.AlternativeLabel', 'HAS_LABEL', cardinality=ZeroOrMore)
    model_embedding = RelationshipFrom('matgraph.models.embeddings.ModelEmbedding', 'FOR', cardinality=ZeroOrMore)
    validated_labels = BooleanProperty(default = False)
    validated_ontology = BooleanProperty(default = False)
    __abstract_node__ = True

    def __str__(self):
        return self.name


