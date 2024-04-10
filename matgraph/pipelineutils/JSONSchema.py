import json, inspect
from neomodel.properties import Property as NeoProperty
from neomodel import (StringProperty, IntegerProperty, FloatProperty,
                      BooleanProperty, DateTimeProperty, DateProperty,
                      JSONProperty, ArrayProperty, UniqueIdProperty)
from neomodel import RelationshipTo, RelationshipFrom

from matgraph.models.matter import Material
import pprint
from neomodel import Relationship
FIELD_TYPE_MAPPING = {
    StringProperty: "string",
    IntegerProperty: "integer",
    FloatProperty: "number",
    BooleanProperty: "boolean",
    DateTimeProperty: "string",  # You can use a "format": "date-time" in the schema for validation
    DateProperty: "string",  # You can use a "format": "date" in the schema for validation
    JSONProperty: "object",
    ArrayProperty: "array",
    UniqueIdProperty: "string",
}

# Define a mapping between Django field types and JSON schema types
FIELD_TYPE_MAPPING = {
    StringProperty: "string",
    IntegerProperty: "integer",
}

def get_field_type(field):
    for field_class, schema_type in FIELD_TYPE_MAPPING.items():
        if isinstance(field, field_class):
            return schema_type
    return None





def generate_schema_from_class(cls):
    schema = {"properties": {}, "relationships": {}}
    print(list(reversed(cls.__mro__)))
    cls_list = list(reversed(cls.__mro__))[6:]
    for cls in cls_list:
        print(cls.__name__)
        for attr_name, attr_value in cls.__dict__.items():
            # Check if the attribute is a relationship instance
            # print(attr_name, attr_value)
            if hasattr(attr_value, 'definition'):
                # Retrieve the relationship direction
                direction = attr_value.definition['direction']
                type = attr_value.definition['relation_type']
                model = attr_value.definition['model']
                cardinality = attr_value.manager.description
                # Determine the relationship type based on the direction
                if direction == 1:
                    relationship_type = 'RelationshipTo'
                    target = attr_value._raw_class.split('.')[-1]
                    origin = cls.__name__
                elif direction == -1:
                    relationship_type = 'RelationshipFrom'
                    origin = attr_value._raw_class.split('.')[-1]
                    target = cls.__name__
                else:
                    continue
                # Relationships

                schema["relationships"][attr_name] = {
                    "type": type,
                    'direction': relationship_type,
                    "target": target,
                    'origin': origin,
                    'model': model.__name__,
                    'cardinality': cardinality
                }
            elif isinstance(attr_value, NeoProperty):
                # Properties
                schema["properties"][attr_name] = {"type": get_field_type(attr_value),
                                                   "required": attr_value.required}


    return schema

schema = generate_schema_from_class(Material)
print(json.dumps(schema, indent = 4, sort_keys=True))