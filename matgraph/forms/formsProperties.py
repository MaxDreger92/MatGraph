import django as django
from django.forms import FloatField, BaseForm, HiddenInput, BaseFormSet, CharField, IntegerField
from django import db
from neomodel import db

from matgraph.models.properties import Property
from graphutils.forms import RelationSingleChoiceField


class BasePropertyForm(BaseForm):
    base_fields = {
        'id': IntegerField(widget=HiddenInput, required=False),
        'measurement_label': CharField(required=False, label="Measurement"),
        'property_label': CharField(required=False, label="Property"),
        # 'unit': FloatField(include_none_option=False, label="Unit"),
        'value': FloatField(required =False, label="Value"),
        'accuracy': FloatField(required =False, label="Accuracy")
    }

    class Meta:
        fields = []

    class _meta:
        labels = None
        exclude = []
        fields = []
        help_texts = []
        model = Property
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)

class BasePropertyFormset(BaseFormSet):

    _pk_field = django.db.models.CharField(name="id")

    def __init__(self, *args, **kwargs):

        kwargs.pop('queryset')
        kwargs.pop('save_as_new', None)

        self.instance = kwargs.pop('instance')
        self.initial = self.get_initial()
        kwargs['initial'] = self.initial

        super().__init__(*args, **kwargs)

    def get_queryset(self):
        return self.initial

    @db.read_transaction
    def get_initial(self):
        if not hasattr(self.instance, "id"):
            return {}
        return self.load(self.instance)

    def load(self, instance):
        raise NotImplementedError()

    def save(self, *args, **kwargs):

        rel = getattr(self.instance, self.attribute_name)

        # TODO: consolidate into single query for performance
        with db.write_transaction:
            rel.disconnect_all()
            for item in self.cleaned_data:
                if not item.pop('DELETE', False):
                    item.pop('id')

                    node = self.target_class.nodes.get(uid=item.pop(self.target_field))

                    # make sure empty values are not saved as empty strings
                    for key, value in item.items():
                        if value == '':
                            item[key] = None

                    if not item['title']:
                        item['title'] = node.label

                    rel.connect(node, item)

        # only used for change messages and therefore not important
        self.new_objects = []
        self.changed_objects = []
        self.deleted_objects = []

class PropertyFormsetCls(BasePropertyFormset):

    attribute_name = 'properties'
    target_field = 'property'
    target_class = Property

    def load(self, instance):

        result, meta = instance.cypher('''
            MATCH (material)-[rel:HAS_PROPERTY]->(property:Property)<-[:HAS_MEASUREMENT_OUTPUT]-(measurement:Measurement)
            WHERE ID(material)=$self
            WITH material, measurement, property, rel
            MATCH(measurement)-[:IS_A]->(measurement_label:EMMOProcess) 
            MATCH(property)-[:IS_A]->(property_label:EMMOQuantity) 

            
            RETURN
                ID(rel) as rel,
                measurement.uid as measurement,
                rel.float_value as value, rel.float_accuracy as accuracy,
                measurement_label.name as label, rel.unit as unit, property.uid as property, property_label.name as property_label
        ''')

        return [
            {
                'id': sub[0], 'measurement': sub[1], 'value': sub[2], 'accuracy': sub[3],
                'measurement_label': sub[4], 'unit': sub[5], 'property': sub[6], 'property_label': sub [7]
            }
            for sub in result
        ]
class PropertyForm(BasePropertyForm):

    base_fields = {
        **BasePropertyForm.base_fields
    }