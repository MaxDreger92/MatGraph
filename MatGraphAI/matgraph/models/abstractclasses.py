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
import ast
import json

from django_neomodel import DjangoNode, classproperty
from neomodel import AliasProperty, StringProperty, UniqueIdProperty, ArrayProperty, RelationshipTo, ZeroOrMore, \
    RelationshipFrom, BooleanProperty
from django.apps import apps

from dbcommunication.ai.setupMessages import MATTER_ONTOLOGY_ASSISTANT_MESSAGES, PROCESS_ONTOLOGY_ASSISTANT_MESSAGES, \
    QUANTITY_ONTOLOGY_ASSISTANT_MESSAGES, QUANTITY_ONTOLOGY_CONNECTOR_MESSAGES, PROCESS_ONTOLOGY_CONNECTOR_MESSAGES, \
    MATTER_ONTOLOGY_CONNECTOR_MESSAGES, MATTER_ONTOLOGY_CANDIDATES_MESSAGES, PROCESS_ONTOLOGY_CANDIDATES_MESSAGES, \
    QUANTITY_ONTOLOGY_CANDIDATES_MESSAGES
from graphutils.embeddings import request_embedding
from graphutils.models import EmbeddingNodeSet, AlternativeLabel
from importing.utils.openai import chat_with_gpt4
from matgraph.models.embeddings import QuantityEmbedding, ProcessEmbedding, MatterEmbedding


class UIDDjangoNode(DjangoNode):
    """
    UIDDjangoNode is an abstract base class for Django-Neo4j nodes that provides a unique identifier (uid)
    as the primary key for DjangoNode instances. It inherits from DjangoNode, which is a base class for
    Neo4j nodes that are compatible with Django.

    The class defines a UniqueIdProperty, 'uid', which serves as the primary key for instances of the class.
    The 'abstract_node' attribute is set to True to ensure that UIDDjangoNode is only used as a base class.

    The _meta method is a class property that sets the app_label and alias property for the primary key (pk) used
    in Django applications. The primary key (pk) is aliased to the 'uid' property using AliasProperty. This ensures
    that Django admin and other parts of the Django framework that use .pk can work seamlessly with this class.

    The Meta class is defined as a nested class inside UIDDjangoNode but left empty. It can be used by subclasses
    to set additional metadata options.
    """
    uid = UniqueIdProperty(
        primary_key=True
    )

    __abstract_node__ = True

    # django (esp. admin) uses .pk in a few places and expects a UUID.
    # add an AliasProperty to handle this
    @classproperty
    def _meta(self):
        self.Meta.app_label = apps.get_containing_app_config(self.__module__).label
        opts = super()._meta
        self.pk = AliasProperty(to='uid')
        return opts

    class Meta:
        pass




    def __hash__(self):
        """
        Computes the hash value of the UIDDjangoNode instance based on its unique identifier (uid).

        Raises a TypeError if the uid is not set.
        """
        if self.uid is None:
            raise TypeError("Model instances without primary key value are unhashable")
        return hash(self.uid)


