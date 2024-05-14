"""
This module defines Django admin classes for the EMMOProcess and EMMOMatter models in the knowledge graph application.
These classes allow for the management of EMMOProcess and EMMOMatter instances in the Django admin interface.

EMMOProcessAdmin and EMMOMatterAdmin inherit from the NodeModelAdmin base class, which is a customized
ModelAdmin class for Neo4j node models. These classes define custom display options and save methods
for EMMOProcess and EMMOMatter instances in the Django admin interface.
"""

from django.contrib import admin as dj_admin

from graphutils.admin import NodeModelAdmin
from matgraph.models.ontology import EMMOProcess, EMMOMatter, EMMOQuantity


@dj_admin.register(EMMOProcess)
class EMMOProcessAdmin(NodeModelAdmin):
    """
    EMMOProcessAdmin is a Django admin class for managing EMMOProcess instances in the Django admin interface.
    Inherits from NodeModelAdmin, a customized ModelAdmin class for Neo4j node models.

    list_display: Specifies the fields to be displayed as columns on the change list page of the admin.
    actions: Specifies the actions available for the EMMOProcess instances in the admin interface.
    """
    list_display = ("name", "description")

    def save(self, commit=True):
        instance = super().save(commit)
        instance.save()

        return instance
    actions = ['delete_model']

@dj_admin.register(EMMOMatter)
class EMMOMatterAdmin(NodeModelAdmin):
    """
    EMMOMatterAdmin is a Django admin class for managing EMMOMatter instances in the Django admin interface.

    This class inherits from NodeModelAdmin, which is a customized ModelAdmin class for Neo4j node models.
    It provides a convenient way to display and manage EMMOMatter instances within the Django admin interface.

        list_display: Specifies the fields to be displayed as columns on the change list page of the admin.
        actions: Specifies the actions available for the EMMOMatter instances in the admin interface.
        save(commit=True): Overrides the save method to save the EMMOMatter instance in the database. The 'commit'
        parameter is a boolean indicating whether the instance should be saved to the database.
        """
    list_display = ("name", "description")

    def save(self, commit=True):
        instance = super().save(commit)
        instance.save()

        return instance
    actions = ['delete_model']


@dj_admin.register(EMMOQuantity)
class EMMOQuantityAdmin(NodeModelAdmin):

    list_display = ("name", "description")

    def save(self, commit=True):
        instance = super().save(commit)
        instance.save()

        return instance
    actions = ['delete_model']