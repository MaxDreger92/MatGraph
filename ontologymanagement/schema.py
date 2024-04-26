from typing import List

from langchain_core.pydantic_v1 import BaseModel, Field, validator




class OntologyClass(BaseModel):
    """
    Ontology Class
    - name: Name of the class
    - alternative_labels: Alternative labels/synonymns of the class give name.
    They should never be more general or more specific or less specific as the name. Give at least one and at max 5 alternative labels.
    """
    name: str = Field(description="Name of the class")
    alternative_labels: List[str] = Field([], description="Alternative labels/synonymns of the class")

