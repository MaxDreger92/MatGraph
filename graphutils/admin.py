from django.contrib.admin import ModelAdmin, SimpleListFilter
from django.contrib.admin.views.main import ChangeList
from django.forms import formset_factory, BaseFormSet
from neomodel import db

from graphutils.helpers import LocaleOrderingQueryBuilder, RelationFilterQueryBuilder


class NeoAdminChangelist(ChangeList):

    # only support ordering by one column to keep things simple by now
    def get_ordering(self, request, queryset):
        return super().get_ordering(request, queryset)[0:1]


class NodeModelAdmin(ModelAdmin):

    node_primary_key = 'uid'
    node_changelist_formset = None
    node_changelist_form = None

    # very important, unordered datasets save data in random places...
    ordering = ('uid', )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs.query_cls = LocaleOrderingQueryBuilder
        return qs

    def get_changelist(self, request, **kwargs):
        return NeoAdminChangelist

    def _get_list_editable_queryset(self, request, prefix):
        object_pks = self._get_edited_object_pks(request, prefix)
        return [self.model.nodes.get(uid=uid) for uid in object_pks]

    def get_changelist_formset(self, request, **kwargs):
        if self.node_changelist_form and self.node_changelist_formset:
            return formset_factory(self.node_changelist_form, formset=self.node_changelist_formset)
        return super().get_changelist_formset(request, **kwargs)


class ChangelistNodeFormset(BaseFormSet):

    def __init__(self, *args, **kwargs):
        self.nodes = list(kwargs.pop('queryset'))
        super().__init__(*args, **kwargs)

    def initial_form_count(self):
        return len(self.nodes)

    def total_form_count(self):
        return self.initial_form_count()

    def _construct_form(self, i, **kwargs):
        kwargs['instance'] = self.nodes[i]
        return super()._construct_form(i, **kwargs)

class RelationFilter(SimpleListFilter):

    query = None
    relation = None
    node_label = None
    property = 'uid'

    def lookups(self, request, model_admin):
        return db.cypher_query(self.query)[0]

    def queryset(self, request, queryset):
        if self.value():
            queryset.query_cls = RelationFilterQueryBuilder

            if not hasattr(queryset, 'relation_filters'):
                queryset.relation_filters = []

            queryset.relation_filters.append(
                (self.relation, self.node_label, self.property, self.value())
            )

        return queryset


class RelationInputFilter(RelationFilter):
    template = 'admin/input_filter.html'

    def lookups(self, request, model_admin):
        return [(None,None)] # dummy

