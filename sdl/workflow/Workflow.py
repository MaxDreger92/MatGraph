import time
from datetime import datetime

from biologic import connect
from biologic.techniques.cv import CVTechnique, CVParams, CVStep
from biologic.techniques.ocv import OCVParams, OCVTechnique
from biologic.techniques.peis import PEISTechnique, PEISParams, SweepMode
from kbio.types import BANDWIDTH, E_RANGE, I_RANGE

from sdl.processes.arduino_procedures.dispense_ml import DispenseMl, DispenseMLParams
from sdl.processes.arduino_procedures.set_ultrasound import SetUltrasoundOn, SetUltrasoundParams
from sdl.processes.biologic_utils import BiologicBaseProcedure, BiologicDataHandler
from sdl.processes.opentrons_procedures.aspirate import Aspirate, AspirateParams
from sdl.processes.opentrons_procedures.dispense import Dispense, DispenseParams
from sdl.processes.opentrons_procedures.drop_tip import DropTip, DropTipParams
from sdl.processes.opentrons_procedures.home_robot import HomeRobot, HomeRobotParams
from sdl.processes.opentrons_procedures.move_to_well import MoveToWell, MoveToWellParams
from sdl.processes.opentrons_procedures.pick_up_tip import PickUpTip, PickUpTipParams
from sdl.processes.opentrons_utils import WellLocation
from sdl.workflow.ProcessingStep import AddPythonCode
from sdl.workflow.utils import BaseWorkflow, Chemical, RequirementModel, Chemicals


def fill_well_workflow(
        chemical,
        target_labware,
        target_well,
        volume: int,
        step_size: int = 50,
        limit: int = 50,
        flowrate: int = 50,
        **kwargs
):
    outputs = []
    operation1 = BaseWorkflow(operations=[
        Aspirate(AspirateParams(
            chemical=chemical,
            volume=step_size,
            flowRate=flowrate,
        )),
        Dispense(DispenseParams(
            labwareLocation=target_labware,
            wellName=target_well,
            volume=step_size,
            flowRate=flowrate))])
    while volume > limit:
        output = operation1.execute(**kwargs)
        outputs = [*outputs, *output]

        volume -= step_size
    operation2 = (BaseWorkflow(operations=[
        Aspirate(AspirateParams(
            chemical=chemical,
            volume=volume,
            flowRate=flowrate,
        )),
        Dispense(DispenseParams(
            labwareLocation=target_labware,
            wellName=target_well,
            volume=volume,
            flowRate=flowrate))]))
    output = operation2.execute(**kwargs)
    outputs = [*outputs, *output]
    return outputs


