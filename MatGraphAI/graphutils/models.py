"""
The graphutils library contains classes that are needed to extend the django functionality on neo4j.

graphutils model classes:
 - AlternativeLabelMixin
 - FileUploadProperty
 - LabeledDjangoNode
 - UIDDjangoNode
 - UploadFile
 - UploadFileProperty
 - UploadFileList
"""

import json
import uuid

from django.apps import apps

from django_neomodel import DjangoNode, classproperty
from neomodel import UniqueIdProperty, StringProperty, ArrayProperty, AliasProperty, JSONProperty, RelationshipFrom, \
    ZeroOrOne, NodeSet, StructuredNode
from neomodel.properties import validator, BooleanProperty
from neomodel import db

from graphutils.embeddings import request_embedding


class EmbeddingNodeSet(NodeSet):
    def __init__(self, cls):
        super().__init__(cls)


    def _get_by_embedding(self, include_similarity, include_input_string, **kwargs):

        #TODO: Needs to have big numbers for limit
        query = """
            CALL db.index.vector.queryNodes($embedding, 15, $vector)
            YIELD node AS similarEmbedding, score
            MATCH (similarEmbedding)-[:FOR]->(n)
            WITH n, similarEmbedding.input AS input, score
            ORDER BY score DESC
            WITH n, COLLECT(input)[0] AS mostRelevantInput, MAX(score) AS highestScore
            RETURN n AS title, highestScore AS score, mostRelevantInput AS similarEmbedding
            ORDER BY highestScore DESC
            LIMIT $limit
        """
        kwargs['embedding'] = self.source_class.embedding

        # db.cypher_query(query, {'embedding': embedding, 'topN': limit, 'vector': vector})[0][0]
        # if limit:
        #     self.limit = limit
        #
        # return self.query_cls(self).build_ast()._execute(False)

        results, _ = db.cypher_query(query, kwargs, resolve_objects=True)

        # The following is not as elegant as it could be but had to be copied from the
        # version prior to cypher_query with the resolve_objects capability.
        # It seems that certain calls are only supposed to be focusing to the first
        # result item returned (?)
        if results:
            if include_similarity and include_input_string:
                return [[n[0], n[1], n[2]] for n in results]
            elif include_similarity:
                return [[n[0], n[1]] for n in results]
            elif include_input_string:
                return [[n[0], n[2]] for n in results]

            else:
                return [n[0] for n in results]
        return []


    def get_by_embedding(self, include_similarity = False, include_input_string = False, **kwargs):
        """
        Retrieve one node from the set matching supplied parameters
        :param lazy: False by default, specify True to get nodes with id only without the parameters.
        :param kwargs: same syntax as `filter()`
        :return: node
        """
        result = self._get_by_embedding(include_similarity, include_input_string, **kwargs)
        return result


    def get_by_string(self, include_similarity = False, include_input_string = False, **kwargs):
        """
        Retrieve one node from the set matching supplied parameters
        :param lazy: False by default, specify True to get nodes with id only without the parameters.
        :param kwargs: same syntax as `filter()`
        :return: node
        """
        kwargs["vector"] = request_embedding(kwargs['string'])
        result = self._get_by_embedding(include_similarity, include_input_string, **kwargs)
        return result


class UIDDjangoNode(DjangoNode):
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


class LabeledDjangoNode(UIDDjangoNode):
    label = StringProperty(
        required=True
    )

    __abstract_node__ = True

    def __str__(self):
        return str(self.label)


class AlternativeLabelMixin:
    alternative_labels = ArrayProperty(
        StringProperty(),
        required=False,
        index=True
    )


class QuotaMixin:
    @property
    def quota(self):
        return {'min': self.min_quota, 'max': self.max_quota}


class UploadedFile:

    def __init__(self, file, name, uid=uuid.uuid4().hex):
        self.uid = uid
        self.name = name
        self.file = file

    def __str__(self):
        return self.name

    @classmethod
    def _from_json(cls, data):
        data = json.loads(data)
        return cls(data['file'], data['name'], data['uid'])

    def _to_json(self):
        return json.dumps({
            'uid': self.uid,
            'name': self.name,
            'file': self.file
        })





class UploadedFileProperty(JSONProperty):

    @validator
    def inflate(self, value):
        return UploadedFile._from_json(value)

    @validator
    def deflate(self, value):
        return value._to_json()





class AlternativeLabel(DjangoNode):

    element = RelationshipFrom('graphutils.models.AlternativeLabel', 'HAS_LABEL', ZeroOrOne)

    label = StringProperty(required=True)
    primary = BooleanProperty(default=False)
    type = StringProperty(required=False)
    language = StringProperty(required=False)



from django.db import models
from neo4j import GraphDatabase

