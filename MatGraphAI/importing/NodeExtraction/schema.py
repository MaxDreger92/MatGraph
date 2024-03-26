from typing import List, Optional

from langchain_core.load import Serializable
from langchain_core.pydantic_v1 import BaseModel, Field, validator


class Node(Serializable):
    attributes: dict = Field(default_factory=dict, description='node properties')

class StringAttribute(BaseModel):
    """
    Optional string attribute
    """
    value: str = Field('',description='specific value of the attribute')
    index: int|str = Field('',description='column index of the attribute. If the name was inferred from context or the table header, the index is a string "inferred"')

class FloatAttribute(BaseModel):
    """
    Optional float attribute
    """
    value: str = Field('', description='specific value of the attribute')
    index: int|str = Field('', description='column index of the attribute. If the name was inferred from context or the table header, the index is a string "inferred"')

class Name(StringAttribute):
    """
    Node name can be typically extracted from the table column
    """
    pass

class Value(FloatAttribute):
    """
    Value of a quantity
    """
    pass

class Error(FloatAttribute):
    """
    Error of a quantity
    """
    pass

class Average(FloatAttribute):
    """
    Average value of a quantity
    """
    pass

class StandardDeviation(FloatAttribute):
    """
    Standard deviation of a quantity
    """
    pass

class Identifier(StringAttribute):
    """
    Identifier of the node
    """
    pass

class Unit(FloatAttribute):
    """
    Unit of a quantity
    """
    pass

class BatchNumber(StringAttribute):
    """
    Batch number of the matter
    """
    pass

class Ratio(FloatAttribute):
    """
    Ratio of the matter
    """
    pass

class Concentration(FloatAttribute):
    """
    Concentration of the matter
    """
    pass


class MatterAttributes(BaseModel):
    """
    Attributes of a specific matter node
    """
    identifier: Optional[Identifier] = None
    batch_number: Optional[BatchNumber] = None
    ratio: Optional[Ratio] = None
    concentration: Optional[Concentration] = None
    name: List[Name]

class QuantityAttributes(BaseModel):
    """
    Attributes of a quantity node
    """
    name: List[Name] = Field([])
    value: Optional[List[Value]] = None
    error: Optional[List[Error]] = None
    average: Optional[List[Average]] = None
    standard_deviation: Optional[List[StandardDeviation]] = None
    unit: Unit = Field('')

class ProcessAttributes(BaseModel):
    """
    Attributes of a process node
    """
    identifier: Optional[Identifier] = Field(None)
    name: List[Name] = Field(None)

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
    Example:
        - Property: Conductivity
    """
    attributes: QuantityAttributes = Field(None)

class ParameterNode(Node):
    """
    Node representing a specific instance of a processing parameter
    Example:
        - Parameter: Temperature
        - Parameter: Voltage
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
    Example:
        [
            {
                "name": "Battery",
                "identifier": "FC1",
            },
            {
                "name": "Electrode",
            }
        ]
    """
    nodes: List[MatterNode] = Field(None)


class PropertyNodeList(BaseModel):
    """
    List of all property nodes extracted from the table.
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




