from typing import List, Optional

from langchain_core.load import Serializable
from pydantic import BaseModel, Field, validator


class Node(Serializable):
    attributes: dict = Field(default_factory=dict, description='node properties')


class StringAttribute(BaseModel):
    """
    AttributeValue: specific value of the attribute can be extracted from the table column and inferred from context or the table header
    AttributeReference:  - If the attribute was inferred from "Context" or "Header", the index is either "guess" or "header".
            - If the attribute is extracted from the SampleRow the index is the ColumnIndex of the attribute.
    Rule : If the attribute value is an empty string, do not extract the attribute
    """
    AttributeValue: str = Field()
    AttributeReference: int|str = Field()
    def to_dict(self):
        return {
            "AttributeValue": self.AttributeValue,
            "AttributeReference": self.AttributeReference
        }

class FloatAttribute(BaseModel):
    """
    AttributeValue: specific value of the attribute can be extracted from the table column and inferred from context or the table header
    AttributeReference:  - If the attribute was inferred from "Context" or "Header", the index is either "guess" or "header".
            - If the attribute is extracted from the SampleRow the index is the ColumnIndex of the attribute.
    """
    AttributeValue: float|str = Field()
    AttributeReference: int|str = Field()
    def to_dict(self):
        return {
            "AttributeValue": self.AttributeValue,
            "AttributeReference": self.AttributeReference
        }

class Name(StringAttribute):
    """
    Node name
    """
    pass

class metadata_type(StringAttribute):
    """
    Node type
    """
    pass

class value(StringAttribute):
    """
    Node value
    """
    pass

class Value(FloatAttribute):
    """
    Value of a quantity
    AttributeValue: floating point number extracted from the table column if none available set to 0.0
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

class Unit(StringAttribute):
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
    Required fields: name (the name can be a single string or a list of strings)
    Optional fields: identifier, batch_number, ratio, concentration

    """
    identifier: Optional[Identifier] = None
    batch_number: Optional[BatchNumber] = None
    name: List[Name] = Field(description="Extract from the column, header or context.")
    def to_dict(self):
        return {
            "identifier": self.identifier.to_dict() if self.identifier else None,
            "batch_number": self.batch_number.to_dict() if self.batch_number else None,
            "name": [name.to_dict() for name in self.name]
        }

class QuantityAttributes(BaseModel):
    """
    Attributes of a specific quantity node. It is possible to have different nodes with the same name as long as they are extracted from
    different table.
    Required fields: name, unit, value
    Optional fields: error, average, standard_deviation
    Each attribute can have multiple values. The value of a quantity can be a single value or a range.
    """
    name: List[Name] = Field(description='Required field.')
    value: Optional[Value|List[Value]] = Field(description='Required field. Can be a single value or a list of values if a spectrum or array is given in the data.')
    error: Optional[Error|List[Error]] = None
    average: Optional[Average|List[Average]] = None
    standard_deviation: Optional[StandardDeviation|List[StandardDeviation]] = None
    unit: Unit = Field(description='Required field. Extract or guess the unit. The unit is never an array. Unitless quantities have the unit ""')
    def to_dict(self):
        return {
            "name": [name.to_dict() for name in self.name],
            "value": [v.to_dict() if hasattr(v, 'to_dict') else v for v in self.value] if isinstance(self.value, list) else self.value.to_dict() if self.value else None,
            "error": self.error.to_dict() if self.error else None,
            "average": self.average.to_dict() if self.average else None,
            "standard_deviation": [v.to_dict() if hasattr(v, 'to_dict') else v for v in self.standard_deviation] if isinstance(self.standard_deviation, list) else self.standard_deviation.to_dict() if self.standard_deviation else None,
            "unit": self.unit.to_dict() if self.unit else None
        }
class ProcessAttributes(BaseModel):
    """
    Attributes of a process node
    Required fields: name
    Optional fields: identifier
    Extract the name of the process from the table column. If the name is not given in the column infer it from the table header or the context.
    """
    identifier: Optional[Identifier] = None
    name: List[Name] = Field('missing',description='Required field.')
    def to_dict(self):
        return {
            "identifier": self.identifier.to_dict() if self.identifier else None,
            "name": [name.to_dict() for name in self.name]
        }

class MetadataAttributes(BaseModel):
    """
    Attributes of a metadata node
    Required fields: Type (Type of the metadata, for example "Facility", "Institution", "Researcher", "Project", "Funding" etc.)
    Optional fields: value (Value of the metadata, for example "University of Cambridge", "Max Planck Institute", "John Doe", "Project X", "Funding Agency Y" etc.)
    Extract the name of the process from the table column. If the name is not given in the column infer it from the table header or the context.
    """
    metadata_type: metadata_type
    value: Optional[value]
    def to_dict(self):
        return {
            "metadata_type": self.metadata_type.to_dict(),
            "name": self.value.to_dict()
        }

