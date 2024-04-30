from django.forms import ValidationError

from uuid import UUID

from django_neomodel import NeoNodeSet
from neomodel import StringProperty, db, NodeSet
from neomodel.match import QueryBuilder
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse
from rest_framework.response import Response



# deletes existing connections
def connect_all(relationship, nodes):
    relationship.disconnect_all()
    for node in nodes:
        relationship.connect(node)

def connect(relationship, node):
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

    relation_data = data[relation] if not is_single else [data[relation]]

    if is_single and relation_data[0] is None:
        relation_data = []

    # collect pks
    pks = [
        item[pk_attr].hex if isinstance(item[pk_attr], UUID) else item[pk_attr]
        for item in relation_data
    ]

    # fetch in single query
    result, meta = db.cypher_query(
        f'UNWIND $pks as pk MATCH (n:{model.__label__}) WHERE n.{pk_attr}=pk RETURN n',
        {'pks': pks}
    )

    if len(result) != len(relation_data):
        raise ValidationError({relation: f'missing node'})

    internal_values = [model.inflate(row[0]) for row in result]

    # add extra attributes
    for i in range(0, len(relation_data)):
        for attr in add_attributes:
            if attr in relation_data[i]:
                setattr(internal_values[i], attr, relation_data[i][attr])

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

class DummyPaginator:

    def __init__(self, limit=20, skip=0):
        self.skip = skip
        self.limit = limit

    def build_query_fragment(self):
        return f' SKIP {self.skip} LIMIT {self.limit}'

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

    def apply(self, node_set):
        setattr(node_set, 'limit', self.limit)
        setattr(node_set, 'skip', self.start)


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

class LocaleOrderingQueryBuilder(FixedQueryBuilder):

    def build_order_by(self, ident, source):

        # cypher uses reversed ordering
        source.order_by_elements.reverse()

        if '?' in source.order_by_elements:
            super().build_order_by(ident, source)
        else:
            self._ast.order_by = []
            for p in source.order_by_elements:
                field = p.split(' ')[0]
                if isinstance(getattr(source.model, field), StringProperty):
                    self._ast.order_by.append(f'apoc.text.clean({ident}.{field}) {p.replace(field,"")}')
                else:
                    self._ast.order_by.append(f'{ident}.{p}')


class RelationFilterQueryBuilder(FixedQueryBuilder):

    def _build_relation_filters(self, filters):

        indent = self.node_set.source.__name__.lower()

        for f in filters:

            direction = f[4] if len(f) > 4 else 'outbound'
            direction = direction == 'outbound'

            if direction:
                self._ast.where.append(
                    f'EXISTS(({indent})-[:{f[0]}]->(:{f[1]} {{{f[2]}: "{f[3]}"}}))'
                )
            else:
                self._ast.where.append(
                    f'EXISTS(({indent})<-[:{f[0]}]-(:{f[1]} {{{f[2]}: "{f[3]}"}}))'
                )


    def build_query(self):

        if hasattr(self.node_set, 'relation_filters'):
            self._build_relation_filters(getattr(self.node_set, 'relation_filters'))

        return super().build_query()