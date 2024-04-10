from matgraph.views.baseViews import AutocompleteView
from matgraph.models.matter import Element, Material
from graphutils.forms import AutocompleteSingleChoiceField


class ElementAutocompleteView(AutocompleteView):
    model = Element
    autocomplete_url='element-autocomplete'

class MaterialInputAutocompleteView(AutocompleteView):
    model = Material
    autocomplete_url='material-input-autocomplete'

class MaterialChoiceField(AutocompleteSingleChoiceField):
    model = Material
    autocomplete_url = 'material-autocomplete'