from dal import autocomplete
from django import forms
from neomodel import db

from matgraph.choices.ChoiceFields import COMPONENT_TYPE_CHOICES
from matgraph.fields.baseFields import RelationMultipleChoiceField


class ComponentTypeChoiceField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = COMPONENT_TYPE_CHOICES.items()
        super().__init__(*args, **kwargs)

class RegularTypeChoiceField(forms.ChoiceField):
    def __init__(self, CHOICE_DICT, *args, **kwargs):
        kwargs['choices'] = CHOICE_DICT.items()
        super().__init__(*args, **kwargs)
class ElementsMultipleChoiceField(RelationMultipleChoiceField):

    def __init__(self, autocomplete_url='element-autocomplete', **kwargs):
        super().__init__('Element', 'Elements', primary_key='uid', label_field='name', **kwargs)
        self.widget = autocomplete.Select2Multiple(url=autocomplete_url, attrs={'style': 'width: 100%;'})

    def prepare_value(self, value):
        # make sure selected value is in choices to have it displayed right away
        if value and len(value):
            self.widget.choices, meta = db.cypher_query(
                'MATCH (element:Element) WHERE element.uid IN $uids RETURN element.uid, element.name',
                {'uids': value}
            )

        return value

# class MaterialMultipleChoiceField(RelationMultipleChoiceField):
#
#     def __init__(self, autocomplete_url='material-input-autocomplete', **kwargs):
#         super().__init__('Material', 'Materials', primary_key='uid', label_field='name', **kwargs)
#         self.widget = autocomplete.Select2Multiple(url=autocomplete_url, attrs={'style': 'width: 100%;'})
#
#     def prepare_value(self, value):
#         # make sure selected value is in choices to have it displayed right away
#         if value and len(value):
#             self.widget.choices, meta = db.cypher_query(
#                 'MATCH (material:Material) WHERE material.uid IN $uids RETURN material.uid, material.name',
#                 {'uids': value}
#             )
#         return value

# class EMMOMatterMultipleChoiceField(RelationMultipleChoiceField):
#
#     def __init__(self, autocomplete_url='material-input-autocomplete', **kwargs):
#         super().__init__('EMMOMatter', 'EMMOMatters', primary_key='uri', label_field='name', **kwargs)
#         self.widget = autocomplete.Select2Multiple(url=autocomplete_url, attrs={'style': 'width: 100%;'})
#
#     def prepare_value(self, value):
#         # make sure selected value is in choices to have it displayed right away
#         if value and len(value):
#             self.widget.choices, meta = db.cypher_query(
#                 'MATCH (material:EMMO_Material) WHERE material.uri IN $uids RETURN material.uri, material.name',
#                 {'uris': value}
#             )
#         return value
#
# class EMMOProcessMultipleChoiceField(RelationMultipleChoiceField):
#
#     def __init__(self, autocomplete_url='emmo-process-autocomplete', **kwargs):
#         super().__init__('EMMOProcess', 'EMMOProcesses', primary_key='uri', label_field='name', **kwargs)
#         self.widget = autocomplete.Select2Multiple(url=autocomplete_url, attrs={'style': 'width: 100%;'})
#
#     def prepare_value(self, value):
#         # make sure selected value is in choices to have it displayed right away
#         if value and len(value):
#             self.widget.choices, meta = db.cypher_query(
#                 'MATCH (material:EMMO_Material) WHERE material.uri IN $uids RETURN material.uri, material.name',
#                 {'uris': value}
#             )
#         return value




