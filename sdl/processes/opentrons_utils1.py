import copy

from sdl.processes.biologic_utils import P
from sdl.processes.opentrons_procedures.move_to_well import MoveToWell, MoveToWellParams
from sdl.processes.opentrons_utils import OpentronsBaseProcedure


class OpentronsMoveAction(OpentronsBaseProcedure[P]):

    def execute_all(self, *args, **kwargs):
        params =copy.deepcopy(self.params)

        # Create a deep copy of wellLocation
        wellLocation = copy.deepcopy(params.wellLocation)
        wellLocation.origin = "top"

        # Initialize MoveToWell with parameters
        move_to_well = MoveToWell(MoveToWellParams(
            labwareId=params.labwareId,
            labwareLocation=params.labwareLocation,
            wellName=params.wellName,
            pipetteId=params.pipetteId,
            pipetteName=params.pipetteName,
            wellLocation=wellLocation,
            speed=params.speed
        ))

        # Prepare the output list
        output = []

        # Execute MoveToWell and append result to output
        output.append(move_to_well.execute(*args, **kwargs))

        # Execute the parent class's execute method instead of PickUpTip's execute method

        parent_output = super().execute(*args, **kwargs)
        output.append(parent_output)

        move_to_top = MoveToWell(MoveToWellParams(
            labwareId=params.labwareId,
            labwareLocation=params.labwareLocation,
            wellName=params.wellName,
            pipetteId=params.pipetteId,
            pipetteName=params.pipetteName,
            wellLocation=wellLocation,
            speed=params.speed
        ))

        move_to_top.execute(*args, **kwargs)

        return output
