import json
import logging
import os
import uuid
from typing import Union

from neomodel import db
from pydantic import ValidationError

from mat2devplatform.settings import BASE_DIR
from sdl.models import Job, WorkflowModel
from sdl.setup.arduino_setup.ArduinoSetup import ArduinoSetup
from sdl.setup.biologic_setup.BiologicSetup import BiologicSetup
from sdl.setup.opentrons_setup.OpentronsSetup import OpentronsSetup
from sdl.workflow.utils import BaseWorkflow, Chemical, SetupModel, Chemicals




class JobRequest:
    def __init__(self, job: Union[json, WorkflowModel, str], job_uid: Union[str, uuid.UUID] = None):
        self.logger = logging.getLogger('app_logger')
        self.logger.info(f"Initializing JobRequest with job: {job}, job_uid: {job_uid}")

        self.job_request = self.parse_job(job)
        self.workflow = self.create_workflow()
        self.requirements = self.workflow.get_requirements()
        self.job_uid = job_uid or uuid.uuid4()
        self.queue_job()

    def parse_job(self, job):
        self.logger.info(f"Parsing job: {job}")
        if isinstance(job, str):
            try:
                return dict(self.get_json_by_filename(job))
            except json.JSONDecodeError as e:
                self.logger.error(f"Error parsing job request: {e}")
                raise ValueError(f"Error parsing job request: {str(e)}")
        elif isinstance(job, WorkflowModel):
            return job.dict()
        elif isinstance(job, dict):
            return job
        else:
            self.logger.error(f"Invalid job request type: {type(job)}")
            raise ValueError(f"Invalid job request type: {type(job)}")

    @staticmethod
    def get_json_by_filename(name):
        directory = os.path.join(BASE_DIR, 'sdl', 'config')
        logging.info(f"Looking for file {name} in directory: {directory}")

        # Walk through the directory and subdirectories to find the file
        for root, dirs, files in os.walk(directory):
            if name in files:
                file_path = os.path.join(root, name)
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read().strip()
                        if not content:
                            logging.error(f"The file {file_path} is empty.")
                            raise ValueError(f"The file {file_path} is empty.")
                        logging.info(f"Successfully loaded file {file_path}")
                        return json.loads(content)
                except PermissionError:
                    logging.error(f"Permission denied when trying to access the file: {file_path}")
                    raise PermissionError(f"Permission denied when trying to access the file: {file_path}")
                except json.JSONDecodeError as e:
                    logging.error(f"Failed to decode JSON from file: {file_path}. Error: {str(e)}")
                    raise ValueError(f"Failed to decode JSON from file: {file_path}. Error: {str(e)}")
                except FileNotFoundError:
                    logging.error(f"File {name} not found in config directory or its subdirectories: {directory}")
                    raise FileNotFoundError(f"File {name} not found in config directory or its subdirectories: {directory}")

    def create_workflow(self):
        self.logger.info(f"Creating workflow from job request: {self.job_request}")
        try:
            return BaseWorkflow.from_config(self.job_request)
        except KeyError as e:
            self.logger.error(f"Invalid workflow configuration: {e}")
            raise ValueError(f"Invalid workflow configuration: {str(e)}")

    def queue_job(self):
        self.logger.info(f"Queueing job with UID: {self.job_uid}")
        requirements = self.parse_requirements()
        model_data = {
            'id': self.job_uid,
            **requirements,
            'workflow': self.job_request
        }
        self.model = Job(**model_data)
        self.model.save()
        self.logger.info(f"Job {self.job_uid} has been saved successfully")

    def parse_requirements(self):
        self.logger.info("Parsing requirements for the workflow")
        try:
            requirements = json.loads(self.requirements.json())
            return {
                'opentrons': requirements.get('opentrons'),
                'opentrons_setup': requirements.get('opentrons_setup'),
                'chemicals': requirements.get('chemicals'),
                'arduino': requirements.get('arduino'),
                'biologic': requirements.get('biologic'),
                'arduino_setup': requirements.get('arduino_setup'),
            }
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing requirements: {e}")
            raise ValueError(f"Error parsing requirements: {str(e)}")


