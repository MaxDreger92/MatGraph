from django.utils.safestring import mark_safe
from neomodel import Q

from graphutils.admin import NodeModelAdmin
from importing.forms import NodeLabelClassifierAdminForm, NodeAttributeClassifierAdminForm
from importing.models import ImportingReport, NodeLabelEmbedding, NodeAttributeEmbedding
from django.contrib import admin


@admin.register(ImportingReport)
class ImportingReportAdmin(admin.ModelAdmin):

    list_display = ['date', 'type']
    list_filter = ('type', 'date')
    fields = (('type','date'), 'get_report')
    readonly_fields = ('date', 'type', 'get_report')

    def get_report(self, obj):
        return mark_safe(obj.report)
    get_report.short_description = 'Report'

    class Media:
        css = {
            'all': ('matching/css/admin_overrides.css',)
        }



@admin.register(NodeLabelEmbedding)
class NodeLabelEmbeddingAdmin(NodeModelAdmin):
    def get_label(self, obj):
        return obj.label.single().name


    get_label.short_description = "Label"

    form = NodeLabelClassifierAdminForm
    # form is necessary to create relations
    list_display = ("input", "uid", 'get_label')
    pass

    # Allows hacked inlines
    def check(self, **kwargs):
        return []


    # needs to be introduced to enable search, actual search is done by get_search_results
    search_fields = ('get_label')

    # Actual search
    def get_search_results(self, request, queryset, search_term):
        if search_term:
            queryset = queryset.filter(
                Q(label__icontains=search_term) |
                Q(uid=search_term)
            )
        may_have_duplicates = False

        return queryset, may_have_duplicates

@admin.register(NodeAttributeEmbedding)
class NodeAttributeEmbeddingAdmin(NodeModelAdmin):
    def get_label(self, obj):
        return obj.label.single().name


    get_label.short_description = "Label"

    form = NodeAttributeClassifierAdminForm
    # form is necessary to create relations
    list_display = ("input", "uid", 'get_label')
    pass

    # Allows hacked inlines
    def check(self, **kwargs):
        return []


    # needs to be introduced to enable search, actual search is done by get_search_results
    search_fields = ('get_label')

    # Actual search
    def get_search_results(self, request, queryset, search_term):
        if search_term:
            queryset = queryset.filter(
                Q(label__icontains=search_term) |
                Q(uid=search_term)
            )
        may_have_duplicates = False

        return queryset, may_have_duplicates


