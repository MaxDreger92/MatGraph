from biologic.biologic.techniques.ca import CAStep, CAParams
from biologic.biologic.techniques.cpp import CPPParams
from biologic.biologic.techniques.ocv import OCVParams
from biologic.biologic.techniques.peis import PEISParams, SweepMode
from biologic.kbio.types import BANDWIDTH, E_RANGE, I_RANGE

from sdl.processes.arduino_procedures.dispense_ml import DispenseMl
from sdl.processes.arduino_procedures.set_ultrasound import SetUltrasoundOn
from sdl.processes.biologic_procedures.CA import CA
from sdl.processes.biologic_procedures.CPP import CPP
from sdl.processes.biologic_procedures.OCV import OCV
from sdl.processes.biologic_procedures.PEIS import PEIS
from sdl.processes.opentrons_procedures.aspirate import Aspirate, AspirateParams
from sdl.processes.opentrons_procedures.dispense import Dispense, DispenseParams
from sdl.processes.opentrons_procedures.drop_tip import DropTip, DropTipParams
from sdl.processes.opentrons_procedures.home_robot import HomeRobot
from sdl.processes.opentrons_procedures.move_to_well import MoveToWell, MoveToWellParams
from sdl.processes.opentrons_procedures.pick_up_tip import PickUpTip, PickUpTipParams
from sdl.processes.opentrons_utils import WellLocation
from sdl.workflow.ProcessingStep import AddPythonCode
from sdl.workflow.utils import BaseWorkflow


class HelloWorldWorkflow(BaseWorkflow):
    def __init__(self):
        super().__init__()
        self.operations = [HomeRobot()]


class ResetWorkflow(BaseWorkflow):
    def __init__(self, pipette_location, pipette_id):
        super().__init__()
        self.operations = [
            HomeRobot(params={}),
            MoveToWell(MoveToWellParams(
                labwareId=pipette_location,
                wellName="A1",
                speed=100,
                wellLocation=WellLocation(
                    origin="top",
                    offset={"x": 0,
                            "y": 0,
                            "z": 0}
                ),
                pipetteId=pipette_id)),
            PickUpTip(params=PickUpTipParams(
                pipetteId=pipette_id,
                labwareId=pipette_location,
                wellName="A1",
                wellLocation=WellLocation(
                    origin="center",
                    offset={"x": 0,
                            "y": 0,
                            "z": 0})))]


class GoHomeWorkflow(BaseWorkflow):
    def __init__(self, pipette_location, pipette_id):
        super().__init__()
        self.operations = [
            HomeRobot(params={}),
            MoveToWell(params=MoveToWellParams(
                labwareId=pipette_location,
                pipetteId=pipette_id,
                wellName="A1",
                speed=100,
                wellLocation=WellLocation(
                    origin="top",
                    offset={"x": 0,
                            "y": 0,
                            "z": 0}
                ))),
            DropTip(params=DropTipParams(
                pipetteId=pipette_id,
                labwareId=pipette_location,
                wellName="A1",
                wellLocation=WellLocation(
                    origin="center",
                    offset={"x": 0,
                            "y": 0,
                            "z": 0}))),
            HomeRobot(params={})]


def fill_well_workflow(
        strSlot_from,
        strWellName_from,
        strOffsetStart_from,
        strPipetteName,
        strSlot_to,
        strWellName_to,
        strOffsetStart_to,
        step_size: int,
        intVolume: int,
        limit: int = 50,
        fltOffsetX_from: float = 0,
        fltOffsetY_from: float = 0,
        fltOffsetZ_from: float = 5,
        fltOffsetX_to: float = 0,
        fltOffsetY_to: float = 0,
        fltOffsetZ_to: float = 5,
        intMoveSpeed: int = 100,
        intFlowrate: int = 50,
        **kwargs
):
    outputs = []
    operation1 = BaseWorkflow(operations=[
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
            volume=step_size,
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
            volume=step_size,
            flowRate=intFlowrate,
            wellLocation=WellLocation(
                origin=strOffsetStart_to,
                offset={"x": fltOffsetX_to,
                        "y": fltOffsetY_to,
                        "z": fltOffsetZ_to})
        ))])
    while intVolume > limit:
        output = operation1.execute(**kwargs)
        outputs = [*outputs, *output]

        intVolume -= step_size
        operation2 = (BaseWorkflow(operations=[
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
                volume=intVolume,
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
                volume=intVolume,
                flowRate=intFlowrate,
                wellLocation=WellLocation(
                    origin=strOffsetStart_to,
                    offset={"x": fltOffsetX_to,
                            "y": fltOffsetY_to,
                            "z": fltOffsetZ_to})
            ))]))
        output = operation2.execute(**kwargs)
        outputs = [*outputs, *output]
        return outputs


