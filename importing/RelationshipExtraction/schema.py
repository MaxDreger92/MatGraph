from typing import List, Union

from pydantic import BaseModel, Field



class Edge(BaseModel):
    source: str = Field(None, description='node_id of the source node')
    target: str = Field(None, description='node_id of the target node')

class HasProperty(Edge):
    """
    Edge connecting matter nodes to property nodes.
    source: matter node
    target: property node
    """
    type: str = Field(choices=["HAS_PROPERTY"])

class HasParameter(Edge):
    """
    Edge connecting manufacturing or measurement nodes to parameter nodes.
    source: manufacturing or measurement node
    target: parameter node
    """
    type: str = Field(choices =["HAS_PARAMETER"])

class HasMeasurement(Edge):
    """
    Edge connecting measurement nodes to property nodes.
    source: measurement node
    target: property node
    """
    type: str = Field(choices = ["HAS_MEASUREMENT_OUTPUT"])

class HasMetadata(Edge):
    """
    Edge connecting measurement nodes to property nodes.
    source: measurement/manufacturing node
    target: property node
    """
    type: str = Field(choices = ["HAS_MEASUREMENT_OUTPUT"])

class HasPartMatter(Edge):
    """
    Edge connecting matter to its component matter node (e.g., FuelCell, has_part, MEA)
    source: matter node
    target: matter node
    """
    type: str = Field(choices = ["has_part"])

class HasPartManufacturing(Edge):
    """
    Edge connecting manufacturing nodes to its subprocess manufacturing nodes (e.g. Solar Cell Fabrication, has_part, Spin Coating)
    source: manufacturing node
    target manufacturing node
    """
    type: str = Field(choices=["has_part"])


class HasPartMeasurement(Edge):
    """
    Edge connecting measurement nodes to its subprocess measurement nodes (e.g. Electron Microscopy, has_part, Sample Preparation)
    source: measurement node
    target measurement node
    """
    type: str = Field(choices=["has_part"])

class IsManufacturingInput(Edge):
    """
    Edge connecting matter nodes to manufacturing steps.
    type:
     - is_manufacturing_input: connects the educt with a manufacturing step (source is matter node, target is manufacturing step)
    """
    type: str = "is_manufacturing_input"

class HasManufacturingOutput(Edge):
    """
    Edge connecting matter nodes to manufacturing steps.
    type:
     - has_manufacturing_output: connects a manufacturing step with its product (source: manufactruing node, target: matter node)
    """
    type: str = "HAS_MANUFACTURING_OUTPUT"

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
    relationships: List[Union[HasManufacturingOutput, IsManufacturingInput]] = Field(None, description='List of matter-manufacturing relationships')


class HasPartMatterRelationships(BaseModel):
    relationships: List[HasPartMatter] = Field(None)

class HasPartMeasurementRelationships(BaseModel):
    relationships: List[HasPartMeasurement]

class HasPartManufacturingRelationships(BaseModel):
    relationships: List[HasPartManufacturing]

class HasMetadataRelationships(BaseModel):
    relationships: List[HasMetadata]