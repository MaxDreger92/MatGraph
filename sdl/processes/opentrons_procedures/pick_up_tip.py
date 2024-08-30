from sdl.processes.opentrons_utils import OpentronsBaseProcedure, OpentronsParamsMoveToLocation
from sdl.processes.opentrons_utils1 import OpentronsMoveAction


class PickUpTipParams(OpentronsParamsMoveToLocation):
    pass

class PickUpTip(OpentronsMoveAction[PickUpTipParams]):
    commandType = 'pickUpTip'
    url = '/runs/{run_id}/commands'
    intent = None

    def execute(self, *args, **kwargs):
        output = self.execute_all(*args, **kwargs)
        return output