class WashElectrodeWorkflow(BaseWorkflow):
    def __init__(self,
                 strLabwareName,
                 well_name="A2",
                 pipette_id="p300_single_v2.0",
                 ):
        super().__init__()
        self.operations = [
            DispenseMl(
                volume=15,
                relay_num=4
            ),
            MoveToWell(
                labwareId=1,
                wellName=well_name,
                pipetteId=pipette_id,
                speed=50,
                wellLocation=WellLocation(
                    origin="top",
                    offset={"x": 0,
                            "y": 0,
                            "z": 0}
                )
            ),
            MoveToWell(
                labwareId=1,
                wellName=well_name,
                pipetteId=pipette_id,
                speed=50,
                wellLocation=WellLocation(
                    origin="bottom",
                    offset={"x": 0,
                            "y": -15,
                            "z": -10}
                )
            ),
            SetUltrasoundOn(
                time=30,
                relay_num=6
            ),
            DispenseMl(
                volume=16,
                relay_num=3
            ),
            DispenseMl(
                volume=10,
                relay_num=5
            ),
            SetUltrasoundOn(
                time=30,
                relay_num=6
            ),
            DispenseMl(
                volume=11,
                relay_num=3
            ),
            DispenseMl(
                volume=15,
                relay_num=4
            ),
            SetUltrasoundOn(
                time=30,
                relay_num=6
            ),
            DispenseMl(
                volume=16,
                relay_num=3
            )]


class FullWorkFlow(BaseWorkflow):
    def __init__(self,
                 tipRack,
                 pipette,
                 strSlot_from,
                 strWellName_from,
                 strOffsetStart_from,
                 strPipetteName,
                 strSlot_to,
                 strWellName_to,
                 strOffsetStart_to,
                 intVolume,
                 limit,
                 ElectrodeTipRack,
                 step_size,
                 autodialCell,
                 strWell2Test_autodialCell,
                 washstation):
        super().__init__()
        self.operations = [
            HomeRobot(params={}),
            MoveToWell(params=MoveToWellParams(
                labwareId=tipRack,
                wellName="A1",
                pipetteId=pipette,
                speed=100,
                wellLocation=WellLocation(
                    origin="top",
                    offset={"x": 0,
                            "y": 1,
                            "z": 0}
                ))),
            PickUpTip(params=PickUpTipParams(
                pipetteId="p300_single_v2.0",
                labwareId=tipRack,
                wellName="A12",
                wellLocation=WellLocation(
                    origin="top",
                    offset={"x": 0,
                            "y": 1,
                            "z": 0}))),
            AddPythonCode(
                fill_well_workflow,
                strSlot_from=strSlot_from,
                strWellName_from=strWellName_from,
                strOffsetStart_from=strOffsetStart_from,
                strPipetteName=strPipetteName,
                strSlot_to=strSlot_to,
                strWellName_to=strWellName_to,
                strOffsetStart_to=strOffsetStart_to,
                intVolume=intVolume,
                limit=limit,
                step_size=step_size),
            MoveToWell(MoveToWellParams(
                labwareId=tipRack,
                wellName="A1",
                pipetteId=pipette,
                speed=100,
                wellLocation=WellLocation(
                    origin="top",
                    offset={"x": 0,
                            "y": 1,
                            "z": 0}
                ))),
            DropTip(DropTipParams(
                pipetteId=pipette,
                labwareId=tipRack,
                wellName="A1",
                wellLocation=WellLocation(
                    origin="bottom",
                    offset={"x": 0,
                            "y": 1,
                            "z": 0}
                ))),
            MoveToWell(MoveToWellParams(
                labwareId=tipRack,
                wellName="A12",
                pipetteId=pipette,
                speed=100,
                wellLocation=WellLocation(
                    origin="top",
                    offset={"x": 0,
                            "y": 1,
                            "z": 0}
                ))),
            PickUpTip(PickUpTipParams(
                pipetteId=pipette,
                labwareId=tipRack,
                wellName="A12",
                wellLocation=WellLocation(
                    origin="center",
                    offset={"x": 0,
                            "y": 0,
                            "z": 0}
                ))),
            AddPythonCode(
                fill_well_workflow,
                strSlot_from=strSlot_from,
                strWellName_from=strWellName_from,
                strOffsetStart_from=strOffsetStart_from,
                strPipetteName=strPipetteName,
                strSlot_to=strSlot_to,
                strWellName_to=strWellName_to,
                strOffsetStart_to=strOffsetStart_to,
                intVolume=intVolume,
                limit=limit,
                step_size=step_size),
            MoveToWell(MoveToWellParams(
                labwareId=tipRack,
                wellName="A12",
                pipetteId=pipette,
                speed=100,
                wellLocation=WellLocation(
                    origin="top",
                    offset={"x": 0,
                            "y": 1,
                            "z": 0}
                ))),
            DropTip(DropTipParams(
                pipetteId=pipette,
                labwareId=tipRack,
                wellName="A12",
                wellLocation=WellLocation(
                    origin="bottom",
                    offset={"x": 0,
                            "y": 1,
                            "z": 0}
                ))),
            MoveToWell(MoveToWellParams(
                labwareId=ElectrodeTipRack,
                wellName="A2",
                pipetteId=pipette,
                speed=100,
                wellLocation=WellLocation(
                    origin="top",
                    offset={"x": 0.6,
                            "y": 0.5,
                            "z": 3}
                ))),
            PickUpTip(PickUpTipParams(
                pipetteId=pipette,
                labwareId=ElectrodeTipRack,
                wellName="A2",
                wellLocation=WellLocation(
                    origin="center",
                    offset={"x": 0.6,
                            "y": 0.5,
                            "z": 0}
                ))),
            MoveToWell(MoveToWellParams(
                labwareId=autodialCell,
                wellName=strWell2Test_autodialCell,
                pipetteId=pipette,
                speed=50,
                wellLocation=WellLocation(
                    origin="top",
                    offset={"x": 0.5,
                            "y": 0.5,
                            "z": 5}
                ))),
            MoveToWell(MoveToWellParams(
                labwareId=autodialCell,
                wellName=strWell2Test_autodialCell,
                pipetteId=pipette,
                speed=50,
                wellLocation=WellLocation(
                    origin="bottom",
                    offset={"x": 0.5,
                            "y": 0.5,
                            "z": -25}
                ))),
            WashElectrodeWorkflow(
                strLabwareName=washstation,

            ),
            HomeRobot(params={})
        ]

