# generated by datamodel-codegen:
#   filename:  aspirate.json
#   timestamp: 2024-07-17T19:03:43+00:00

from __future__ import annotations

from typing import Optional

from sdl.processes.opentrons_utils import WellLocation, Offset, OpentronsBaseProcedure, OpentronsParamsMoveToLocation
from sdl.processes.opentrons_utils1 import OpentronsMoveAction


class AspirateParams(OpentronsParamsMoveToLocation):
    volume: int
    flowRate: float = 100
    wellLocation : Optional[WellLocation] = WellLocation(origin='bottom', offset=Offset(x=0, y=0, z=2))



class Aspirate(OpentronsMoveAction[AspirateParams]):
    url: str = '/runs/{run_id}/commands'
    commandType = "aspirate"
    intent: Optional[str] = None
    chemical: Optional[str] = None

    def execute(self, *args, **kwargs):
        print("Aspirate execute")
        print(self.params)
        output = self.execute_all(*args, **kwargs)
        return output