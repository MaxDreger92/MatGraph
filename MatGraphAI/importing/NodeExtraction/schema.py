from typing import List

from langchain_core.pydantic_v1 import BaseModel, Field



class Name(BaseModel):
    name: str = Field(None, description='specific name or description')
    index: int|str = Field(None, description='column Index of the name. If the name was inferred from context, the index is a string "inferred"')

class Node(BaseModel):
    name: List[Name] = Field([], description='All names of this instance. An instance can have more than one name if those names really refer to the same instance.')

class Value(BaseModel):
    value: float = Field(None, description='Float value')
    index: int|str = Field(None, description='Column Index of the value. If the attribute was inferred from context, the index is a string "inferred"')

class Error(BaseModel):
    error: float = Field(None, description='Error message')
    index: int|str = Field(None, description='Column Index of the error. If the attribute was inferred from context, the index is a string "inferred"')

class Average(BaseModel):
    average: float = Field(None, description='Average value')
    index: int|str  = Field(None, description='Column Index of the average. If the attribute was inferred from context, the index is a string "inferred"')

class StandardDeviation(BaseModel):
    standard_deviation: float = Field(None, description='Standard deviation')
    index: int | str = Field(None, description='Column Index of the standard deviation. If the attribute was inferred from context, the index is a string "inferred"')

class Identifier(BaseModel):
    identifier: str = Field(None, description='Identifier of the instance')
    index: int|str = Field(None, description='Column Index of the identifier. If the attribute was inferred from context, the index is a string "inferred"')

class Unit(BaseModel):
    unit: str = Field(None, description='Unit')
    index: int|str = Field(None, description='Column Index of the unit. If the attribute was inferred from context, the index is a string "inferred"')

class BatchNumber(BaseModel):
    batch_number: str = Field(None, description='Batch number of the matter')
    index: int|str = Field(None, description='Column Index of the batch number. If the attribute was inferred from context, the index is a string "inferred"')

class Ratio(BaseModel):
    ratio: float = Field(None, description='Ratio of the matter')
    index: int|str = Field(None, description='Column Index of the ratio. If the attribute was inferred from context, the index is a string "inferred"')

class Concentration(BaseModel):
    concentration: float = Field(None, description='Concentration of the matter')
    index: int|str = Field(None, description='Column Index of the concentration. If the attribute was inferred from context, the index is a string "inferred"')

class MatterAttributes(Node):
    identifier: Identifier = Field(None, description='Identifier of the matter')
    batch_number: BatchNumber = Field(None, description='Batch number of the matter')
    ratio: Ratio = Field(None, description='Ratio of the matter')
    concentration: Concentration = Field(None, description='Concentration of the matter')

class QuantityAttributes(Node):
    value: List[Value] = Field([])
    error: List[Error] = Field([])
    average: List[Average] = Field([])
    standard_deviation: List[StandardDeviation] = Field([])
    unit: Unit = Field(None)

class ProcessAttributes(Node):
    identifier: Identifier = Field(None, description='Attributes of the process')


class Matter(BaseModel):
    attributes: MatterAttributes = Field(None, description='specific instance of a Material, Chemical, Device, Component, Product, Intermediate, etc. node')

class Property(BaseModel):
    attributes: QuantityAttributes = Field(None, description='specific instance of a physical property node')

class Parameter(BaseModel):
    attributes: QuantityAttributes = Field(None, description='specific instance of a processing parameter node')

class Manufacturing(BaseModel):
    attributes: ProcessAttributes = Field(None, description='specific instance of a manufacturing node')

class Measurement(BaseModel):
    attributes: ProcessAttributes = Field(None, description='specific instance of a measurement or characterization node')

class Metadata(BaseModel):
    attributes: ProcessAttributes = Field(None, description='specific instance of a metadata node')


class Properties(BaseModel):
    instances: List[Property] = Field([], description='All instances of property nodes extracted from the table')

class Parameters(BaseModel):
    instances: List[Parameter] = Field([], description='All instances of parameter nodes extracted from the table')

class Matters(BaseModel):
    instances: List[Matter] = Field([], description='All distinguishable instances of specifc matter (materials, chemicals, devices, components, products, intermediates, etc.) nodes extracted from the table')

class Manufacturings(BaseModel):
    instances: List[Manufacturing] = Field([], description='All instances of manufacturing nodes extracted from the table')

class Measurements(BaseModel):
    instances: List[Measurement] = Field([], description='All instances of measurement nodes extracted from the table')

class Metadatas(BaseModel):
    instances: List[Metadata] = Field([], description='All instances of metadata nodes extracted from the table')