class ElectrochemicalExperiments(BaseWorkflow):
    def __init__(self):
        super().__init__()
        self.operations = [
            PEIS(PEISParams(
                vs_initial = False,
                initial_voltage_step = 0.0,
                duration_step = 0,
                record_every_dT = 0.5,
                record_every_dI = 0.01,
                final_frequency = 1,
                initial_frequency = 100000,
                sweep = SweepMode.Logarithmic,
                amplitude_voltage = 0.02,
                frequency_number = 50,
                average_n_times = 4,
                correction = False,
                wait_for_steady = 0.1,
                bandwidth = BANDWIDTH.BW_5,
                E_range = E_RANGE.E_RANGE_10V,
            )),
        PEIS(PEISParams(
            vs_initial = False,
            initial_voltage_step = 0.0,
            duration_step = 0,
            record_every_dT = 0.5,
            record_every_dI = 0.01,
            final_frequency = 0.1,
            initial_frequency = 100000,
            sweep = SweepMode.Logarithmic,
            amplitude_voltage = 0.01,
            frequency_number = 60,
            average_n_times = 3,
            correction = False,
            wait_for_steady = 0.1,
            bandwidth = BANDWIDTH.BW_5,
            E_range = E_RANGE.E_RANGE_10V,
        )),
        OCV(OCVParams(
            rest_time_T = 1800,
            record_every_dT = 0.5,
            record_every_dE = 10,
            E_range = E_RANGE.E_RANGE_10V,
            bandwidth = BANDWIDTH.BW_5,
        )),
        OCV(OCVParams(
            rest_time_T = 900,
            record_every_dT = 0.5,
            record_every_dE = 10,
            E_range = E_RANGE.E_RANGE_10V,
            bandwidth = BANDWIDTH.BW_5,
        )),
        OCV(OCVParams(
            rest_time_T = 600,
            record_every_dT = 0.5,
            record_every_dE = 10,
            E_range = E_RANGE.E_RANGE_10V,
            bandwidth = BANDWIDTH.BW_5,
        )),
        OCV(OCVParams(
            rest_time_T = 10,
            record_every_dT = 0.5,
            record_every_dE = 10,
            E_range = E_RANGE.E_RANGE_10V,
            bandwidth = BANDWIDTH.BW_5,
        )),
        CA(CAParams(
            record_every_dT = 0.5,
            record_every_dI = 0.01,
            n_cycles = 0,
            steps = [CAStep(
                voltage = -1.0,
                duration = 600,
                vs_initial = False
            )],
            I_range = I_RANGE.I_RANGE_10uA,
        )),
        CPP(CPPParams(
            record_every_dEr = 10,
            rest_time_T = 1800,
            record_every_dTr = 0.5,
            vs_initial_scan = (True,True,True),
            voltage_scan = (-0.25, 1.5, -0.25),
            scan_rate = (0.01, 0.01, 0.01),
            I_pitting = 0.01,
            t_b = 10,
            record_every_dE = 0.01,
            average_over_dE = False,
            begin_measuring_I = 0.75,
            end_measuring_I = 1.0,
            record_every_dT = 0.5))]



class TestBiologic(BaseWorkflow):
    operations = [OCV(OCVParams(
        rest_time_T = 10,
        record_every_dT = 0.5,
        record_every_dE = 10,
        E_range = E_RANGE.E_RANGE_10V,
        bandwidth = BANDWIDTH.BW_5,
    ))]
