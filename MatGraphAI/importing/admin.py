from django.utils.safestring import mark_safe
from neomodel import Q

from graphutils.admin import NodeModelAdmin
from importing.forms import NodeLabelClassifierAdminForm, NodeAttributeClassifierAdminForm, \
    MatterAttributeClassifierAdminForm, MetadataAttributeClassifierAdminForm, ManufacturingAttributeClassifierAdminForm, \
    MeasurementAttributeClassifierAdminForm, ParameterAttributeClassifierAdminForm, PropertyAttributeClassifierAdminForm
from importing.models import ImportingReport, NodeLabelEmbedding, NodeAttributeEmbedding, LabelClassificationReport, \
    MatterAttributeEmbedding, ManufacturingAttributeEmbedding, MeasurementAttributeEmbedding, \
    ParameterAttributeEmbedding, PropertyAttributeEmbedding, MetadataAttributeEmbedding, ImporterCache, \
    AttributeClassificationReport
from django.contrib import admin

from matgraph.models.metadata import File


# @admin.register(ImportingReport)
# class ImportingReportAdmin(admin.ModelAdmin):
#
#     list_display = ['date', 'type']
#     list_filter = ('type', 'date')
#     fields = (('type','date'), 'get_report')
#     readonly_fields = ('date', 'type', 'get_report')
#
#     def get_report(self, obj):
#         return mark_safe(obj.report)
#     get_report.short_description = 'Report'
#
#     class Media:
#         css = {
#             'all': ('matching/css/admin_overrides.css',)
#         }



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

# @admin.register(NodeAttributeEmbedding)
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

@admin.register(MatterAttributeEmbedding)
class MatterAttributeEmbeddingAdmin(NodeAttributeEmbeddingAdmin):
    form = MatterAttributeClassifierAdminForm
    pass

@admin.register(PropertyAttributeEmbedding)
class PropertyAttributeEmbeddingAdmin(NodeAttributeEmbeddingAdmin):
    form = PropertyAttributeClassifierAdminForm
    pass

@admin.register(ParameterAttributeEmbedding)
class ParameterAttributeEmbeddingAdmin(NodeAttributeEmbeddingAdmin):
    form = ParameterAttributeClassifierAdminForm
    pass

@admin.register(MeasurementAttributeEmbedding)
class MeasurementAttributeEmbeddingAdmin(NodeAttributeEmbeddingAdmin):
    form = MeasurementAttributeClassifierAdminForm
    pass


@admin.register(ManufacturingAttributeEmbedding)
class ManufacturingAttributeEmbeddingAdmin(NodeAttributeEmbeddingAdmin):
    form = ManufacturingAttributeClassifierAdminForm
    pass

@admin.register(MetadataAttributeEmbedding)
class ManufacturingAttributeEmbeddingAdmin(NodeAttributeEmbeddingAdmin):
    form = MetadataAttributeClassifierAdminForm
    pass

@admin.register(File)
class FileAdmin(NodeModelAdmin):



    form = NodeAttributeClassifierAdminForm
    # form is necessary to create relations
    list_display = ("name", "context", 'link', 'uid')
    pass

    # Allows hacked inlines
    def check(self, **kwargs):
        return []


@admin.register(LabelClassificationReport)
class LabelClassifictionReportAdmin(admin.ModelAdmin):

    list_display = ['date', 'file_link']
    list_filter = ('date','file_link', 'context',)
    fields = (('file_link', 'context', 'date', 'report_file_link'), 'get_report')
    readonly_fields = ('date', 'get_report')

    def get_report(self, obj):
        return mark_safe(obj.html_report)
    get_report.short_description = 'Report'


    # needs to be introduced to enable search, actual search is done by get_search_results
    search_fields = ('name', 'context')

    # Actual search
    def get_search_results(self, request, queryset, search_term):
        if search_term:
            queryset = queryset.filter(
                Q(name__icontains=search_term) |
                Q(context__icontains=search_term) |
                Q(uid=search_term)
            )
        may_have_duplicates = False

        return queryset, may_have_duplicates

@admin.register(AttributeClassificationReport)
class AttributeClassifictionReportAdmin(admin.ModelAdmin):

    list_display = ['date', 'file_link']
    list_filter = ('date','file_link', 'context',)
    fields = (('file_link', 'context', 'date', 'report_file_link'), 'get_report')
    readonly_fields = ('date', 'get_report')

    def get_report(self, obj):
        return mark_safe(obj.html_report)
    get_report.short_description = 'Report'


    # needs to be introduced to enable search, actual search is done by get_search_results
    search_fields = ('name', 'context')

    # Actual search
    def get_search_results(self, request, queryset, search_term):
        if search_term:
            queryset = queryset.filter(
                Q(name__icontains=search_term) |
                Q(context__icontains=search_term) |
                Q(uid=search_term)
            )
        may_have_duplicates = False

        return queryset, may_have_duplicates

@admin.register(ImporterCache)
class ImporterCacheAdmin(admin.ModelAdmin):
    field = (('header', 'label', 'header_attribute', 'column_attribute', 'sample_column', 'validated',))
    list_display = ('header', 'sample_column', 'label', 'header_attribute', 'column_attribute', 'validated',)
    list_editable = ('label', 'header_attribute', 'column_attribute', 'validated',)  # Make 'validated' field editable in list view
    pass
