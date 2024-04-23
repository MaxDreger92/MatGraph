from typing import List

from langchain_core.pydantic_v1 import BaseModel, Field



class Edge(BaseModel):
    source: int = Field(None, description='node_id of the source node')
    target: int = Field(None, description='node_id of the target node')

class HasProperty(Edge):
    """
    Edge connecting matter nodes to property nodes.
    source: matter node
    target: property node
    """
    type: str = Field(choices=["has_property"])

class HasParameter(Edge):
    """
    Edge connecting manufacturing or measurement nodes to parameter nodes.
    source: manufacturing or measurement node
    target: parameter node
    """
    type: str = Field(choices =["has_parameter"])

class HasMeasurement(Edge):
    """
    Edge connecting measurement nodes to property nodes.
    source: measurement node
    target: property node
    """
    type: str = Field(choices = ["has_measurement_output"])

class HasManufacturing(Edge):
    """
    Edge connecting matter nodes to manufacturing steps.
    types:
     - is_manufacturing_input: connects the educt with a manufacturing step (source is matter node, target is manufacturing step)
     - has_manufacturing_output: connects the manufacturing step with its product (source is manufacturing step, target is matter node)
    """
    type: str = Field(None, choices=["is_manufacturing_input", "has_manufacturing_output"])

class HasPropertyRelationships(BaseModel):
    relationships: List[HasProperty] = Field(None, description='List of has_property relationships')

class HasParameterRelationships(BaseModel):
    """
    All has_parameter relationships.
    Each parameter needs to be connected to exactly one manufacturing or measurement node.
    """

    relationships: List[HasParameter] = Field(None, description='List of has_parameter relationships')

class HasMeasurementRelationships(BaseModel):
    relationships: List[HasMeasurement] = Field(None, description='List of has_measurement relationships')

class HasManufacturingRelationships(BaseModel):
    relationships: List[HasManufacturing] = Field(None, description='List of has_manufacturing relationships')