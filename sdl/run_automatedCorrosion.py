import json
import os

from dotenv import load_dotenv

from mat2devplatform.settings import BASE_DIR
import logging

def main():
    # Configure logging early


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
    from sdl.experiment.Experiment import ExperimentManager, JobRequest
    from sdl.models import WorkflowModel

    config_dir = os.path.join(os.getcwd(), 'sdl', 'config')
    config.DATABASE_URL = os.getenv('NEOMODEL_NEO4J_BOLT_URL')

    with open(os.path.join(config_dir, 'opentrons', 'flex.json'), 'r', encoding='utf-8') as file:
        opentrons_config = json.load(file)

    with open(os.path.join(config_dir, 'arduino', 'arduino.json'), 'r', encoding='utf-8') as file:
        arduino_config = json.load(file)

    with open(os.path.join(config_dir, 'arduino_setup', 'arduino_setup.json'), 'r', encoding='utf-8') as file:
        arduino_setup = json.load(file)

    with open(os.path.join(config_dir, 'biologic', 'biologic_setup.json'), 'r', encoding='utf-8') as file:
        biologic_config = json.load(file)

    with open(os.path.join(config_dir, 'opentrons_setup', 'labware_flex.json'), 'r', encoding='utf-8') as file:
        labware_config = json.load(file)

    with open(os.path.join(config_dir, 'chemicals', 'chemicals.json'), 'r', encoding='utf-8') as file:
        chemicals_config = json.load(file)

    with open(os.path.join(config_dir, 'job_request', 'job.json'), 'r', encoding='utf-8') as file:
        workflow = json.load(file)

    with open(os.path.join(config_dir, 'offset', 'offset.json'), 'r', encoding='utf-8') as file:
        offset_config = json.load(file)


    # SETUP EXPERIMENTAL SETUP------------------------------------------------------------------------

    # opentrons = OpentronsSetup(
    #     robot_config_source=opentrons_config,
    #     labware_config_source=labware_config,
    #     chemicals_config_source=chemicals_config,
    #     LOGGING=LOGGING)
    #
    # arduino = ArduinoSetup(
    #     config=arduino_config,
    #     relay_config=arduino_setup,
    #     LOGGING=LOGGING
    # )
    #
    # biologic = BiologicSetup(
    #     config_source=biologic_config,
    #     LOGGING=LOGGING
    # )

    # experiment = Experiment(
    #     opentrons_config=opentrons_config,
    #     arduino_config=arduino_config,
    #     relay_config=arduino_setup,
    #     biologic_config=biologic_config,
    #     labware_config=labware_config,
    #     chemicals_config=chemicals_config,
    #     workflow = workflow
    # )
    # experiment.initialize_setups()
    # experiment.store_setups()
    # experiment.execute()



    Job = JobRequest(
        job=workflow
    )


    exp_Manager = ExperimentManager(
        opentrons="flex.json",
        arduino="arduino.json",
        biologic="biologic_setup.json",
        opentrons_setup="labware_flex.json",
        chemicals="chemicals.json",
        arduino_relays="arduino_setup.json",
        offset_config="offset.json"
    )
    exp_Manager.find_executable_experiments()
    exp_Manager.run_experiments()


if __name__ == '__main__':
    main()
