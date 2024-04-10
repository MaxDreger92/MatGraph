from neomodel import db
from django.contrib.admin.widgets import FilteredSelectMultiple
from django import forms


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


class RelationMultipleChoiceField(RelationChoiceFieldBase, forms.MultipleChoiceField):
    def __init__(self, node_label, name_plural, primary_key='uid', label_field='label', **kwargs):
        super().__init__(
            widget=RelationMultipleChoiceWidget(name_plural, False, node_label=node_label, primary_key=primary_key,
                                                label_field=label_field),
            primary_key=primary_key,
            **kwargs
        )
