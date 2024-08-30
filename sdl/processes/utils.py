import uuid
from typing import Dict

from pydantic import BaseModel, Field


class ProcessOutput(BaseModel):
    id : str = Field(default = uuid.uuid4(), description="The ID of the process")
    status : str = Field(default = "success", description="The status of the process")
    output : Dict = Field(default = {}, description="The output of the process")
    input : Dict = Field(default = {}, description="The input of the process")
