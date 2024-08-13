from pydantic import BaseModel

from sdl.processes.opentrons_utils import OpentronsBaseProcedure


class PickUpTipParams(BaseModel):
    labwareId: str
    wellName: str
    pipetteId: str


class PickUpTip(OpentronsBaseProcedure[PickUpTipParams]):
    commandType = 'pickUpTip'
    url = '/runs/{run_id}/commands'
    intent = None
