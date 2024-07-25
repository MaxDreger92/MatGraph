# generated by datamodel-codegen:
#   filename:  aspirate.json
#   timestamp: 2024-07-17T19:03:43+00:00

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from sdl.Robot.workflow.processes.opentrons_utils import WellLocation, Offset, OpentronsBaseProcedure


class AspirateParams(BaseModel):
    labwareId: str
    wellName: str
    pipetteId: str
    volume: int
    flowRate: float = 100
    wellLocation: WellLocation = WellLocation(origin='top', offset=Offset(x=0, y=0, z=0))


class Aspirate(OpentronsBaseProcedure):
    url: str = '/runs/{run_id}/commands'
    commandType = "aspirate"
    params: AspirateParams
    intent: Optional[str] = None
