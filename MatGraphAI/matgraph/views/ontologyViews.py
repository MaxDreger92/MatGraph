from matgraph.models.ontology import EMMOMatter
from graphutils.forms import AutocompleteSingleChoiceField


class OntologyChoiceField(AutocompleteSingleChoiceField):
    model = EMMOMatter
    autocomplete_url = 'emmomatter-autocomplete'