"""
The graphutils library contains classes that are needed to extend the django functionality on neo4j.

graphutils helper classes:
 - LocalOrderingQueryBuilder
 - NeoPaginator

graphutils helper functions:
 - connect
 - connect_all
 - relation_to_internal_value
 - replace
 - validate_param
"""

from django.forms import ValidationError

from uuid import UUID

from neomodel import StringProperty
from neomodel.match import QueryBuilder
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse
from rest_framework.response import Response


# deletes existing connections
def connect_all(relationship, nodes):
    """
    Disconnects any existing relationships and then connects the given nodes.

    Args:
        relationship (Relationship): The relationship instance to operate on.
        nodes (iterable): An iterable of nodes to connect.
    """
    relationship.disconnect_all()
    for node in nodes:
        relationship.connect(node)

def connect(relationship, node):
    """
    Disconnects any existing relationships and then connects the given node.

    Args:
        relationship (Relationship): The relationship instance to operate on.
        node (Node): The node to connect.
    """
    relationship.disconnect_all()
    if node:
        relationship.connect(node)

def replace(relationship, node):
    try:
        old_node = relationship.single()
    except BaseException:
        old_node = None
    finally:
        if old_node:
            relationship.reconnect(old_node, node)
        else:
            relationship.connect(node)


def relation_to_internal_value(data, relation, model, add_attributes=[]):

    if relation not in data:
        return

    pk_attr = 'uid' if hasattr(model, 'uid') else 'code'
    is_single = not isinstance(data[relation], list)

    internal_values = []
    relation_data = data[relation] if not is_single else [data[relation]]

    if is_single and relation_data[0] is None:
        relation_data = []

    for item in relation_data:
        try:

            value = item[pk_attr]

            if isinstance(value, UUID):
                value = value.hex

            node = model.nodes.get(**{pk_attr: value})
            internal_values.append(node)

            for attr in add_attributes:
                if attr in item:
                    setattr(node, attr, item[attr])

        except model.DoesNotExist:
            raise ValidationError({relation: f'unknown {relation} for key "{value}"'})

    if is_single:
        data[relation] = internal_values[0] if len(internal_values) else None
    else:
        data[relation] = internal_values


def validate_param(request, param, type=str, list=False, required=True, default=None, uuidAsHexStr=False, **kwargs):

    if type == 'uuid':
        type = UUID

    if list:
        value = request.query_params.getlist(param, [])
    else:
        value = request.query_params.get(param, None)

    if not value:
        if default is not None:
            return default
        elif required:
            raise ValidationError(f'missing required parameter: {param}')
        elif not list:
            return None

    try:
        if list:
            value = [type(elm) for elm in value]
        else:
            value = type(value)
    except ValueError:
        raise ValidationError(f'invalid value: {param}')

    if type == UUID and uuidAsHexStr:
        if list:
            value = [v.hex for v in value]
        else:
            value = value.hex

    if type in (int, float):
        if min := kwargs.pop('min', None):
            if value < min:
                raise ValidationError(f'invalid value: {param}')
        if max := kwargs.pop('max', None):
            if value > max:
                raise ValidationError(f'invalid value: {param}')

    return value


class NeoPaginator:

    def __init__(self, request, max_limit=20, default_limit=20):
        self.start = validate_param(request, 'start', type=int, default=0, min=0, required=False)
        self.limit = validate_param(request, 'limit', type=int, default=default_limit, max=max_limit, min=1, required=False)
        self.request = request

    def build_query_fragment(self):
        return f' SKIP {self.start} LIMIT {self.limit}'

    def build_query(self, query):
        return f'{query} {self.build_query_fragment()}'

    def build_next_url(self):

        url = reverse(self.request.resolver_match.view_name, request=self.request)

        params = self.request.query_params.copy()
        params['start'] = self.start + self.limit
        params['limit'] = self.limit

        return f'{url}?{params.urlencode()}'

    def build_response(self, data, **kwargs):
        return Response({
            'results': data,
            'next': None if not len(data) else self.build_next_url()
        }, **kwargs)

class LocaleOrderingQueryBuilder(QueryBuilder):

    def build_order_by(self, ident, source):

        # cypher uses reversed ordering
        source._order_by.reverse()

        if '?' in source._order_by:
            super().build_order_by(ident, source)
        else:
            self._ast['order_by'] = []
            for p in source._order_by:
                field = p.split(' ')[0]
                if isinstance(getattr(source.model, field), StringProperty):
                    self._ast['order_by'].append(f'apoc.text.clean({ident}.{field}) {p.replace(field,"")}')
                else:
                    self._ast['order_by'].append(f'{ident}.{p}')

