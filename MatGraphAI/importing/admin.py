from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from neomodel import Q

from graphutils.admin import NodeModelAdmin
from importing.forms import NodeLabelClassifierAdminForm, NodeAttributeClassifierAdminForm, \
    MatterAttributeClassifierAdminForm, MetadataAttributeClassifierAdminForm, ManufacturingAttributeClassifierAdminForm, \
    MeasurementAttributeClassifierAdminForm, ParameterAttributeClassifierAdminForm, PropertyAttributeClassifierAdminForm
from importing.models import NodeLabelEmbedding, LabelClassificationReport, \
    MatterAttributeEmbedding, ManufacturingAttributeEmbedding, MeasurementAttributeEmbedding, \
    ParameterAttributeEmbedding, PropertyAttributeEmbedding, MetadataAttributeEmbedding, ImporterCache, \
    AttributeClassificationReport, FullTableCache
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

class ReportAdmin(admin.ModelAdmin):

    fields = [('context', 'date', 'report_file_link'), ('show_file_link_url', 'show_report_link_url'), 'get_report']

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()


    list_display = ['date', 'show_file_link_url',  'show_report_link_url']
    list_filter = ('date', 'file_link', 'context',)
    readonly_fields = ('date', 'get_report', 'show_file_link_url', 'show_report_link_url')

    def show_file_link_url(self, obj):
        return format_html("<a href='{url}'>{url}</a>", url=obj.file_link)
    show_file_link_url.short_description = 'File Link'
    show_file_link_url.allow_tags = True
    def show_report_link_url(self, obj):
        return format_html("<a href='{url}'>{url}</a>", url=obj.report_file_link)
    show_report_link_url.short_description = 'Report Link'
    show_report_link_url.allow_tags = True
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

@admin.display(description="FileLink")
@admin.register(LabelClassificationReport)
class LabelClassifictionReportAdmin(ReportAdmin):
    pass


@admin.register(AttributeClassificationReport)
class AttributeClassifictionReportAdmin(admin.ModelAdmin):
    pass

@admin.register(ImporterCache)
class ImporterCacheAdmin(admin.ModelAdmin):
    field = (('header', 'sample_column', 'column_label', 'validated_column_label', 'header_attribute', 'column_attribute', 'validated_column_attribute',))
    list_display = ('header', 'sample_column', 'column_label', 'validated_column_label', 'header_attribute', 'column_attribute', 'validated_column_attribute',)
    list_editable = ('column_label', 'header_attribute', 'validated_column_label', 'column_attribute', 'validated_column_attribute',)  # Make 'validated' field editable in list view
    pass

@admin.register(FullTableCache)
class FullTableCacheAdmin(admin.ModelAdmin):
    field =(('header', 'graph',))
    list_display = ('header', 'graph',)
    list_editable = ('graph',)