import json
import logging
import os
import uuid
from typing import Union
from neomodel import db
from mat2devplatform.settings import BASE_DIR
from sdl.models import Job
from sdl.setup.arduino_setup.ArduinoSetup import ArduinoSetup
from sdl.setup.biologic_setup.BiologicSetup import BiologicSetup
from sdl.setup.opentrons_setup.OpentronsSetup import OpentronsSetup
from sdl.workflow.utils import BaseWorkflow


class Experiment:
    def __init__(self,
                 opentrons_config: json = None,
                 labware_config: json = None,
                 chemicals_config: json = None,
                 arduino_config: json = None,
                 relay_config: json = None,
                 biologic_config: json = None,
                 workflow: json = None,
                 experiment_id: Union[uuid.UUID, str] = None,
                 store_experiment: bool = True,
                 offset_config: json = None):
        """
        Initialize an experiment with a list of setups and a workflow.
        """
        self.experiment_id = uuid.uuid4() if experiment_id is None else experiment_id


        self.experiment_directory = self.create_experiment_directory()
        self.logger = self.initialize_logger(self.experiment_directory)
        self.logger.info(f"Initializing experiment with ID {self.experiment_id}")

        self.setups = self.create_setups(opentrons_config, labware_config, chemicals_config, arduino_config,
                                         relay_config, biologic_config, offset_config)
        self.workflow = self.create_workflow(workflow)
        self.outputs = []

        self.logger.info("Experiment initialization completed.")

    def initialize_logger(self, log_directory: str):
        """
        Initialize a logger with a custom log directory.
        """
        # Ensure the log directory exists
        if log_directory and not os.path.exists(log_directory):
            os.makedirs(log_directory, exist_ok=True)

        # Create the log file path
        log_file_path = os.path.join(log_directory, f"{self.experiment_id}.log") if log_directory else f"{self.experiment_id}.log"

        # Configure the logger
        logger = logging.getLogger(f'experiment_logger_{self.experiment_id}')
        logger.setLevel(logging.INFO)  # Set the logging level

        # Create handlers: FileHandler for logging to a file, StreamHandler for console output
        file_handler = logging.FileHandler(log_file_path)
        console_handler = logging.StreamHandler()

        # Set logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Avoid duplicating handlers if they already exist
        if not logger.handlers:
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)

        return logger

    def create_workflow(self, workflow):
        self.logger.info("Creating workflow for the experiment.")
        if workflow:
            try:
                return BaseWorkflow.from_config(workflow)
            except KeyError as e:
                self.logger.error(f"Invalid workflow configuration: {str(e)}")
                raise KeyError(f"Invalid workflow configuration: {str(e)}")
        else:
            self.logger.error("No workflow provided for the experiment.")
            raise KeyError("No workflow provided.")

    def create_setups(self, opentrons_config, labware_config, chemicals_config, arduino_config, relay_config,
                      biologic_config, offset_config):
        self.logger.info("Creating setups for the experiment.")
        setups = {}

        if opentrons_config:
            try:
                self.logger.info("Initializing Opentrons setup.")
                opentrons = OpentronsSetup(robot_config_source=opentrons_config,
                                           labware_config_source=labware_config,
                                           chemicals_config_source=chemicals_config,
                                           offset_config=offset_config,
                                           ip=opentrons_config['ip'],
                                           port=opentrons_config['port'],
                                           logger=self.logger)
                setups['opentrons'] = opentrons
                self.logger.info("Opentrons setup initialized.")
            except Exception as e:
                self.logger.error(f"Error initializing Opentrons setup: {str(e)}")
                raise

        if arduino_config:
            try:
                self.logger.info("Initializing Arduino setup.")
                arduino = ArduinoSetup(config=arduino_config, relay_config=relay_config, logger=self.logger)
                setups['arduino'] = arduino
                self.logger.info("Arduino setup initialized.")
            except Exception as e:
                self.logger.error(f"Error initializing Arduino setup: {str(e)}")
                raise

        if biologic_config:
            try:
                self.logger.info("Initializing Biologic setup.")
                biologic = BiologicSetup(config_source=biologic_config, logger=self.logger)
                setups['biologic'] = biologic
                self.logger.info("Biologic setup initialized.")
            except Exception as e:
                self.logger.error(f"Error initializing Biologic setup: {str(e)}")
                raise

        self.logger.info("Setups created successfully.")
        return setups

    def store_experiment(self):
        self.logger.info(f"Storing experiment with ID {self.experiment_id}.")
        required_fields = {
            'id': self.experiment_id,
            'requirements': self.setups['opentrons'].config,
            'workflow': self.workflow.json()
        }

        # Use dictionary comprehension to conditionally add optional fields
        optional_fields = {key: self.setups[key].config for key in ['biologic', 'arduino'] if key in self.setups}

        if 'arduino' in optional_fields:
            optional_fields['arduino_relays'] = self.setups['arduino'].relay_config

        # Merge required fields and optional fields
        model_data = {**required_fields, **optional_fields}

        try:
            self.model = Job(**model_data)
            self.model.save()
            self.logger.info(f"Experiment {self.experiment_id} stored successfully.")
        except Exception as e:
            self.logger.error(f"Error saving the experiment model: {str(e)}")
            raise



    def create_experiment_directory(self):
        experiment_dir = os.path.join(BASE_DIR, str(self.experiment_id))

        try:
            os.makedirs(experiment_dir, exist_ok=True)
        except Exception as e:
            raise
        return experiment_dir

    def update_setups(self, setup):
        self.logger.info(f"Updating setup '{setup.name_space}'")
        self.setups[setup.name_space] = setup

    @property
    def configs(self):
        self.logger.info(f"Fetching configs for experiment {self.experiment_id}.")
        return {setup.name_space: setup.info for setup in self.setups.values()}

    def initialize_setups(self, simulate=False):
        """Initialize all setups."""
        self.logger.info(f"Initializing all setups for experiment {self.experiment_id}.")
        for name, setup in self.setups.items():
            try:
                self.logger.info(f"Initializing setup '{name}'")
                setup.setup(simulate)
                self.update_setups(setup)
            except Exception as e:
                self.logger.error(f"Error initializing setup '{name}': {str(e)}")
                raise
        self.logger.info(f"All setups initialized for experiment {self.experiment_id}.")

    def store_setups(self):
        """Store all setups."""
        self.logger.info(f"Storing all setups for experiment {self.experiment_id}.")
        for name, setup in self.setups.items():
            try:
                self.logger.info(f"Storing setup '{name}'")
                kwargs = self.configs
                setup.save_graph(**kwargs)
            except Exception as e:
                self.logger.error(f"Error storing setup '{name}': {str(e)}")
                raise
        self.logger.info(f"All setups stored for experiment {self.experiment_id}.")

    def execute(self, workflow=None, *args, **kwargs):
        """Execute the experiment workflow."""
        self.logger.info(f"Executing workflow for experiment {self.experiment_id}.")
        try:
            if isinstance(self.workflow, list):
                for sub_workflow in self.workflow:
                    self.logger.info(f"Executing sub-workflow for experiment {self.experiment_id}.")
                    configs = {k: v for config in self.configs.values() for k, v in config.items()}
                    output = sub_workflow.execute(**configs,
                                                  logger=self.logger,
                                                  experiment_id=self.experiment_id,
                                                  opentrons_setup=self.setups['opentrons'],
                                                  opentrons_offset=self.setups['opentrons'].offset_config,
                                                  experiment_directory=self.experiment_directory)
                    self.outputs.extend(output)
            else:
                self.logger.info(f"Executing main workflow for experiment {self.experiment_id}.")
                output = self.workflow.execute(logger=self.logger,
                                               **self.configs,
                                               opentrons_setup=self.setups['opentrons'],
                                               opentrons_offset=self.setups['opentrons'].offset_config,
                                               experiment_id=self.experiment_id,
                                               experiment_directory=self.experiment_directory)
                if not isinstance(output, list):
                    output = [output]
                self.outputs.extend(output)

            self.logger.info(f"Workflow execution completed for experiment {self.experiment_id}.")
        except Exception as e:
            self.logger.error(f"Error during workflow execution: {str(e)}")
            raise

    def find_chemicals(self, chemical_name, opentrons_id):
        self.logger.info(f"Finding chemicals: {chemical_name} for Opentrons ID: {opentrons_id}")
        query = f'''
            MATCH (p:Property)<-[:HAS_PROPERTY]-(c:Matter {{name: '{chemical_name}'}})-[:IN|HAS_METADATA]->(m:Metadata)<-[:HAS_PART*..5]-(o:Opentrons {{setup_id: '{opentrons_id}'}})
            WHERE p.name = 'amount' OR p.name = 'Quantity'
            RETURN c.name, p.value, p.unit'''
        try:
            res, _ = db.cypher_query(query, {})
            self.logger.info(f"Found chemicals: {res}")
            return res
        except Exception as e:
            self.logger.error(f"Error finding chemicals: {str(e)}")
            raise

    def find_labware(self, labware_name, opentrons_id):
        self.logger.info(f"Finding labware: {labware_name} for Opentrons ID: {opentrons_id}")
        query = f'''
            MATCH (l:Labware {{name: '{labware_name}'}})-[:HAS_PART]->(w:Well)-[:HAS_PROPERTY]->(p:Property)
            MATCH (l)-[:HAS_PART]->(o:Opentrons {{setup_id: '{opentrons_id}'}})
            RETURN l.name, w.well_id, p.value, p.unit'''
        try:
            res, _ = db.cypher_query(query, {})
            self.logger.info(f"Found labware: {res}")
            return res
        except Exception as e:
            self.logger.error(f"Error finding labware: {str(e)}")
            raise


