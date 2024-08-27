import json
import logging
import os

from dotenv import load_dotenv



# Configure logging early
logging.basicConfig(
    level=logging.INFO,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Set the logging format
    handlers=[
        logging.FileHandler("logfile.log"),  # Log to a file
        logging.StreamHandler()  # Log to console
    ]
)

LOGGER = logging.getLogger(__name__)

def main():
    # LOAD CONFIG FILES
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Change the current working directory to the project root directory
    os.chdir(project_root)

    load_dotenv()

    # Set the environment variable for Django settings
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mat2devplatform.settings")

    # Manually setup Django
    import django
    django.setup()  # Ensure Django is properly set up

    # Now you can import Django models and other components
    from neomodel import config
    from sdl.setup.biologic_setup.BiologicSetup import BiologicSetup
    from sdl.setup.opentrons_setup.OpentronsSetup import OpentronsSetup
    from sdl.experiment.Experiment import ExperimentManager
    from sdl.experiment.Experiment import Experiment
    from sdl.workflow.Workflow import TestWorkflow
    from sdl.setup.arduino_setup.ArduinoSetup import ArduinoSetup

    config_dir = os.path.join(os.getcwd(), 'sdl', 'config')
    config.DATABASE_URL = os.getenv('NEOMODEL_NEO4J_BOLT_URL')









    with open(os.path.join(config_dir, 'opentrons.json'), 'r', encoding='utf-8') as file:
        opentrons_config = json.load(file)

    with open(os.path.join(config_dir, 'arduino.json'), 'r', encoding='utf-8') as file:
        arduino_config = json.load(file)

    with open(os.path.join(config_dir, 'arduino_setup.json'), 'r', encoding='utf-8') as file:
        arduino_setup = json.load(file)

    with open(os.path.join(config_dir, 'biologic_setup.json'), 'r', encoding='utf-8') as file:
        biologic_config = json.load(file)

    with open(os.path.join(config_dir, 'opentron_no_arduino_setup.json'), 'r', encoding='utf-8') as file:
        labware_config = json.load(file)

    with open(os.path.join(config_dir, 'chemicals.json'), 'r', encoding='utf-8') as file:
        chemicals_config = json.load(file)


    # SETUP EXPERIMENTAL SETUP------------------------------------------------------------------------
    opentrons = OpentronsSetup(robot_config_source=opentrons_config,
                               labware_config_source=labware_config,
                               chemicals_config_source = chemicals_config,
                               ip=opentrons_config['ip'],
                               port=opentrons_config['port'],
                               logger=LOGGER)


    biologic = BiologicSetup(config_source=biologic_config, logger=LOGGER)

    arduino = ArduinoSetup(config=arduino_config, relay_config=arduino_setup, logger=LOGGER)

    experiment = Experiment(setups=[opentrons, biologic],
                            workflow=[TestWorkflow()],
                            logger=LOGGER)
    experiment.initialize_setups()
    experiment.store_setups()
    experiment.execute()
    exp_Manager = ExperimentManager(setups = [opentrons, biologic, arduino], logger=LOGGER)
    exp_Manager.find_executable_experiments()


if __name__ == '__main__':
    main()
