import logging

from sdl.Robot.experiment.Experiment import Experiment
from sdl.Robot.setup.arduino_setup.ArduinoSetup import ArduinoSetup
from sdl.Robot.setup.opentrons_setup.OpentronsSetup import OpentronsSetup
from sdl.Robot.workflow.ProcessingStep import AddPythonCode
from sdl.Robot.workflow.Workflow import fill_well_workflow, ResetWorkflow, GoHomeWorkflow, HelloWorldWorkflow
from sdl.Robot.workflow.processes.lib.arduino_procedures.models.dispense_ml import DispenseMl
from sdl.Robot.workflow.processes.lib.arduino_procedures.models.get_relay_status import GetRelayStatus
from sdl.Robot.workflow.processes.lib.arduino_procedures.models.set_relay_on_time import SetRelayOnTime
from sdl.Robot.workflow.processes.lib.arduino_procedures.models.set_ultrasound import SetUltrasoundOn
from sdl.Robot.workflow.processes.lib.opentrons_procedures.models.home_robot import HomeRobot


def main():
    import os
    from dotenv import load_dotenv
    import json

    # LOAD CONFIG FILES--------------------------------------------------------------------------------
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Create and configure the logger
    logging.basicConfig(
        level=logging.INFO,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Set the logging format
        handlers=[
            logging.FileHandler("logfile.log"),  # Log to a file
            logging.StreamHandler()  # Log to console
        ]
    )

    LOGGER = logging.getLogger(__name__)

    # Change the current working directory to the project root directory
    os.chdir(project_root)

    load_dotenv()
    from neomodel import config

    config.DATABASE_URL = os.getenv('NEOMODEL_NEO4J_BOLT_URL')
    print(config.DATABASE_URL)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mat2devplatform.settings")
    config_dir = os.path.join(os.getcwd(), 'Robot', 'config')
    robot_config = json.load(open(os.path.join(config_dir, 'robot.json')))
    labware_config = json.load(open(os.path.join(config_dir, 'opentron_setup.json')))
    arduino_config = json.load(open(os.path.join(config_dir, 'arduino.json')))
    arduino_setup = json.load(open(os.path.join(config_dir, 'arduino_setup1.json')))

    # SETUP EXPERIMENTAL SETUP------------------------------------------------------------------------
    opentrons = OpentronsSetup(robot_config_source=robot_config,
                         labware_config_source=labware_config,
                         ip=robot_config['ip'],
                         port=robot_config['port'],
                         logger=LOGGER)


    arduino = ArduinoSetup(config=arduino_config,
                           relay_config=arduino_setup,
                         logger=LOGGER)

    #
    # test = SetRelayOnTime(relay_num=3, time_on=5)
    #
    #
    #
    # print("connection",arduino.connection)
    #
    # print("relay:",test.execute(connection=arduino.connection))




    experiment = Experiment(setups=[opentrons, arduino],
                            workflow=[
                                # ResetWorkflow(pipette_location=opentrons.get_labware_id(1),
                                #                     pipette_id=opentrons.default_pipette),
                                #       AddPythonCode(fill_well_workflow,strSlot_from = opentrons.get_labware_id(5),
                                #                                        strWellName_from = "A1",
                                #                                        strOffsetStart_from = 'bottom',
                                #                                        strPipetteName = opentrons.default_pipette,
                                #                                        strSlot_to = opentrons.get_labware_id(6),
                                #                                        strWellName_to = "A1",
                                #                                        strOffsetStart_to = 'bottom',
                                #                                        intVolume = 75,
                                #                                         limit = 50,
                                #                                         step_size = 50,    ),
                                #       GoHomeWorkflow(
                                #           pipette_location=opentrons.get_labware_id(1),
                                #           pipette_id=opentrons.default_pipette
                                #       )
                                HomeRobot(params ={})
                                      ],
                            logger=LOGGER)
    # experiment = Experiment(setups=[opentrons, arduino],
    #                         workflow=HelloWorldWorkflow(),
    #                         logger=LOGGER)
    experiment.initialize_setups()
    experiment.store_setups()
    experiment.execute()


# dispense = DispenseMl(
    #     volume=10,
    #     from_loc={
    #         "device": "opentrons",
    #         "properties": {
    #             "slot": 6,
    #             "well": "A1"
    #         }
    #     },
    #     to_loc={
    #         "device": "opentrons",
    #         "properties": {
    #             "slot": 6,
    #             "well": "A1"
    #         }
    #     }
    # )
    # dispense.execute(connection=arduino.connection, arduino_config=arduino.setup_config, amount=50, logger=LOGGER)
    # apply_ultrasound = SetUltrasoundOn(
    #     time = 5,
    #     relay_num = 6
    #
    # )
    # apply_ultrasound.execute(connection=arduino.connection, arduino_config=arduino.setup_config, logger=LOGGER)

    # experiment.workflow.execute(
    #     robot_ip= experiment.setups['opentrons'].robot_ip,
    #     headers = experiment.setups['opentrons'].headers,
    #     run_id = experiment.setups['opentrons'].runID,
    #     logger = LOGGER,
    #     additional_params = None,

    # experiment.execute()

    # Setting up an Experiment:

    # 1. Define a SetupClass for each kind of setup you have
    # 2. Define a class for the workflow you are doing
    # 3. Define an Experiment Class with the setups and workflows you want to do
    # 4. Instantiate the experiment
    # 5. Run the experiment
    # experiment.to_graph()
    # Example usage:


if __name__ == '__main__':
    main()
