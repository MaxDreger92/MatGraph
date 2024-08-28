import time

from biologic import connect
from biologic.techniques.ca import CAParams, CAStep
from biologic.techniques.cpp import CPPParams
from biologic.techniques.ocv import OCVParams
from biologic.techniques.peis import PEISParams, SweepMode
from kbio.types import BANDWIDTH, E_RANGE, I_RANGE

from sdl.processes.arduino_procedures.dispense_ml import DispenseMl
from sdl.processes.arduino_procedures.set_ultrasound import SetUltrasoundOn, SetUltrasoundParams
from sdl.processes.biologic_procedures.CA import CA
from sdl.processes.biologic_procedures.CPP import CPP
from sdl.processes.biologic_procedures.OCV import OCV
from sdl.processes.biologic_procedures.PEIS import PEIS
from sdl.processes.biologic_utils import BiologicBaseProcedure
from sdl.processes.opentrons_procedures.aspirate import Aspirate, AspirateParams
from sdl.processes.opentrons_procedures.dispense import Dispense, DispenseParams
from sdl.processes.opentrons_procedures.drop_tip import DropTip, DropTipParams
from sdl.processes.opentrons_procedures.home_robot import HomeRobot, HomeRobotParams
from sdl.processes.opentrons_procedures.move_to_well import MoveToWell, MoveToWellParams
from sdl.processes.opentrons_procedures.pick_up_tip import PickUpTip, PickUpTipParams
from sdl.processes.opentrons_utils import WellLocation
from sdl.workflow.ProcessingStep import AddPythonCode
from sdl.workflow.utils import BaseWorkflow


class HelloWorldWorkflow(BaseWorkflow):
    def __init__(self):
        super().__init__()
        self.operations = [HomeRobot(HomeRobotParams())]


