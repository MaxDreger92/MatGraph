"""
The graphutils library contains classes that are needed to extend the django functionality on neo4j.

graphutils form classes:
 - AutocompleteSingleChoiceField
 - ChoiceWidgetBase
 - NeoModelForm
 - RelationChoiceFieldBase
 - RelationMultipleChoiceField
 - RelationMultipleChoiceWidget
 - RelationSingleChoiceField
 - RelationSingleChoiceWidget
"""

from dal import autocomplete
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms import Select
from django import forms
from neomodel import db, RelationshipManager


class DateInput(forms.DateInput):
    input_type = 'date'

class ChoiceWidgetBase:

    def __init__(self, *args, **kwargs):
        self.primary_key = kwargs.pop('primary_key', 'uid')
        self.node_label = kwargs.pop('node_label')
        self.label_field = kwargs.pop('label_field')
        super().__init__(*args, **kwargs)
        self.cached_choices = None

    @property
    def choices(self):
        if not self.cached_choices:
            self.cached_choices, meta = db.cypher_query(
                f'''
                    MATCH (n:{self.node_label})
                    RETURN n.{self.primary_key}, n.{self.label_field}
                    ORDER BY toLower(n.{self.label_field})
                '''
            )
        return self.cached_choices

    @choices.setter
    def choices(self, value):
        pass


class RelationMultipleChoiceWidget(ChoiceWidgetBase, FilteredSelectMultiple):
    pass


class RelationSingleChoiceWidget(ChoiceWidgetBase, Select):

    def __init__(self, *args, **kwargs):
        self.include_none_option = kwargs.pop('include_none_option', True)
        super().__init__(*args, **kwargs)

    @property
    def choices(self):
        if self.include_none_option:
            return [(None, '---')]+super().choices
        else:
            return super().choices

    @choices.setter
    def choices(self, value):
        pass


class RelationChoiceFieldBase:

    def __init__(self, widget, primary_key='uid', **kwargs):
        super().__init__(
            **kwargs
        )

        # it's important to set the widget after calling super().__init__
        # otherwise django tries to fetch choices before the db connection initializes
        self.widget = widget
        self.primary_key = primary_key

    # disable validation for now, as it's only relevant for internal backend
    # TODO: implement :)
    def validate(self, values):
        return

    # not the cleanest way to handle relation saving
    # done here, because primary_key is already known
    def save(self, relation_name, instance, data):
        rel = getattr(instance, relation_name)
        node_class = rel.definition['node_class']

        if isinstance(data, list):
            rel.disconnect_all()
            for value in data:
                if value:
                    rel.connect(
                        node_class.nodes.get(**{self.primary_key: value})
                    )
        elif data:

            # to avoid cardinality issues (One)
            try:
                old_node = rel.single()
            except BaseException:
                old_node = None
            finally:
                if old_node:
                    rel.reconnect(
                        old_node,
                        node_class.nodes.get(**{self.primary_key: data})
                    )
                else:
                    rel.connect(
                        node_class.nodes.get(**{self.primary_key: data})
                    )


class RelationMultipleChoiceField(RelationChoiceFieldBase, forms.MultipleChoiceField):

    def __init__(self, node_label, name_plural, primary_key='uid', label_field='name', **kwargs):
        super().__init__(
            widget=RelationMultipleChoiceWidget(name_plural, False, node_label=node_label, primary_key=primary_key, label_field=label_field),
            primary_key=primary_key,
            **kwargs
        )


class RelationSingleChoiceField(RelationChoiceFieldBase, forms.ChoiceField):

    def __init__(self, node_label, primary_key='uid', label_field='label', include_none_option=True, **kwargs):
        super().__init__(
            widget=RelationSingleChoiceWidget(node_label=node_label, primary_key=primary_key, label_field=label_field, include_none_option=include_none_option),
            primary_key=primary_key,
            **kwargs
        )



class NeoModelForm(forms.ModelForm):

    labels = {}

    def __init__(self, *args, **kwargs):

        if instance := kwargs.get('instance', None):

            kwargs['initial'] = {}

            for name, field in self.declared_fields.items():
                if isinstance(field, RelationMultipleChoiceField):
                    kwargs['initial'][name] = [
                        getattr(rel, field.primary_key)
                        for rel in getattr(instance, name).all()
                    ]
                elif isinstance(field, RelationSingleChoiceField):
                    try:
                        rel = getattr(instance, name).single()
                        kwargs['initial'][name] = getattr(rel, field.primary_key) if rel else None
                    except:
                        kwargs['initial'][name] = None

        super().__init__(*args, **kwargs)

        for field, label in self.labels.items():
            if field in self.fields:
                self.fields[field].label = label

    def save(self, commit=True):
        instance = super().save(commit)

        with db.transaction:
            instance.save()

            # save relations
            for changed in self.changed_data:
                if hasattr(instance, changed):
                    if isinstance(getattr(instance, changed), RelationshipManager):
                        self.fields[changed].save(changed, instance, self.cleaned_data[changed])

        return instance


class AutocompleteSingleChoiceField(RelationSingleChoiceField):

    label_property = 'label'
    model = None
    autocomplete_url = None

    def __init__(self, **kwargs):
        super().__init__(self.model, **kwargs)
        self.widget = autocomplete.Select2(url=self.autocomplete_url, attrs={'style': 'width: 270px;'})

    def prepare_value(self, value):

        # make sure selected value is in choices to have it displayed right away
        if value and len(value):
            self.widget.choices = [
                (value, getattr(self.model.nodes.get(uid=value), self.label_property))
            ]

        return value
