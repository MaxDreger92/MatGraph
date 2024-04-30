"""
All admin classes that are required for Matter models. Contains Typefilters, to allow filtering of Matter
classes by certain properties and the model admins. AdminClasses register the models on the admin site and allow
reading writing and deleting of their instances via the admin interface.
Contains the classes
    ElementAdmin
    MoleculeAdmin
    ManufacturedAdmin
    ComponentAdmin
    DeviceAdmin
"""
from django.contrib import admin as dj_admin
from neomodel import Q

from graphutils.admin import NodeModelAdmin
from matgraph.forms.formsMatter import MoleculeAdminForm, MaterialAdminForm, DeviceAdminForm, ComponentAdminForm
from matgraph.inlines.inlinesProperties import TabularPropertyInline
from matgraph.models.matter import (Molecule,
                                    Component,
                                    Device, Material, Element)


@dj_admin.register(Element)
class ElementAdmin(NodeModelAdmin):
    """
    ElementAdmin represents the element class in the admin site.

    list_display: A tuple of fields to be displayed in the admin list view.
    """
    list_display = ("name",
                    "symbol")


@dj_admin.register(Molecule)
class MoleculeAdmin(NodeModelAdmin):
    """
    Admin class of the Molecule model, to register Molecule at the admin page.

    list_display: A tuple of fields to be displayed in the admin list view.
    form: The admin form associated with this model.
    actions: A list of actions available for this model in the admin page.
    """

    list_display = ("uid",
                    "SMILES",
                    "InChI_key",
                    "CAS",
                    "InChI",
                    "compound_cid",
                    "IUPAC_name",
                    "chemical_formula",
                    )
    form = MoleculeAdminForm

    def response_add(self, request, obj, post_url_continue=None):
        """

        :param request:
        :param obj:
        :param post_url_continue:
        :return:
        """
        obj.pk = obj.uid  # make sure redirect after add works
        return super().response_add(request, obj, post_url_continue)

    # Allows hacked inlines
    def check(self, **kwargs):
        return []

    actions = ['delete_model']


@dj_admin.register(Material)
class MaterialAdmin(NodeModelAdmin):
    """
    MaterialAdmin registers the Material model to the Django Admin page.

    form: The admin form associated with this model.
    list_display: A tuple of fields to be displayed in the admin list view.
    inlines: A list of inline model classes associated with this model.
    search_fields: A tuple of fields that can be searched in the admin page.
    """

    # form is necessary to create relations
    form = MaterialAdminForm
    list_display = ("name", "uid")
    pass

    # Allows hacked inlines
    def check(self, **kwargs):
        return []

    inlines = [TabularPropertyInline]

    # needs to be introduced to enable search, actual search is done by get_search_results
    search_fields = ('name',)

    # Actual search
    def get_search_results(self, request, queryset, search_term):
        if search_term:
            queryset = queryset.filter(
                Q(name__icontains=search_term) |
                Q(uid=search_term)
            )
        may_have_duplicates = False

        return queryset, may_have_duplicates


@dj_admin.register(Component)
class ComponentAdmin(NodeModelAdmin):
    """
    ComponentAdmin registers the Component model to the Django Admin page.

    form: The admin form associated with this model.
    list_display: A tuple of fields to be displayed in the admin list view.
    """
    # form is necessary for the creation of relations
    form = ComponentAdminForm
    # list_display determines which properties are displayed
    list_display = ["uid"]

    # save function, necessary to save instances
    def save(self, commit=True):
        instance = super().save(commit)
        instance.save()

        return instance


@dj_admin.register(Device)
class DeviceAdmin(NodeModelAdmin):
    """
    DeviceAdmin registers the Device model to the Django Admin page.

    form: The admin form associated with this model.
    list_display: A tuple of fields to be displayed in the admin list view.
    """

    # form is necessary for the creation of relations
    form = DeviceAdminForm

    # Displayed attributes in item list of the admin page
    list_display = ("uid",
                    "name")
