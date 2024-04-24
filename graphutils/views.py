"""
The graphutils library contains classes that are needed to extend the django functionality on neo4j.

graphutils views classes:
 - AutocompleteView
"""

from dal import autocomplete
from django_neomodel import NeoNodeSet
from neomodel.match import QueryBuilder, NodeSet


class FixedQueryBuilder(QueryBuilder):

    # neomodel's querybuilder crashes on count if skip/limit are used (eg. pagination)
    def _count(self):

        # ignore skip/limit to avoid unexpected results
        skip = self._ast.skip
        limit = self._ast.limit
        self._ast.skip = None
        self._ast.limit = None

        result = super()._count()

        self._ast.skip = skip
        self._ast.limit = limit

        return result

    # enable neo4j's parallel runtime to accelerate queries
    def build_query(self):

        if hasattr(db, '_session'):
            if hasattr(db._session, "_connection_access_mode"):
                if db._session._connection_access_mode != "WRITE":
                    return "CYPHER runtime = parallel " + super().build_query()

        return super().build_query()



# make sure FixedQueryBuilder is used by default
NodeSet.query_cls = FixedQueryBuilder
NeoNodeSet.query_cls = FixedQueryBuilder

# only supports ordering by a single property for now
class DistanceOrderingQueryBuilder(FixedQueryBuilder):

    def build_single_order_by(self, ident, source, property_name):

        tokens = source.split()
        source = tokens.pop(0)
        order = ' '.join(tokens)

        if source == property_name:
            return f'apoc.text.distance({ident}.{source}, $distance_ordering_query) {order}'
        else:
            return '{0}.{1}'.format(ident, source)

    def build_order_by(self, ident, source):
        self._query_params['distance_ordering_query'] = source.distance_ordering_query
        self._ast.order_by = [
            self.build_single_order_by(ident, p, source.distance_ordering_field)
            for p in source.order_by_elements
        ]


class AutocompleteView(autocomplete.Select2QuerySetView):

    model = None

    label_property = 'label'
    value_property = 'uid'

    distance_ordering = True

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return self.model.nodes.none()
        qs = self.model.nodes.filter(**{self.label_property+'__icontains': self.q}).order_by(self.label_property)

        qs.distance_ordering_field = self.label_property
        qs.distance_ordering_query = self.q
        qs.query_cls = DistanceOrderingQueryBuilder

        return qs

    def get_result_value(self, result):
        return str(getattr(result, self.value_property))

    def get_result_label(self, result):
        return str(getattr(result, self.label_property))