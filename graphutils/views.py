"""
The graphutils library contains classes that are needed to extend the django functionality on neo4j.

graphutils views classes:
 - AutocompleteView
"""

from dal import autocomplete


class AutocompleteView(autocomplete.Select2QuerySetView):

    model = None

    label_property = 'label'
    value_property = 'uid'

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return self.model.nodes.none()
        return self.model.nodes.filter(**{self.label_property+'__icontains': self.q})

    def get_result_value(self, result):
        return str(getattr(result, self.value_property))

    def get_result_label(self, result):
        return str(getattr(result, self.label_property))