class UniqueNode(DjangoNode):
    """
    Abstract base class for unique nodes in a Django-Neo4j graph.

    uid: A unique identifier property.
    """
    uid = UniqueIdProperty()
    __abstract_node__ = True

    @classmethod
    def category(cls):
        pass


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

    ONTOLOGY_MAPPER = {
        'EMMOMatter': MATTER_ONTOLOGY_ASSISTANT_MESSAGES,
        'EMMOProcess': PROCESS_ONTOLOGY_ASSISTANT_MESSAGES,
        'EMMOQuantity': QUANTITY_ONTOLOGY_ASSISTANT_MESSAGES
    }

    EMBEDDING_MODEL_MAPPER = {
        'EMMOMatter': MatterEmbedding,
        'EMMOProcess': ProcessEmbedding,
        'EMMOQuantity': QuantityEmbedding
    }



    ONTOLOGY_CANDIDATES = {
        'EMMOMatter': MATTER_ONTOLOGY_CANDIDATES_MESSAGES,
        'EMMOProcess': PROCESS_ONTOLOGY_CANDIDATES_MESSAGES,
        'EMMOQuantity': QUANTITY_ONTOLOGY_CANDIDATES_MESSAGES
    }

    ONTOLOGY_CONNECTOR = {
        'EMMOMatter': MATTER_ONTOLOGY_CONNECTOR_MESSAGES,
        'EMMOProcess': PROCESS_ONTOLOGY_CONNECTOR_MESSAGES,
        'EMMOQuantity': QUANTITY_ONTOLOGY_CONNECTOR_MESSAGES
    }

    def save(self, add_labels_create_embeddings = True, connect_to_onotlogy = True, *args, **kwargs):
        super().save()

        if add_labels_create_embeddings:
            alternative_labels = chat_with_gpt4(prompt= self.name, setup_message= self.ONTOLOGY_MAPPER[self._meta.object_name])
            alternative_labels = json.loads(alternative_labels)
            for label in alternative_labels['alternative_labels']:
                alternative_label_node = AlternativeLabel(label = label).save()
                self.alternative_label.connect(alternative_label_node)
                embedding = request_embedding(label)
                embedding_node = self.EMBEDDING_MODEL_MAPPER[self.__label__](vector = embedding, input = label).save()
                self.model_embedding.connect(embedding_node)
            embedding_node = self.EMBEDDING_MODEL_MAPPER[self.__label__](vector = request_embedding(self.name), input = self.name).save()
            self.model_embedding.connect(embedding_node)
            self.validated_labels = False
        if connect_to_onotlogy:
            self.connect_to_ontology()

    def connect_to_ontology(self):
        if len(self.emmo_subclass) == 0 and len(self.emmo_parentclass) == 0:
            candidates = self.find_candidates()
            find_connection = self.find_connection(candidates)
            print("Find Connection", find_connection)


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

    def find_candidates(self):
        nodes = self.nodes.get_by_string(string = self.name, limit = 8, include_similarity = False)
        prompt = f"""Input: {self.name}\nCandidates: {", ".join([node.name for node in nodes if node.name != self.name])} \nOnly return the final output!"""
        ontology_advice = chat_with_gpt4(prompt= prompt, setup_message= self.ONTOLOGY_CANDIDATES[self._meta.object_name])
        if ontology_advice.lower().strip(" ").strip("\n") == "false":
            uids = list(dict.fromkeys([node.uid for node in nodes if node.name != self.name]))
            return self.get_superclasses(uids)
        else:
            gpt_json = json.loads(ontology_advice.replace("\n", ""))
            if gpt_json['input_is_subclass_of_candidate']:
                candidate_uid = nodes[[node.name for node in nodes].index(gpt_json['candidate'])].uid
                return self.get_subclasses([candidate_uid])
            else:
                candidate_uid = nodes[[node.name for node in nodes].index(gpt_json['candidate'])].uid
                return self.get_superclasses([candidate_uid])

    def find_connection(self, candidates):
        prompt = f"""Input: {self.name}\nCandidates: {", ".join([candidate[1] for candidate in candidates])} \nOnly Return The Final List!"""
        connecting_path = chat_with_gpt4(prompt= prompt, setup_message= self.ONTOLOGY_CONNECTOR[self._meta.object_name])
        return ast.literal_eval(connecting_path)



    def add_labels_create_embeddings(self):
        alternative_labels = chat_with_gpt4(prompt= self.name, setup_message= self.ONTOLOGY_MAPPER[self._meta.object_name])
        alternative_labels = json.loads(alternative_labels)
        for label in alternative_labels['alternative_labels']:
            alternative_label_node = AlternativeLabel(label = label).save()
            self.alternative_label.connect(alternative_label_node)
            embedding = request_embedding(label)
            embedding_node = self.EMBEDDING_MODEL_MAPPER[self.__label__](vector = embedding, input = label).save()
            self.model_embedding.connect(embedding_node)
        embedding_node = self.EMBEDDING_MODEL_MAPPER[self.__label__](vector = request_embedding(self.name), input = self.name).save()
        self.model_embedding.connect(embedding_node)


    name = StringProperty()
    uri = StringProperty()
    description = StringProperty()
    alternative_label =RelationshipTo('graphutils.models.AlternativeLabel', 'HAS_LABEL', cardinality=ZeroOrMore)
    model_embedding = RelationshipFrom('matgraph.models.embeddings.ModelEmbedding', 'FOR', cardinality=ZeroOrMore)
    validated_labels = BooleanProperty()
    validated_ontology = BooleanProperty()
    __abstract_node__ = True

    def __str__(self):
        return self.name