class MatterNode(Node):
    """
    Node representing a specific instance of a Material, Chemical, Device, Component, Product, Intermediate, etc.
    Example:
        - Matter: FuelCell
        - Matter: H2O
        - Matter: Gas Diffusion Layer
    """
    attributes: MatterAttributes = Field(None)
    def to_dict(self):
        return {
            "attributes": self.attributes.to_dict()
        }
class PropertyNode(Node):
    """
    Node representing a specific instance of a physical property
    REMARK: Usually each distinct "name", "value" pair should be represented as a separate node. The only exception are
    values that inherently are arrays (e.g. a spectrum) which should be represented as a single node.

    """
    attributes: QuantityAttributes = Field(None)
    def to_dict(self):
        return {
            "attributes": self.attributes.to_dict()
        }

class ParameterNode(Node):
    """
    Node representing a specific instance of a processing parameter
        REMARK: Usually each distinct "name", "value" pair should be represented as a separate node. The only exception are
    values that inherently are arrays (e.g. a spectrum) which should be represented as a single node.
    """
    attributes: QuantityAttributes = Field(None)
    def to_dict(self):
        return {
            "attributes": self.attributes.to_dict()
        }

class ManufacturingNode(Node):
    """
    Node representing a specific instance of a manufacturing node
    Example:
        - Manufacturing: StackAssembly
        - Manufacturing: Electro Spinning
    """
    attributes: ProcessAttributes = Field(None)
    def to_dict(self):
        return {
            "attributes": self.attributes.to_dict()
        }

class MeasurementNode(Node):
    """
    Node representing a specific instance of a measurement or characterization node
    Example:
        - Measurement: XRD
        - Measurement: SEM
    """
    attributes: ProcessAttributes = Field(None)
    def to_dict(self):
        return {
            "attributes": self.attributes.to_dict()
        }

class SimulationNode(Node):
    """
    Node representing a specific instance of a simulation node
    Example:
        - Simulation: DFT
        - Simulation: MD
    """
    attributes: ProcessAttributes = Field(None)
    def to_dict(self):
        return {
            "attributes": self.attributes.to_dict()
        }

class MetadataNode(Node):
    """
    Node representing a specific instance of a metadata node
    Example:
        - Metadata: Institution
        - Metadata: Researcher
    """
    attributes: MetadataAttributes = Field(None)
    def to_dict(self):
        return {
            "attributes": self.attributes.to_dict()
        }

class MatterNodeList(BaseModel):
    """
    List of all matter nodes (materials, chemicals, devices, components, products, intermediates, etc.) extracted from the table.
    Different instances of Materials, Chemicals, Devices, Components, Products, Intermediates, etc. need to be represented as different nodes.
    The final list of nodes need to represent the full content of the table which requires to infer the correct number of nodes and their attributes.
    """
    nodes: List[MatterNode] = Field(None)
    def to_dict(self):
        return {
            "nodes": [node.to_dict() for node in self.nodes]
        }


class PropertyNodeList(BaseModel):
    """
    List of all property nodes extracted from the table.
    REMARK: Usually each distinct name/value pair should be represented as separate nodes. The only exception are
    values that inherently are arrays (e.g. a spectrum) which should be represented as a single node.
    """
    nodes: List[PropertyNode] = Field(None)
    def to_dict(self):
        return {
            "nodes": [node.to_dict() for node in self.nodes]
        }

class ParameterNodeList(BaseModel):
    """
    List of all parameter nodes extracted from the table.
    """
    nodes: List[ParameterNode] = Field(None)
    def to_dict(self):
        return {
            "nodes": [node.to_dict() for node in self.nodes]
        }

class ManufacturingNodeList(BaseModel):
    """
    List of all manufacturing nodes extracted from the table.
    """
    nodes: List[ManufacturingNode] = Field(None)
    def to_dict(self):
        return {
            "nodes": [node.to_dict() for node in self.nodes]
        }

class MeasurementNodeList(BaseModel):
    """
    List of all measurement nodes extracted from the table.
    """
    nodes: List[MeasurementNode] = Field(None)
    def to_dict(self):
        return {
            "nodes": [node.to_dict() for node in self.nodes]
        }

class MetadataNodeList(BaseModel):
    """
    List of all metadata nodes extracted from the table.
    """
    nodes: List[MetadataNode] = Field(None)
    def to_dict(self):
        return {
            "nodes": [node.to_dict() for node in self.nodes]
        }



class SimulationNodeList(BaseModel):
    """
    List of all simulation nodes extracted from the table.
    """
    nodes: List[SimulationNode] = Field(None)
    def to_dict(self):
        return {
            "nodes": [node.to_dict() for node in self.nodes]
        }
