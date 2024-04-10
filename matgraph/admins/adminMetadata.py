"""
This module defines the admin classes for the Instrument, Researcher, and Institution models.
Each class registers its associated model in the Django admin site and specifies the fields to be displayed,
forms to be used, and actions available for the model in the admin page.
"""

from neomodel import RelationshipTo, StringProperty, ArrayProperty
from matgraph.forms.formsMetadata import ResearcherAdminForm, InstitutionAdminForm
from matgraph.models.metadata import Researcher, Institution, Instrument
from matgraph.admins.adminBase import (NodeModelAdmin)
from django.contrib import admin as dj_admin


@dj_admin.register(Instrument)
class ResearcherAdmin(NodeModelAdmin):
    """
    ResearcherAdmin registers the Instrument model to the Django Admin page.

    list_display: A tuple of fields to be displayed in the admin list view.
    """
    class Meta:
        pass
    list_display = ("name", "uid")


@dj_admin.register(Researcher)
class ResearcherAdmin(NodeModelAdmin):
    """
    ResearcherAdmin registers the Researcher model to the Django Admin page.

    list_display: A tuple of fields to be displayed in the admin list view.
    form: The admin form associated with this model.
    """
    class Meta:
        pass
    list_display = ("name", "ORCID", "email", "uid")
    form = ResearcherAdminForm


@dj_admin.register(Institution)
class InstitutionAdmin(NodeModelAdmin):
    """
    InstitutionAdmin registers the Institution model to the Django Admin page.

    list_display: A tuple of fields to be displayed in the admin list view.
    form: The admin form associated with this model.
    search_fields: A tuple of fields that can be searched in the admin page.
    """
    class Meta:
        pass
    list_display = ("name", "ROI", "link", "uid")
    form  = InstitutionAdminForm
    search_fields = ('name',)
