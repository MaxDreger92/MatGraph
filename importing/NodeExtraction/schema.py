from typing import List, Optional

from langchain_core.load import Serializable
from langchain_core.pydantic_v1 import BaseModel, Field, validator


class Node(Serializable):
    attributes: dict = Field(default_factory=dict, description='node properties')


class Attribute(BaseModel):
    """
    AttributeValue: specific value of the attribute can be extracted from the table column and inferred from context or the table header
    AttributeReference:  - If the attribute was inferred from "Context" or "Header", the index is either "guess" or "header".
            - If the attribute is extracted from the SampleRow the index is the ColumnIndex of the attribute.
    Rule : If the attribute value is an empty string, do not extract the attribute
    """
    AttributeValue: float|str = Field('missing')
    AttributeReference: int|str = Field('missing')

class Name(Attribute):
    """
    Node name
    """
    pass

class Value(Attribute):
    """
    Value of a quantity
    """
    pass

class Error(Attribute):
    """
    Error of a quantity
    """
    pass

class Average(Attribute):
    """
    Average value of a quantity
    """
    pass

class StandardDeviation(Attribute):
    """
    Standard deviation of a quantity
    """
    pass

class Identifier(Attribute):
    """
    Identifier of the node
    """
    pass

class Unit(Attribute):
    """
    Unit of a quantity
    """
    pass

class BatchNumber(Attribute):
    """
    Batch number of the matter
    """
    pass

class Ratio(Attribute):
    """
    Ratio of the matter
    """
    pass

class Concentration(Attribute):
    """
    Concentration of the matter
    """
    pass


class MatterAttributes(BaseModel):
    """
    Attributes of a specific matter node
    Required fields: name (the name can be a single string or a list of strings)
    Optional fields: identifier, batch number, ratio, concentration

    """
    identifier: Optional[Identifier] = None
    batch_number: Optional[BatchNumber] = None
    ratio: Optional[Ratio] = None
    concentration: Optional[Concentration] = None
    name: List[Name] = Field(Name(AttributeValue='missing', AttributeReference='missing'), description="Extract from the column, header or context.")

class QuantityAttributes(BaseModel):
    """
    Attributes of a specific quantity node. It is possible to have different nodes with the same name as long as they are extracted from
    different table.
    Required fields: name, unit, value
    Optional fields: error, average, standard_deviation
    Each attribute can have multiple values. The value of a quantity can be a single value or a range.
    """
    name: Name|List[Name] = Field(Name(AttributeValue='missing', AttributeReference='missing'), description='Required field.')
    value: Value|List[Value]
    error: Optional[Error|List[Error]] = None
    average: Optional[Average|List[Average]] = None
    standard_deviation: Optional[StandardDeviation|List[StandardDeviation]] = None
    unit: Unit = Field(Unit(AttributeValue='missing', AttributeReference='missing'), description='Required field. Extract or guess the unit. The unit is never an array.')

class ProcessAttributes(BaseModel):
    """
    Attributes of a process node
    Required fields: name
    Optional fields: identifier
    Extract the name of the process from the table column. If the name is not given in the column infer it from the table header or the context.
    """
    identifier: Optional[Identifier] = None
    name: List[Name] = Field('missing',description='Required field.')

class MatterNode(Node):
    """
    Node representing a specific instance of a Material, Chemical, Device, Component, Product, Intermediate, etc.
    Example:
        - Matter: FuelCell
        - Matter: H2O
        - Matter: Gas Diffusion Layer
    """
    attributes: MatterAttributes = Field(None)

class PropertyNode(Node):
    """
    Node representing a specific instance of a physical property
    REMARK: Usually each distinct "name", "value" pair should be represented as a separate node. The only exception are
    values that inherently are arrays (e.g. a spectrum) which should be represented as a single node.

    """
    attributes: QuantityAttributes = Field(None)

class ParameterNode(Node):
    """
    Node representing a specific instance of a processing parameter
        REMARK: Usually each distinct "name", "value" pair should be represented as a separate node. The only exception are
    values that inherently are arrays (e.g. a spectrum) which should be represented as a single node.
    """
    attributes: QuantityAttributes = Field(None)

class ManufacturingNode(Node):
    """
    Node representing a specific instance of a manufacturing node
    Example:
        - Manufacturing: StackAssembly
        - Manufacturing: Electro Spinning
    """
    attributes: ProcessAttributes = Field(None)

class MeasurementNode(Node):
    """
    Node representing a specific instance of a measurement or characterization node
    Example:
        - Measurement: XRD
        - Measurement: SEM
    """
    attributes: ProcessAttributes = Field(None)

class MetadataNode(Node):
    """
    Node representing a specific instance of a metadata node
    Example:
        - Metadata: Institution
        - Metadata: Researcher
    """
    attributes: ProcessAttributes = Field(None)

class MatterNodeList(BaseModel):
    """
    List of all matter nodes (materials, chemicals, devices, components, products, intermediates, etc.) extracted from the table.
    Different instances of Materials, Chemicals, Devices, Components, Products, Intermediates, etc. need to be represented as different nodes.
    The final list of nodes need to represent the full content of the table which requires to infer the correct number of nodes and their attributes.
    """
    nodes: List[MatterNode] = Field(None)


class PropertyNodeList(BaseModel):
    """
    List of all property nodes extracted from the table.
    REMARK: Usually each distinct name/value pair should be represented as separate nodes. The only exception are
    values that inherently are arrays (e.g. a spectrum) which should be represented as a single node.
    """
    nodes: List[PropertyNode] = Field(None)

class ParameterNodeList(BaseModel):
    """
    List of all parameter nodes extracted from the table.
    """
    nodes: List[ParameterNode] = Field(None)

class ManufacturingNodeList(BaseModel):
    """
    List of all manufacturing nodes extracted from the table.
    """
    nodes: List[ManufacturingNode] = Field(None)

class MeasurementNodeList(BaseModel):
    """
    List of all measurement nodes extracted from the table.
    """
    nodes: List[MeasurementNode] = Field(None)

class MetadataNodeList(BaseModel):
    """
    List of all metadata nodes extracted from the table.
    """
    nodes: List[MetadataNode] = Field(None)




