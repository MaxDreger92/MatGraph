import logging

from sdl.Robot.experiment.Experiment import Experiment
from sdl.Robot.setup.ExperimentalSetup import OpentronsSetup
from sdl.Robot.workflow.Workflow import FillWellWorkflow
from sdl.Robot.workflow.processes.lib.opentrons.models.drop_tip import DropTip, DropTipParams
from sdl.Robot.workflow.processes.lib.opentrons.models.home_robot import HomeRobot
from sdl.Robot.workflow.processes.lib.opentrons.models.move_to_well import MoveToWell, MoveToWellParams
from sdl.Robot.workflow.processes.lib.opentrons.models.pick_up_tip import PickUpTip, PickUpTipParams
from sdl.Robot.workflow.processes.opentrons_utils import WellLocation


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

    LOGGER.debug("This is a debug message")
    LOGGER.info("This is an info message")
    LOGGER.warning("This is a warning message")
    LOGGER.error("This is an error message")
    LOGGER.critical("This is a critical message")


    # Change the current working directory to the project root directory
    os.chdir(project_root)

    load_dotenv()
    from neomodel import config

    config.DATABASE_URL = os.getenv('NEOMODEL_NEO4J_BOLT_URL')
    print(config.DATABASE_URL)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mat2devplatform.settings")
    config_dir = os.path.join(os.getcwd(), 'Robot', 'config')
    robot_config = json.load(open(os.path.join(config_dir, 'robot.json')))
    labware_config = json.load(open(os.path.join(config_dir, 'test_setup.json')))

    # SETUP EXPERIMENTAL SETUP------------------------------------------------------------------------
    sdl = OpentronsSetup(robot_config_source=robot_config,
                         labware_config_source=labware_config,
                         ip=robot_config['ip'],
                         port=robot_config['port'])

    sdl.setup()

    experiment = Experiment(setups=[sdl],
                            workflow=[HomeRobot(params={}),
                                      MoveToWell(params=MoveToWellParams(
                                          labwareId=sdl.get_labware_id(1),
                                          wellName="A1",
                                          speed=100,
                                          wellLocation=WellLocation(
                                              origin="top",
                                              offset={"x": 0,
                                                      "y": 0,
                                                      "z": 0}
                                          ),
                                          pipetteId=sdl.default_pipette)),
                                      PickUpTip(params=PickUpTipParams(
                                          pipetteId=sdl.default_pipette,
                                          labwareId=sdl.get_labware_id(1),
                                          wellName="A1",
                                          wellLocation=WellLocation(
                                              origin="top",
                                              offset={"x": 0,
                                                      "y": 0,
                                                      "z": 0}))),
                                      FillWellWorkflow(
                                          strSlot_from=sdl.get_labware_id(5),
                                          strWellName_from="A1",
                                          strOffsetStart_from="bottom",
                                          strPipetteName=sdl.default_pipette,
                                          strSlot_to=sdl.get_labware_id(6),
                                          strWellName_to="A1",
                                          strOffsetStart_to="bottom",
                                          intVolume=235
                                      ),
                                      MoveToWell(params=MoveToWellParams(
                                          labwareId=sdl.get_labware_id(1),
                                          pipetteId=sdl.default_pipette,
                                          wellName="A1",
                                          speed=100,
                                          wellLocation=WellLocation(
                                              origin="top",
                                              offset={"x": 0,
                                                      "y": 0,
                                                      "z": 0}
                                          ))),
                                          DropTip(params=DropTipParams(
                                              pipetteId=sdl.default_pipette,
                                              labwareId=sdl.get_labware_id(1),
                                              wellName="A1",
                                              wellLocation=WellLocation(
                                                  origin="top",
                                                  offset={"x": 0,
                                                          "y": 0,
                                                          "z": 0}))),
                                      HomeRobot(params={})
                                      ])
    # experiment.workflow.execute()
    # experiment = Experiment(setups=[sdl],
    #                         workflow=HelloWorldWorkflow())
    # experiment.initialize_setups()
    # experiment.workflow.execute(
    #     robot_ip= experiment.setups['opentrons'].robot_ip,
    #     headers = experiment.setups['opentrons'].headers,
    #     run_id = experiment.setups['opentrons'].runID,
    #     logger = LOGGER,
    #     additional_params = None,
    #
    # )
    # experiment.execute()

    # Setting up an Experiment:

    # 1. Define a SetupClass for each kind of setup you have
    # 2. Define a class for the workflow you are doing
    # 3. Define an Experiment Class with the setups and workflows you want to do
    # 4. Instantiate the experiment
    # 5. Run the experiment

    # Example usage:

if __name__ == '__main__':
    main()
