from django.contrib import admin as dj_admin

from graphutils.admin import NodeModelAdmin
# from matgraph.forms.adminForms import ComponentAdminForm
from matgraph.models.properties import Property, Parameter


@dj_admin.register(Property)
class PropertyAdmin(NodeModelAdmin):
    list_display = ["uid"]

    def save(self, commit=True):
        instance = super().save(commit)
        instance.user_skill = True
        instance.save()

        return instance

    actions = ['delete_model']

@dj_admin.register(Parameter)
class ParameterAdmin(NodeModelAdmin):
    list_display = ["uid"]

    def save(self, commit=True):
        instance = super().save(commit)
        instance.user_skill = True
        instance.save()

        return instance

    actions = ['delete_model']

