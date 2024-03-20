from typing import List

from langchain_core.pydantic_v1 import BaseModel, Field



class Edge(BaseModel):
    source: int|str = Field(None, description='node_id of the source node')
    target: int|str = Field(None, description='node_id of the target node')

class HasProperty(Edge):
    type: str = Field("has_property", description='Type of the edge')

class HasParameter(Edge):
    type: str = Field("has_parameter", description='Type of the edge')

class HasMeasurement(Edge):
    type: str = Field("has_measurement_output", description='Type of the edge')

class HasManufacturing(Edge):
    type: str = Field(None, description='Type of the edge, either "is_manufacturing_input" or "is_manufacturing_output". Extract edges that connect matter nodes that are educts to manufacturing steps and matter nodes that are products to manufacturing steps.')

class HasPropertyRelationships(BaseModel):
    relationships: List[HasProperty] = Field(None, description='List of has_property relationships')

class HasParameterRelationships(BaseModel):
    relationships: List[HasParameter] = Field(None, description='List of has_parameter relationships')

class HasMeasurementRelationships(BaseModel):
    relationships: List[HasMeasurement] = Field(None, description='List of has_measurement relationships')

class HasManufacturingRelationships(BaseModel):
    relationships: List[HasManufacturing] = Field(None, description='List of has_manufacturing relationships')