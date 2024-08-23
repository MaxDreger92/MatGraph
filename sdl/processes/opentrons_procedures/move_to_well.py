
from sdl.processes.opentrons_utils import OpentronsBaseProcedure, OpentronsParamsMoveToLocation


class MoveToWellParams(OpentronsParamsMoveToLocation):
    pass


class MoveToWell(OpentronsBaseProcedure[MoveToWellParams]):
    url = '/runs/{run_id}/commands'
    commandType = "moveToWell"
    intent = None
