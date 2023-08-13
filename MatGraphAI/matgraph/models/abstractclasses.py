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
from django_neomodel import DjangoNode, classproperty
from neomodel import AliasProperty, StringProperty, UniqueIdProperty, ArrayProperty, RelationshipTo, ZeroOrMore
from django.apps import apps


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
    name = StringProperty()
    uri = StringProperty()
    description = StringProperty()
    alternative_label =RelationshipTo('graphutils.models.AlternativeLabel', 'HAS_LABEL', cardinality=ZeroOrMore)
    __abstract_node__ = True

    def __str__(self):
        return self.name