class WashElectrodeWorkflow(BaseWorkflow):
    def __init__(self,
                 labwareName,
                 well_name="A2",
                 ):
        super().__init__()
        self.operations = [
            DispenseMl(DispenseMLParams(
                volume=15,
                relay_num=4
            )),
            MoveToWell(MoveToWellParams(
                labwareName="nis_2_wellplate_30000ul",
                wellName="A2",
                speed=50)
            ),
            MoveToWell(MoveToWellParams(
                labwareName="nis_2_wellplate_30000ul",
                wellName="A2",
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
            DispenseMl(DispenseMLParams(
                volume=16,
                relay_num=3
            )),
            DispenseMl(DispenseMLParams(
                volume=10,
                relay_num=5
            )),
            SetUltrasoundOn(SetUltrasoundParams(
                time=30,
                relay_num=6
            )),
            DispenseMl(DispenseMLParams(
                volume=11,
                relay_num=3
            )),
            DispenseMl(DispenseMLParams(
                volume=15,
                relay_num=4
            )),
            SetUltrasoundOn(SetUltrasoundParams(
                time=30,
                relay_num=6
            )),
            DispenseMl(DispenseMLParams(
                volume=16,
                relay_num=3
            ))]


class BiologicWorkflow(BaseWorkflow, BiologicDataHandler):
    """
    This class is used to define a Biologic workflow it requires self.operations to be a list of BiologicProcedures only
    """

    def __init__(self):
        """
        Ensures that self.operations is a list of BiologicBaseProcedure instances.
        """
        super().__init__()
        self.boolTryToConnect = True
        self.intMaxAttempts = 5

        if not isinstance(self.operations, list):
            raise TypeError("self.operations must be a list")

        if not all(isinstance(operation, BiologicBaseProcedure) for operation in self.operations):
            raise ValueError("All operations must be instances of BiologicBaseProcedure")

    def execute(self, *args, **kwargs):
        self.time_started = datetime.now()
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
                    experiment_directory = kwargs["experiment_directory"]
                    self.time_ended = datetime.now()
                    outputs = self.handle_data(runner, experiment_directory, self.operations, **kwargs)
                    self.boolTryToConnect = False
            except Exception as e:
                logger.error(f"Failed to connect to the Biologic: {e}")
                self.intAttempts_temp += 1
                time.sleep(50)
        return outputs


# class FullWorkFlow(BaseWorkflow):
#     def __init__(self,
#                  MeasuringWell,
#                  MaterialWell,
#                  pipetteWell,
#                  Volume,
#
#                  ):
#         super().__init__()
#         self.operations = [
#             HomeRobot(HomeRobotParams()),
#             MoveToWell(MoveToWellParams(
#                 labwareLocation= 1,
#                 wellName=pipetteWell,
#                 speed=100,
#                 wellLocation=WellLocation(
#                     origin="top",
#                     offset={"x": 0,
#                             "y": 0,
#                             "z": 0}
#                 ))),
#             PickUpTip(PickUpTipParams(
#                 labwareLocation=1,
#                 wellName=pipetteWell,
#                 wellLocation=WellLocation(
#                     origin="top",
#                     offset={"x": 0,
#                             "y": 0,
#                             "z": 0}))),
#             AddPythonCode(
#                 fill_well_workflow,
#                 strSlot_from="2", #NEEDS TO BE DETERMINED
#                 strWellName_from=MaterialWell,
#                 strOffsetStart_from='bottom',
#                 strPipetteName=None,
#                 strSlot_to="4", #NEEDS TO BE DETERMINED
#                 strWellName_to=MeasuringWell,
#                 strOffsetStart_to='center',
#                 intVolume=Volume,
#                 limit='1000',
#                 step_size='1000'),
#             MoveToWell(MoveToWellParams(
#                 labwareLocation=1,
#                 wellName=pipetteWell,
#                 speed=100,
#                 wellLocation=WellLocation(
#                     origin="top",
#                     offset={"x": 0,
#                             "y": 0,
#                             "z": 0}
#                 ))),
#             DropTip(DropTipParams(
#                 labwareLocation="1",
#                 wellName=pipetteWell,
#                 wellLocation=WellLocation(
#                     origin="bottom",
#                     offset={"x": 0,
#                             "y": 1,
#                             "z": 0}
#                 ))),
#             MoveToWell(MoveToWellParams(
#                 labwareId=ElectrodeTipRack,
#                 wellName="A2",
#                 pipetteId=pipette,
#                 speed=100,
#                 wellLocation=WellLocation(
#                     origin="top",
#                     offset={"x": 0.6,
#                             "y": 0.5,
#                             "z": 3}
#                 ))),
#             PickUpTip(PickUpTipParams(
#                 pipetteId=pipette,
#                 labwareId=ElectrodeTipRack,
#                 wellName="A2",
#                 wellLocation=WellLocation(
#                     origin="center",
#                     offset={"x": 0.6,
#                             "y": 0.5,
#                             "z": 0}
#                 ))),
#             MoveToWell(MoveToWellParams(
#                 labwareId=autodialCell,
#                 wellName=strWell2Test_autodialCell,
#                 pipetteId=pipette,
#                 speed=50,
#                 wellLocation=WellLocation(
#                     origin="top",
#                     offset={"x": 0.5,
#                             "y": 0.5,
#                             "z": 5}
#                 ))),
#             MoveToWell(MoveToWellParams(
#                 labwareId=autodialCell,
#                 wellName=strWell2Test_autodialCell,
#                 pipetteId=pipette,
#                 speed=50,
#                 wellLocation=WellLocation(
#                     origin="bottom",
#                     offset={"x": 0.5,
#                             "y": 0.5,
#                             "z": -25}
#                 ))),
#             WashElectrodeWorkflow(
#                 strLabwareName=washstation,
#
#             ),
#             HomeRobot(HomeRobotParams())
#         ]


class RinseElectrodeWorkflow(BaseWorkflow):
    def __init__(self,
                 strLabwareName,
                 well_name="A2",
                 pipette_id="p300_single_v2.0",
                 ):
        super().__init__()
        self.operations = [
            DispenseMl(DispenseMLParams(
                volume=15,
                relay_num=4
            )),
            MoveToWell(MoveToWellParams(
                labwareName="Nis 2 Well Plate 30000 µL",
                wellName="A2",
                speed=50)
            ),
            MoveToWell(MoveToWellParams(
                labwareName="Nis 2 Well Plate 30000 µL",
                wellName="A2",
                speed=50,
                wellLocation=WellLocation(
                    origin="bottom",
                    offset={"x": 0,
                            "y": -15,
                            "z": -7}
                ))
            ),
            SetUltrasoundOn(SetUltrasoundParams(
                time=30,
                relay_num=6
            )),
            DispenseMl(DispenseMLParams(
                volume=16,
                relay_num=3
            )),
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

    def __name__(self):
        return "WashElectrodeWorkflowNoArduino"


# class FullWorkflow(BaseWorkflow):
#     def __init__(self):
#         super().__init__()
#         self.operations = [
#             PickUpTip(PickUpTipParams(
#                 labwareLocation="1",
#                 wellName="A1")),
#             AddPythonCode(
#                 fill_well_workflow,
#                 strSlot_from="2",
#                 strWellName_from="A1",
#                 strOffsetStart_from='bottom',
#                 strPipetteName=None,
#                 strSlot_to="4",
#                 strWellName_to="B2",
#                 strOffsetStart_to='center',
#                 intVolume=1500,
#                 limit=1000,
#                 step_size=1000),
#             DropTip(DropTipParams(
#                 labwareLocation="1",
#                 wellName="A1",
#                 homeAfter=True)),
#             PickUpTip(PickUpTipParams(
#                 labwareLocation="10",
#                 wellName="B2",
#                 wellLocation=WellLocation(
#                     origin="top",
#                     offset={"x": 0.2,
#                             "y": 0,
#                             "z": 1}
#                 ))),
#             MoveToWell(MoveToWellParams(
#                 labwareLocation="4",
#                 wellName="B2",
#                 speed=50,
#                 wellLocation=WellLocation(
#                     origin="top",
#                     offset={"x": 0,
#                             "y": 0,
#                             "z": 5}
#                 ))),
#             MoveToWell(MoveToWellParams(
#                 labwareLocation="4",
#                 wellName="B2",
#                 speed=5,
#                 wellLocation=WellLocation(
#                     origin="top",
#                     offset={"x": 0,
#                             "y": 0,
#                             "z": -23}
#                 ))),
#             OCV(OCVParams(
#                 rest_time_T = 10,
#                 record_every_dT = 0.5,
#                 record_every_dE = 10,
#                 E_range = E_RANGE.E_RANGE_10V,
#                 bandwidth = BANDWIDTH.BW_5,
#             )),
#             OCVParams(OCVParams(
#                 rest_time_T = 12,
#                 record_every_dT = 0.5,
#                 record_every_dE = 10,
#                 E_range = E_RANGE.E_RANGE_10V,
#                 bandwidth = BANDWIDTH.BW_5,
#             )),
#             WashElectrodeWorkflowNoArduino(
#                 labwareLocation="3",
#                 well_name="A1",
#             ),
#             WashElectrodeWorkflowNoArduino(
#                 labwareLocation="6",
#                 well_name="A1",
#             ),
#             DropTip(DropTipParams(
#                 labwareLocation="10",
#                 wellName="B2",
#                 homeAfter=True)),
#         ]
#


class TestWorkflow1(BaseWorkflow):
    def __init__(self, ):
        super().__init__()
        print("printing test variable")
        self.operations = [
            HomeRobot(HomeRobotParams()),

        ]
        self.requirements = RequirementModel(
            chemicals="chemicals.json",
            opentrons_setup="labware_flex.json",
            opentrons="flex.json",
            biologic="biologic_setup.json",
            arduino="arduino.json",
            arduino_setup="arduino_setup.json"
        )


class TestBiologicWorkflow(BiologicWorkflow):
    def __init__(self):
        super().__init__()
        self.operations = [
            OCVTechnique(OCVParams(
                rest_time_T=10,
                record_every_dT=0.5,
                record_every_dE=10,
                E_range=E_RANGE.E_RANGE_10V,
                bandwidth=BANDWIDTH.BW_5,
            )),
            CVTechnique(CVParams(
                average_over_dE=False,
                record_every_dE=0.001,
                n_cycles=40,
                begin_measuring_i=0.5,
                end_measuring_i=1,
                bandwidth=BANDWIDTH.BW_5,
                I_range=I_RANGE.I_RANGE_10mA,
                Ei=CVStep(voltage=0.15,
                          scan_rate=0.05,
                          vs_initial=False),
                E1=CVStep(voltage=1.35,
                          scan_rate=0.05,
                          vs_initial=False),
                E2=CVStep(voltage=-0.25,
                          scan_rate=0.05,
                          vs_initial=False),
                Ef=CVStep(voltage=-0.25,
                          scan_rate=0.05,
                          vs_initial=False)
            )),
            # PEISTechnique(PEISParams(
            #     vs_initial=False,
            #     initial_voltage_step=0,
            #     duration_step=0,
            #     record_every_dT=0.5,
            #     record_every_dI=0.01,
            #     final_frequency=0.1,
            #     initial_frequency=200000,
            #     sweep= SweepMode.Logarithmic,
            #     amplitude_voltage=0.025,
            #     frequency_number=60,
            #     average_n_times=5,
            #     correction=False,
            #     wait_for_steady=0.1,
            #     bandwidth=BANDWIDTH.BW_5,
            #     E_range=E_RANGE.E_RANGE_10V
            # )),
            OCVTechnique(OCVParams(
                rest_time_T=10,
                record_every_dT=0.5,
                record_every_dE=10,
                E_range=E_RANGE.E_RANGE_10V,
                bandwidth=BANDWIDTH.BW_5,
            )),
        ]

        self.requirements = RequirementModel(
            chemicals="chemicals.json",
            opentrons_setup="labware_flex.json",
            opentrons="flex.json",
            biologic="biologic_setup.json",
            arduino="arduino.json",
            arduino_setup="arduino_setup.json"
        )

    def __name__(self):
        return "TestBiologicWorkflow"

class TestBiologicWorkflow1(BiologicWorkflow):
    def __init__(self):
        super().__init__()
        self.operations = [
            # OCVTechnique(OCVParams(
            #     rest_time_T=10,
            #     record_every_dT=0.5,
            #     record_every_dE=10,
            #     E_range=E_RANGE.E_RANGE_10V,
            #     bandwidth=BANDWIDTH.BW_5,
            # )),
            PEISTechnique(PEISParams(
                vs_initial=False,
                initial_voltage_step=0,
                duration_step=0,
                record_every_dT=0.5,
                record_every_dI=0.01,
                final_frequency=0.1,
                initial_frequency=200000,
                sweep= SweepMode.logarithmic,
                amplitude_voltage=0.025,
                frequency_number=60,
                average_n_times=5,
                correction=False,
                wait_for_steady=0.1,
                bandwidth=BANDWIDTH.BW_5,
                E_range=E_RANGE.E_RANGE_10V
            )),
            # OCVTechnique(OCVParams(
            #     rest_time_T=10,
            #     record_every_dT=0.5,
            #     record_every_dE=10,
            #     E_range=E_RANGE.E_RANGE_10V,
            #     bandwidth=BANDWIDTH.BW_5,
            # )),
        ]

        self.requirements = RequirementModel(
            chemicals="chemicals.json",
            opentrons_setup="labware_flex.json",
            opentrons="flex.json",
            biologic="biologic_setup.json",
            arduino="arduino.json",
            arduino_setup="arduino_setup.json"
        )

    def __name__(self):
        return "TestBiologicWorkflow"


class TestWorkflow(BaseWorkflow):
    def __init__(self, chemical, volume):
        super().__init__()
        self.operations = [
            HomeRobot(HomeRobotParams()),
            PickUpTip(PickUpTipParams(
                labwareName="Nis_tall 4 Tip Rack 1 µL",
                wellName="A2",
                speed=80,
                wellLocation=WellLocation(
                    origin="top",
                    offset={"x": 0,
                            "y": 0,
                            "z": 2
                            }
                ))),
            RinseElectrodeWorkflow(
                strLabwareName="Nis 2 Well Plate 30000 µL",
                well_name="A2"),
            MoveToWell(MoveToWellParams(
                labwareName="TLG 1 Reservoir 50000 µL",
                wellName="A1",
                speed=50,
                wellLocation=WellLocation(
                    origin="top",
                    offset={"x": 0,
                            "y": 0,
                            "z": 0}
                ))),
            MoveToWell(MoveToWellParams(
                labwareName="TLG 1 Reservoir 50000 µL",
                wellName="A1",
                speed=50,
                wellLocation=WellLocation(
                    origin="bottom",
                    offset={"x": 0,
                            "y": 0,
                            "z": 2}
                ))),
            TestBiologicWorkflow(),
            MoveToWell(MoveToWellParams(
                labwareName="TLG 1 Reservoir 50000 µL",
                wellName="A1",
                speed=50,
                wellLocation=WellLocation(
                    origin="top",
                    offset={"x": 0,
                            "y": 0,
                            "z": 2}
                ))),
            RinseElectrodeWorkflow(
                strLabwareName="Nis 2 Well Plate 30000 µL",
                well_name="A2"),
            MoveToWell(MoveToWellParams(
                labwareName="Nis_tall 4 Tip Rack 1 µL",
                wellName="A2",
                speed=50,
                wellLocation=WellLocation(
                    origin="top",
                    offset={"x": 0,
                            "y": 0,
                            "z": 0}
                ))),
            DropTip(DropTipParams(
                labwareName="Nis_tall 4 Tip Rack 1 µL",
                wellName="A2",
                wellLocation=WellLocation(
                    origin="bottom",
                    offset={"x": 0,
                            "y": 0,
                            "z": 2}
                ),
                homeAfter=True)
            ),
        ]

        self.requirements = RequirementModel(
            chemicals=Chemicals(chemicals=[Chemical(name=chemical, volume=volume, unit="ul")]),
            opentrons_setup="opentrons_setup_small.json",
            opentrons="ot2.json",
            biologic="biologic_setup.json",
            arduino="arduino.json",
            arduino_setup="arduino_setup.json"
        )
