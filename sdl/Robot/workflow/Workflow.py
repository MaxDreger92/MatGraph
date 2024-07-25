import importlib
import pkgutil

from sdl.Robot.workflow.ProcessingStep import LoopStep
from sdl.Robot.workflow.processes.lib.opentrons.models.aspirate import AspirateParams, Aspirate
from sdl.Robot.workflow.processes.lib.opentrons.models.dispense import Dispense, DispenseParams
from sdl.Robot.workflow.processes.lib.opentrons.models.home_robot import HomeRobot
from sdl.Robot.workflow.processes.lib.opentrons.models.move_to_well import MoveToWell, MoveToWellParams
from sdl.Robot.workflow.processes.opentrons_utils import WellLocation
from sdl.Robot.workflow.utils import BaseWorkflow


class HelloWorldWorkflow(BaseWorkflow):
    def __init__(self):
        super().__init__()
        self.operations = [HomeRobot()]
class FillWellWorkflow(BaseWorkflow):
    def __init__(self,
                 strSlot_from,
                 strWellName_from,
                 strOffsetStart_from,
                 strPipetteName,
                 strSlot_to,
                 strWellName_to,
                 strOffsetStart_to,
                 intVolume: int,
                 fltOffsetX_from: float = 0,
                 fltOffsetY_from: float = 0,
                 fltOffsetZ_from: float = 5,
                 fltOffsetX_to: float = 0,
                 fltOffsetY_to: float = 0,
                 fltOffsetZ_to: float = 5,
                 intMoveSpeed: int = 100,
                 intFlowrate: int = 100):
        super().__init__()
        self.operations = [LoopStep(action=
        BaseWorkflow(operations=[MoveToWell(params=MoveToWellParams(
            labwareId=strSlot_from,
            wellName=strWellName_from,
            pipetteId=strPipetteName,
            wellLocation=WellLocation(
                origin="top",
                offset={"x": fltOffsetX_from,
                        "y": fltOffsetY_from,
                        "z": 0}
            ),
            speed=intMoveSpeed
        )),
            Aspirate(params=AspirateParams(
                labwareId=strSlot_from,
                wellName=strWellName_to,
                pipetteId=strPipetteName,
                volume=50,
                flowRate=intFlowrate,
                wellLocation=WellLocation(
                    origin=strOffsetStart_from,
                    offset={"x": fltOffsetX_from,
                            "y": fltOffsetY_from,
                            "z": fltOffsetZ_from}))),
            MoveToWell(params=MoveToWellParams(
                labwareId=strSlot_to,
                wellName=strWellName_to,
                pipetteId=strPipetteName,
                wellLocation=WellLocation(
                    origin="top",
                    offset={"x": fltOffsetX_to,
                            "y": fltOffsetY_to,
                            "z": 0}
                ),
                speed=intMoveSpeed
            )),
            Dispense(params=DispenseParams(
                labwareId=strSlot_to,
                wellName=strWellName_to,
                pipetteId=strPipetteName,
                volume=50,
                flowRate=intFlowrate,
                wellLocation=WellLocation(
                    origin=strOffsetStart_to,
                    offset={"x": fltOffsetX_to,
                            "y": fltOffsetY_to,
                            "z": fltOffsetZ_to})
            ))]),
            counter=intVolume,
            limit=50,
            step_size=-50,
            condition=lambda x: x.counter > x.limit),
        BaseWorkflow(operations=[
            MoveToWell(params=MoveToWellParams(
                labwareId=strSlot_from,
                wellName=strWellName_from,
                pipetteId=strPipetteName,
                wellLocation=WellLocation(
                    origin="top",
                    offset={"x": fltOffsetX_from,
                            "y": fltOffsetY_from,
                            "z": 0}
                ),
                speed=intMoveSpeed
            )),
            Aspirate(params=AspirateParams(
                labwareId=strSlot_from,
                wellName=strWellName_to,
                pipetteId=strPipetteName,
                volume=50,
                flowRate=intFlowrate,
                wellLocation=WellLocation(
                    origin=strOffsetStart_from,
                    offset={"x": fltOffsetX_from,
                            "y": fltOffsetY_from,
                            "z": fltOffsetZ_from}))),
            MoveToWell(params=MoveToWellParams(
                labwareId=strSlot_to,
                wellName=strWellName_to,
                pipetteId=strPipetteName,
                wellLocation=WellLocation(
                    origin="top",
                    offset={"x": fltOffsetX_to,
                            "y": fltOffsetY_to,
                            "z": 0}
                ),
                speed=intMoveSpeed
            )),
            Dispense(params=DispenseParams(
                labwareId=strSlot_to,
                wellName=strWellName_to,
                pipetteId=strPipetteName,
                volume=50,
                flowRate=intFlowrate,
                wellLocation=WellLocation(
                    origin=strOffsetStart_to,
                    offset={"x": fltOffsetX_to,
                            "y": fltOffsetY_to,
                            "z": fltOffsetZ_to})
            ))])]


