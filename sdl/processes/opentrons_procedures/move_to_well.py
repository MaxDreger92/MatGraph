
from typing import Optional

from pydantic import BaseModel

from sdl.processes.opentrons_utils import WellLocation, OpentronsBaseProcedure


class MoveToWellParams(BaseModel):
    labwareId: str
    wellName: str
    pipetteId: str
    wellLocation: WellLocation
    speed: int


class MoveToWell(OpentronsBaseProcedure[MoveToWellParams]):
    url = '/runs/{run_id}/commands'
    commandType = "moveToWell"
    intent = None
