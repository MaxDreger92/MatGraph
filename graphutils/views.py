"""
The graphutils library contains classes that are needed to extend the django functionality on neo4j.

graphutils views classes:
 - AutocompleteView
"""

from dal import autocomplete

from graphutils.helpers import DistanceOrderingQueryBuilder


class AutocompleteView(autocomplete.Select2QuerySetView):
    model = None

    label_property = 'label'
    value_property = 'uid'

    distance_ordering = True

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return self.model.nodes.none()
        qs = self.model.nodes.filter(**{self.label_property + '__icontains': self.q}).order_by(self.label_property)

        qs.distance_ordering_field = self.label_property
        qs.distance_ordering_query = self.q
        qs.query_cls = DistanceOrderingQueryBuilder

        return qs

    def get_result_value(self, result):
        return str(getattr(result, self.value_property))

    def get_result_label(self, result):
        return str(getattr(result, self.label_property))