class ExperimentManager:
    """
    A class to manage experiments it gets a workflow and setups. Stores the experiment_id with a timestamp and a status in a csv file in the experiment directory.
    the csv file has the following columns:
    experiment_id, timestamp, status

    for each experiment it creates a directory with the experiment_id and stores the setups and the workflow in the folder.
    """

    def __init__(self, opentrons: Union[str, dict], arduino: Union[str, dict], biologic: Union[str, dict],
                 opentrons_setup: Union[str, dict], chemicals: Union[str, dict], arduino_relays: Union[str, dict], offset_config: Union[str, dict]):
        self.logger = logging.getLogger('app_logger')
        self.jobs = Job.objects.all()
        self.opentrons = opentrons if isinstance(opentrons, dict) else self.get_json_by_filename(opentrons)
        self.arduino = arduino if isinstance(arduino, dict) else self.get_json_by_filename(arduino)
        self.biologic = biologic if isinstance(biologic, dict) else self.get_json_by_filename(biologic)
        self.opentrons_setup = opentrons_setup if isinstance(opentrons_setup, dict) else self.get_json_by_filename(
            opentrons_setup)
        self.arduino_setup = arduino_relays if isinstance(arduino_relays, dict) else self.get_json_by_filename(
            arduino_relays)
        self.chemicals = Chemicals.from_config(chemicals) if isinstance(chemicals, dict) else Chemicals.from_config(
            self.get_json_by_filename(chemicals))
        self.chemical_config = chemicals if isinstance(chemicals, dict) else self.get_json_by_filename(chemicals)
        self.offset_config = offset_config if isinstance(offset_config, dict) else self.get_json_by_filename(offset_config)
        self.logger.info("Experiment Manager initialized.")
        self.runnable_experiments = []

    def find_setup_by_namespace(self, setups, namespace):
        for setup in setups:
            if setup.name_space == namespace:
                return setup
        return None

    def find_executable_experiments(self):
        self.setup = SetupModel.from_config(
            chemicals=self.chemicals,
            opentrons_setup=self.opentrons_setup,
            arduino_setup=self.arduino_setup,
            biologic=self.biologic,
            opentrons=self.opentrons,
            arduino=self.arduino
        )
        queued_jobs = Job.objects.filter(
            status="queued",
        )
        for job in queued_jobs:
            if self.check_requirements(job):
                self.runnable_experiments.append(job)
                self.logger.info(f"Job {job.id} is executable.")
            else:
                self.logger.info(f"Job {job.id} not executable.")
        self.logger.info(f'Found {len(self.runnable_experiments)} runnable experiments.')
        for i in self.runnable_experiments:
            self.logger.info(i.workflow)

    def check_requirements(self, job):
        chemical_check =  self.check_chemicals(job)
        setup_check = self.check_required_setup(job)
        return chemical_check and setup_check

    def check_chemicals(self, job):
        """
        Check if the required chemicals are present. Does a direct comparison of
        open
        """
        for chemical in job.chemicals['chemicals']:
            chemical = Chemical(**chemical)
            if not self.chemicals.check_chemical(chemical):
                return False
        return True


    def check_required_setup(self, job):
        """
        Check if the required setups are present. Does a direct comparison of the follwing:
        -opentrons
        -opentrons_setup
        -biologic
        -arduino
        -arduino_relays
        The comparison is done as a simple string comparison.
        """
        if job.opentrons != self.setup.opentrons:
            self.logger.info("Opentrons setup not matching")
            return False
        if job.opentrons_setup != self.setup.opentrons_setup:
            self.logger.info("Opentrons labware setup not matching")
            return False
        if job.biologic != self.setup.biologic:
            self.logger.info("Biologic setup not matching")
            return False
        if job.arduino != self.setup.arduino:
            self.logger.info("Arduino setup not matching")
            return False
        if job.arduino_setup != self.setup.arduino_setup:
            self.logger.info("Arduino relays not matching")
            return False
        return True


    def run_experiments(self):
        for runnable_experiment in self.runnable_experiments:
            experiment = Experiment(
                opentrons_config=self.opentrons,
                arduino_config=self.arduino,
                relay_config=self.arduino_setup,
                biologic_config=self.biologic,
                labware_config=self.opentrons_setup,
                chemicals_config=self.chemical_config,
                workflow=runnable_experiment.workflow,
                experiment_id=runnable_experiment.id,
                offset_config=self.offset_config
            )
            experiment.initialize_setups()
            experiment.store_setups()
            experiment.execute()
            self.logger.info(f"Experiment {experiment.experiment_id} executed successfully.")
            self.update_job_status(experiment.experiment_id, "completed")


    def update_job_status(self, experiment_id, status):
        # Check if the status is valid
        valid_statuses = dict(Job.STATUS_CHOICES).keys()
        if status not in valid_statuses:
            raise ValidationError(f"Invalid status: {status}. Must be one of {valid_statuses}")

        try:
            # Use get() for direct retrieval
            experiment = Job.objects.get(id=experiment_id)
        except Job.DoesNotExist:
            return f"Job with id {experiment_id} does not exist."

        # Update and save the status
        experiment.status = status
        experiment.save()

        return f"Job {experiment_id} status updated to {status}"



    @staticmethod
    def get_json_by_filename(name):
        directory = os.path.join(BASE_DIR, 'sdl', 'config')

        # Walk through the directory and subdirectories to find the file
        for root, dirs, files in os.walk(directory):
            if name in files:
                file_path = os.path.join(root, name)
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read().strip()
                        if not content:
                            raise ValueError(f"The file {file_path} is empty.")
                        return json.loads(content)
                except PermissionError:
                    raise PermissionError(f"Permission denied when trying to access the file: {file_path}")
                except json.JSONDecodeError as e:
                    raise ValueError(f"Failed to decode JSON from file: {file_path}. Error: {str(e)}")
                except FileNotFoundError:
                    raise FileNotFoundError(f"File {name} not found in config directory or its subdirectories: {directory}")
