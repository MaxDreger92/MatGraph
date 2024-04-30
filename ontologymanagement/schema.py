from typing import List, Optional

from langchain_core.pydantic_v1 import BaseModel, Field, validator




class OntologyClass(BaseModel):
    """
    Ontology Class
    - name: Name of the class
    - alternative_labels: Alternative labels/synonymns of the class give name.
    They should never be more general or more specific or less specific as the name. Give at least one and at max 5 alternative labels.
    """
    name: str = Field(description="Name of the class")
    description: str = Field(description="Short scientific one sentence description of the class")
    alternative_labels: List[str] = Field([], description="Alternative labels/synonymns of the class")


class ChildClass(BaseModel):
    """
    SubClass among the given candidate.
    A SubClass is a subclass of the input class. This means the input class is a general type of the SubClass.
    (e.g. SnO2 is a SubClass of MetalOxide)
    """
    child_name: str = Field(description="Class Name")

class ParentClass(BaseModel):
    """
    ParentClass among the given candidate.
    A ParentClass is a superclass of the input class. This means the input class is a specific type of the ParentClass.
    (e.g. MetalOxide is a ParentClass of SnO2)
    """
    parent_name: str = Field(description="Class Name")

class Response(BaseModel):
    """
    Answer for the given input:
     - answer: ParentClass|SubClass
    The response should be either a ParentClass or a SubClass chosen from list of candidates.
    If no candidate is a subclass or parent class of the input "answer" is None.
    """
    answer: Optional[ParentClass|ChildClass] = Field(None)

class OntoClass(BaseModel):
    """
    Ontology Class
    - name: Name of the class
    """
    name: str = Field(description="Name of the class")

class ClassList(BaseModel):
    """
    List of classes going from the parent to class to the input class
    - classes: List of classes
    """
    classes: List[OntoClass] = Field([], description="List of classes")
