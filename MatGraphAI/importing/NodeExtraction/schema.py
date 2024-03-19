from typing import List

from langchain_core.pydantic_v1 import BaseModel, Field



class Name(BaseModel):
    name: str = Field(None, description='Name of the node')
    index: int = Field(None, description='Column Index of the name')

class Node(BaseModel):
    names: List[Name] = Field([])

class Value(BaseModel):
    value: float = Field(None, description='Float value')
    index: int = Field(None, description='Column Index of the value. If the attribute was inferred from context, the index is a string "inferred"')

class Error(BaseModel):
    error: float = Field(None, description='Error message')
    index: int = Field(None, description='Column Index of the error. If the attribute was inferred from context, the index is a string "inferred"')

class Average(BaseModel):
    average: float = Field(None, description='Average value')
    index: int = Field(None, description='Column Index of the average. If the attribute was inferred from context, the index is a string "inferred"')

class StandardDeviation(BaseModel):
    standard_deviation: float = Field(None, description='Standard deviation')
    index: int | str = Field(None, description='Column Index of the standard deviation. If the attribute was inferred from context, the index is a string "inferred"')

class Identifier(BaseModel):
    identifier: str = Field(None, description='Identifier of the process')
    index: int = Field(None, description='Column Index of the identifier. If the attribute was inferred from context, the index is a string "inferred"')

class Unit(BaseModel):
    unit: str = Field(None, description='Unit')
    index: int = Field(None, description='Column Index of the unit. If the attribute was inferred from context, the index is a string "inferred"')


class MatterAttributes(Node):
    identifier: str = Field(None, description='Identifier of the matter')
    batch_number: str = Field(None, description='Batch number of the matter')
    ratio: float = Field(None, description='Ratio of the matter')
    concentration: float = Field(None, description='Concentration of the matter')

class QuantityAttributes(Node):
    value: List[Value] = Field([])
    error: List[Error] = Field([])
    average: List[Average] = Field([])
    standard_deviation: List[StandardDeviation] = Field([])
    unit: Unit = Field(None)

class ProcessAttributes(Node):
    identifier: Identifier = Field(None, description='Attributes of the process')


class Matter(BaseModel):
    attributes: MatterAttributes = Field(None, description='Matter node')

class Property(BaseModel):
    attributes: QuantityAttributes = Field(None, description='Property node')

class Parameter(BaseModel):
    attributes: QuantityAttributes = Field(None, description='Parameter node')

class Manufacturing(BaseModel):
    attributes: ProcessAttributes = Field(None, description='Manufacturing node')

class Measurement(BaseModel):
    attributes: ProcessAttributes = Field(None, description='Measurement node')

class Metadata(BaseModel):
    attributes: ProcessAttributes = Field(None, description='Metadata node')


Properties = List[Property]
Parameters = List[Parameter]
Manufacturings = List[Manufacturing]
Measurements = List[Measurement]
Metadatas = List[Metadata]
Matters = List[Matter]
