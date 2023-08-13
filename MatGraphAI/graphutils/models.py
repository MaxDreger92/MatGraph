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
    ZeroOrOne
from neomodel.properties import validator, BooleanProperty


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


class UploadedFilesList(list):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def upload(self, upload):
        self.append(UploadedFile(upload.file, upload.name))

    @classmethod
    def from_future_attachments(cls, attachments):
        from attachments.models import FutureAttachment

        ufl = cls()

        for att in attachments:
            att = FutureAttachment.objects.get(id=att['id'])
            ufl.append(UploadedFile(att.file.name, att.name))
            att.keep_file = True  # make sure file is not deleted when FutureAttachment is deleted
            att.save()

        return ufl


class UploadedFileProperty(JSONProperty):

    @validator
    def inflate(self, value):
        return UploadedFile._from_json(value)

    @validator
    def deflate(self, value):
        return value._to_json()


class FileUploadProperty(ArrayProperty):

    def __init__(self, *args, **kwargs):
        kwargs['base_property'] = UploadedFileProperty()
        kwargs['default'] = UploadedFilesList()
        super().__init__(*args, **kwargs)

    @validator
    def inflate(self, value):
        return UploadedFilesList(super().inflate(value))


class AlternativeLabel(DjangoNode):

    element = RelationshipFrom('graphutils.models.AlternativeLabel', 'HAS_LABEL', ZeroOrOne)

    label = StringProperty(required=True)
    primary = BooleanProperty(default=False)
    type = StringProperty(required=False)
    language = StringProperty(required=False)