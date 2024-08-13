from typing import TypeVar, Generic

from biologic.biologic.params import TechniqueParams
from biologic.biologic.technique import Technique
from pydantic import BaseModel

from sdl.workflow.utils import BaseProcedure

P = TypeVar('P', bound=TechniqueParams)

class BiologicBaseProcedure(BaseProcedure, Generic[P]):
    technique_cls=  Technique
    def __init__(self, params: P):
        self.params = params
        self.technique = self.technique_cls(params)

    def execute(self, *args, **kwargs):
        channel = kwargs.get("biologic_channel")
        if channel is None:
            raise ValueError("Biologic channel must be provided")
        self.runner = channel.run_techniques([self.technique])



