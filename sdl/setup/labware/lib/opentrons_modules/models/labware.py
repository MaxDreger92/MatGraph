import json

from pydantic import BaseModel
from typing import List, Dict, Optional

class Well(BaseModel):
    depth: float
    totalLiquidVolume: float
    shape: str
    diameter: Optional[float] = None
    xDimension: Optional[float] = None
    yDimension: Optional[float] = None
    x: float
    y: float
    z: float

class Metadata(BaseModel):
    displayName: str
    displayCategory: str
    displayVolumeUnits: str
    tags: List[str]

class Dimensions(BaseModel):
    xDimension: float
    yDimension: float
    zDimension: float

class GroupMetadata(BaseModel):
    wellBottomShape: Optional[str] = None

class Group(BaseModel):
    metadata: GroupMetadata
    wells: List[str]

class Parameters(BaseModel):
    format: str
    quirks: List[str]
    isMagneticModuleCompatible: bool
    loadName: str
    tipLength: Optional[float] = None  # Optional attribute for tip racks

class CornerOffsetFromSlot(BaseModel):
    x: float
    y: float
    z: float

class Brand(BaseModel):
    brand: str
    brandId: List[str]

class Labware(BaseModel):
    ordering: List[List[str]]
    brand: Brand
    metadata: Metadata
    dimensions: Dimensions
    wells: Dict[str, Well]
    groups: List[Group]
    parameters: Parameters
    namespace: str
    version: int
    schemaVersion: int
    cornerOffsetFromSlot: CornerOffsetFromSlot

    @classmethod
    def load_labware_from_file(cls, filename: str) -> 'Labware':
        with open(filename) as f:
            data = json.load(f)
        return cls(**data)