class ResetWorkflow(BaseWorkflow):
    def __init__(self, pipette_location, pipette_id):
        super().__init__()
        self.operations = [
            HomeRobot(HomeRobotParams()),
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
            HomeRobot(HomeRobotParams()),
            MoveToWell(MoveToWellParams(
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
            DropTip(DropTipParams(
                pipetteId=pipette_id,
                labwareId=pipette_location,
                wellName="A1",
                wellLocation=WellLocation(
                    origin="center",
                    offset={"x": 0,
                            "y": 0,
                            "z": 0}))),
            HomeRobot(HomeRobotParams())]


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
        fltOffsetZ_from: float = 6,
        fltOffsetX_to: float = 0,
        fltOffsetY_to: float = 0,
        fltOffsetZ_to: float = 5,
        intMoveSpeed: int = 100,
        intFlowrate: int = 50,
        **kwargs
):
    outputs = []
    operation1 = BaseWorkflow(operations=[
        Aspirate(AspirateParams(
            labwareLocation=strSlot_from,
            wellName=strWellName_from,
            pipetteId=strPipetteName,
            volume=step_size,
            flowRate=intFlowrate,
            wellLocation=WellLocation(
                origin=strOffsetStart_from,
                offset={"x": fltOffsetX_from,
                        "y": fltOffsetY_from,
                        "z": fltOffsetZ_from}))),
        Dispense(params=DispenseParams(
            labwareLocation=strSlot_to,
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
            Aspirate(params=AspirateParams(
                labwareLocation=strSlot_from,
                wellName=strWellName_from,
                pipetteId=strPipetteName,
                volume=intVolume,
                flowRate=intFlowrate,
                wellLocation=WellLocation(
                    origin=strOffsetStart_from,
                    offset={"x": fltOffsetX_from,
                            "y": fltOffsetY_from,
                            "z": fltOffsetZ_from}))),
            Dispense(params=DispenseParams(
                labwareLocation=strSlot_to,
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
            DispenseMl(DispenseParams(
                volume=15,
                relay_num=4
            )),
            MoveToWell(MoveToWellParams(
                labwareId=1,
                wellName=well_name,
                pipetteId=pipette_id,
                speed=50,
                wellLocation=WellLocation(
                    origin="top",
                    offset={"x": 0,
                            "y": 0,
                            "z": 0}
                ))
            ),
            MoveToWell(MoveToWellParams(
                labwareId=1,
                wellName=well_name,
                pipetteId=pipette_id,
                speed=50,
                wellLocation=WellLocation(
                    origin="bottom",
                    offset={"x": 0,
                            "y": -15,
                            "z": -10}
                ))
            ),
            SetUltrasoundOn(SetUltrasoundParams(
                time=30,
                relay_num=6
            )),
            DispenseMl(DispenseParams(
                volume=16,
                relay_num=3
            )),
            DispenseMl(DispenseParams(
                volume=10,
                relay_num=5
            )),
            SetUltrasoundOn(SetUltrasoundParams(
                time=30,
                relay_num=6
            )),
            DispenseMl(DispenseParams(
                volume=11,
                relay_num=3
            )),
            DispenseMl(DispenseParams(
                volume=15,
                relay_num=4
            )),
            SetUltrasoundOn(SetUltrasoundParams(
                time=30,
                relay_num=6
            )),
            DispenseMl(DispenseParams(
                volume=16,
                relay_num=3
            ))]

class BiologicWorkflow(BaseWorkflow):
    def __init__(self, operations: list[BiologicBaseProcedure]):
        super().__init__()
        self.operations = operations

    def execute(self, *args, **kwargs):
        logger = kwargs.get("logger")
        self.intAttempts_temp = 0
        while self.boolTryToConnect and self.intAttempts_temp < self.intMaxAttempts:
            logger.info(f"Attempting to connect to the Biologic: {self.intAttempts_temp + 1} / {self.intMaxAttempts}")

            try:
                with connect('USB0', force_load=True) as bl:
                    channel = bl.get_channel(1)
                    # Run the experiment after a successful connection
                    logger.info("Experiment started successfully.")
                    runner = channel.run_techniques(self.operations)

                    # If successful, break out of the loop
                    for data_temp in runner:
                        print(data_temp)
                    self.boolTryToConnect = False
            except Exception as e:
                logger.error(f"Failed to connect to the Biologic: {e}")
                self.intAttempts_temp += 1
                time.sleep(5)


class FullWorkFlow(BaseWorkflow):
    def __init__(self,
                 # tipRack,
                 # pipette,
                 # strSlot_from,
                 # strWellName_from,
                 # strOffsetStart_from,
                 # strPipetteName,
                 # strSlot_to,
                 # strWellName_to,
                 # strOffsetStart_to,
                 # intVolume,
                 # limit,
                 # ElectrodeTipRack,
                 # step_size,
                 # autodialCell,
                 # strWell2Test_autodialCell,
                 # washstation
                 MeasuringWell,
                 MaterialWell,
                 pipetteWell,
                 Volume,

                 ):
        super().__init__()
        self.operations = [
            HomeRobot(HomeRobotParams()),
            MoveToWell(MoveToWellParams(
                labwareLocation= 1,
                wellName=pipetteWell,
                speed=100,
                wellLocation=WellLocation(
                    origin="top",
                    offset={"x": 0, #NEEDS TO BE DETERMINED
                            "y": 0, #NEEDS TO BE DETERMINED
                            "z": 0} #NEEDS TO BE DETERMINED
                ))),
            PickUpTip(PickUpTipParams(
                labwareLocation=1,
                wellName=pipetteWell,
                wellLocation=WellLocation(
                    origin="top",
                    offset={"x": 0,
                            "y": 0,
                            "z": 0}))),
            AddPythonCode(
                fill_well_workflow,
                strSlot_from="2", #NEEDS TO BE DETERMINED
                strWellName_from=MaterialWell,
                strOffsetStart_from='bottom',
                strPipetteName=None,
                strSlot_to="4", #NEEDS TO BE DETERMINED
                strWellName_to=MeasuringWell,
                strOffsetStart_to='center',
                intVolume=Volume,
                limit='1000',
                step_size='1000'),
            MoveToWell(MoveToWellParams(
                labwareLocation=1,
                wellName=pipetteWell,
                speed=100,
                wellLocation=WellLocation(
                    origin="top",
                    offset={"x": 0,
                            "y": 0,
                            "z": 0}
                ))),
            DropTip(DropTipParams(
                labwareLocation="1",
                wellName=pipetteWell,
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
            HomeRobot(HomeRobotParams())
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


class TestWorkflow(BaseWorkflow):
    def __init__(self):
        super().__init__()
        self.operations = [
            PickUpTip(PickUpTipParams(
                labwareLocation="1",
                wellName="A1")),
            Aspirate(AspirateParams(
                labwareLocation="3",
                wellName="A1",
                volume=100,
                flowRate=50)),
            Dispense(DispenseParams(
                labwareLocation="6",
                wellName="A1",
                volume=100,
                flowRate=50)),
            DropTip(DropTipParams(
            labwareLocation="1",
            wellName="A1",
            homeAfter=True))]


class NewFullWorkFlow(BaseWorkflow):
    def __init__(self,
                 # tipRack,
                 # pipette,
                 # strSlot_from,
                 # strWellName_from,
                 # strOffsetStart_from,
                 # strPipetteName,
                 # strSlot_to,
                 # strWellName_to,
                 # strOffsetStart_to,
                 # intVolume,
                 # limit,
                 # ElectrodeTipRack,
                 # step_size,
                 # autodialCell,
                 # strWell2Test_autodialCell,
                 # washstation
                 MeasuringWell,
                 MaterialWell,
                 pipetteWell,
                 Volume,

                 ):
        super().__init__()
        self.operations = [
            HomeRobot(HomeRobotParams()),
            PickUpTip(PickUpTipParams(
                labwareLocation=1,
                wellName=pipetteWell,
                wellLocation=WellLocation(
                    origin="top",
                    offset={"x": 0,
                            "y": 0,
                            "z": 0}))),
            AddPythonCode(
                fill_well_workflow,
                strSlot_from="2", #NEEDS TO BE DETERMINED
                strWellName_from=MaterialWell,
                strOffsetStart_from='bottom',
                strPipetteName=None,
                strSlot_to="4", #NEEDS TO BE DETERMINED
                strWellName_to=MeasuringWell,
                strOffsetStart_to='center',
                intVolume=Volume,
                limit='1000',
                step_size='1000'),
            DropTip(DropTipParams(
                labwareLocation="1",
                wellName=pipetteWell,
                wellLocation=WellLocation(
                    origin="bottom",
                    offset={"x": 0,
                            "y": 1,
                            "z": 0}
                ))),
            PickUpTip(PickUpTipParams(
                labwareLocation=10,
                wellName="A2",
                wellLocation=WellLocation(
                    origin="center",
                    offset={"x": 0.6,
                            "y": 0.5,
                            "z": 0}
                ))),
            MoveToWell(MoveToWellParams(
                labwareLocation=4,
                wellName=MeasuringWell,
                speed=50,
                wellLocation=WellLocation(
                    origin="top",
                    offset={"x": 0.5,
                            "y": 0.5,
                            "z": 5}
                ))),
            MoveToWell(MoveToWellParams(
                labwareLocation=4,
                wellName=MeasuringWell,
                speed=50,
                wellLocation=WellLocation(
                    origin="bottom",
                    offset={"x": 0.5,
                            "y": 0.5,
                            "z": -25}
                ))),
            HomeRobot(HomeRobotParams())
        ]

class WashElectrodeWorkflowNoArduino(BaseWorkflow):
    def __init__(self,
                 labwareLocation,
                 well_name,
                 pipette_id="p300_single_v2.0",
                 ):
        super().__init__()
        self.operations = [
            MoveToWell(MoveToWellParams(
                labwareLocation=labwareLocation,
                wellName=well_name
            )),
            MoveToWell(MoveToWellParams(
                labwareLocation=labwareLocation,
                wellName=well_name,
                wellLocation=WellLocation(
                    origin="bottom",
                    offset={"x": 0,
                            "y": 0,
                            "z": 5}
                ))
            ),
            MoveToWell(MoveToWellParams(
                labwareLocation=labwareLocation,
                wellName=well_name,
                wellLocation=WellLocation(
                    origin="bottom",
                    offset={"x": 0,
                            "y": -3,
                            "z": 5}
                ))
            ),
            MoveToWell(MoveToWellParams(
                labwareLocation=labwareLocation,
                wellName=well_name,
                wellLocation=WellLocation(
                    origin="bottom",
                    offset={"x": 0,
                            "y": 3,
                            "z": 5}
                ))
            ),
            MoveToWell(MoveToWellParams(
                labwareLocation=labwareLocation,
                wellName=well_name,
                wellLocation=WellLocation(
                    origin="bottom",
                    offset={"x": 0,
                            "y": -3,
                            "z": 5}
                ))
            ),
            MoveToWell(MoveToWellParams(
                labwareLocation=labwareLocation,
                wellName=well_name,
                wellLocation=WellLocation(
                    origin="top",
                    offset={"x": 0,
                            "y": 0,
                            "z": 0}
                ))
            )
        ]



class TestWorkflow(BaseWorkflow):
    def __init__(self):
        super().__init__()
        self.operations = [
            HomeRobot(HomeRobotParams()),
            PickUpTip(PickUpTipParams(
                labwareLocation="1",
                wellName="A1")),
            AddPythonCode(
                fill_well_workflow,
                strSlot_from="2",
                strWellName_from="A1",
                strOffsetStart_from='bottom',
                strPipetteName=None,
                strSlot_to="4",
                strWellName_to="B2",
                strOffsetStart_to='center',
                intVolume=1500,
                limit=1000,
                step_size=1000),
            DropTip(DropTipParams(
                labwareLocation="1",
                wellName="A1",
                homeAfter=True)),
            PickUpTip(PickUpTipParams(
                labwareLocation="10",
                wellName="B2",
                wellLocation=WellLocation(
                    origin="top",
                    offset={"x": 0.2,
                            "y": 0,
                            "z": 1}
                ))),
            MoveToWell(MoveToWellParams(
                labwareLocation="4",
                wellName="B2",
                speed=50,
                wellLocation=WellLocation(
                    origin="top",
                    offset={"x": 0,
                            "y": 0,
                            "z": 5}
                ))),
            MoveToWell(MoveToWellParams(
                labwareLocation="4",
                wellName="B2",
                speed=5,
                wellLocation=WellLocation(
                    origin="top",
                    offset={"x": 0,
                            "y": 0,
                            "z": -23}
                ))),
            OCV(OCVParams(
                rest_time_T = 10,
                record_every_dT = 0.5,
                record_every_dE = 10,
                E_range = E_RANGE.E_RANGE_10V,
                bandwidth = BANDWIDTH.BW_5,
            )),
            OCVParams(OCVParams(
                rest_time_T = 12,
                record_every_dT = 0.5,
                record_every_dE = 10,
                E_range = E_RANGE.E_RANGE_10V,
                bandwidth = BANDWIDTH.BW_5,
            )),
            WashElectrodeWorkflowNoArduino(
                labwareLocation="3",
                well_name="A1",
            ),
            WashElectrodeWorkflowNoArduino(
                labwareLocation="6",
                well_name="A1",
            ),
            DropTip(DropTipParams(
                labwareLocation="10",
                wellName="B2",
                homeAfter=True)),
        ]



class TestWorkflow(BaseWorkflow):
    def __init__(self):
        super().__init__()
        self.operations = [
            HomeRobot(HomeRobotParams())
        ]




