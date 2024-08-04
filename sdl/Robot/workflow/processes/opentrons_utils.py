import functools
import json
import datetime
import opentrons
print(opentrons)

import opentrons.protocol_engine.errors as ot_errors
from opentrons.protocol_engine.errors import ModuleNotLoadedError
import requests
from neomodel import db
from pydantic import BaseModel

from sdl.Robot.workflow.utils import BaseProcedure



def request_with_run_id(f):
    """ get run_id from param """

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if "run_id" not in kwargs:
            raise TypeError("No run_id given. Please pass run_id as a parameter or use ot_api.set_run_id()")
            kwargs["run_id"] = run_id

        try:
            return f(*args, **kwargs)
        except TypeError as e:
            if "run_id" in str(e):
                raise TypeError("Error calling function. Did you not pass run_id as a kwarg?")
            raise e

    return wrapper




class Offset(BaseModel):
    x: float
    y: float
    z: float


class WellLocation(BaseModel):
    origin: str
    offset: Offset


class Location(BaseModel):
    slotName: str


class Vector(BaseModel):
    x: float
    y: float
    z: float


class OpentronsBaseProcedure(BaseProcedure):

    name_space = "opentrons"

    def execute(self, *args, **kwargs):
        """
        Executes a command on the Opentrons robot using a JSON structure.

        Parameters:
        - args: Object or dictionary containing essential parameters.
        - kwargs: Additional parameters that can override those in args.

        Returns:
        - Response data from the Opentrons API.
        """

        # Extract and validate necessary fields from the combined dictionary
        required_kwargs = ['opentrons_ip', 'opentrons_headers', 'opentrons_run_id', 'logger', 'opentrons_port']
        missing_kwargs = [key for key in required_kwargs if key not in kwargs]

        if missing_kwargs:
            missing_keys = ', '.join(missing_kwargs)
            raise ValueError(f"Missing required keyword arguments: {missing_keys}")

        robot_ip = kwargs['opentrons_ip']
        headers = kwargs['opentrons_headers']
        run_id = kwargs['opentrons_run_id']
        logger = kwargs['logger']
        port = kwargs['opentrons_port']
        command_type = self.dict().get('commandType')
        params = self.dict().get('params', {})
        intent = self.dict().get('intent')

        if not command_type:
            raise ValueError("Missing required field 'commandType' in the command data.")

        command_url = f"http://{robot_ip}:{port}/runs/{run_id}/commands"

        command_data = {
            "commandType": command_type,
            "params": params,
            "intent": intent or "setup"
        }
        print(command_data)
        print(command_url)

        command_payload = {
            "data": command_data
        }

        str_command = json.dumps(command_payload)
        logger.info(f"Executing command: {command_type}")

        try:
            response = requests.post(
                url=command_url,
                headers=headers,
                data=str_command,
                params={"waitUntilComplete": True},
            )
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

            response_content = response.json()

            if response_content['data']['status'] == "failed":
                error_message = response_content['data']['error']
                logger.error(f"Failed to execute command.\nError message: {error_message}")
                raise Exception(f"Failed to execute command.\nError message: {error_message}")

            dic_response = response_content['data']
            logger.info(f"Command {command_type} executed successfully.")
            return self.create_cypher_query(dic_response)

        except requests.exceptions.RequestException as e:
            error_message = str(e)
            logger.error(f"HTTP request failed: {error_message}")
            raise Exception(f"HTTP request failed: {error_message}")

        except json.JSONDecodeError as e:
            error_message = str(e)
            logger.error(f"Error decoding JSON response: {error_message}")
            raise Exception(f"Error decoding JSON response: {error_message}")

        except Exception as e:
            error_message = str(e)
            logger.error(f"Unexpected error: {error_message}")
            raise Exception(f"Unexpected error: {error_message}")


    def create_cypher_query(self, data):
        queries = []
        params = {}
        entry = data

        command_type = entry.get('commandType')
        params_prefix = f"entry"

        common_query = f"""
            MERGE (m:Manufacturing {{id: $id}})
            SET m.createdAt = $createdAt,
                m.name = $commandType,
                m.status = $status,
                m.startedAt = $startedAt,
                m.completedAt = $completedAt,
                m.intent = $intent
        """

        pipette_query = ""
        labware_query = ""
        well_query = ""


        params.update({
            f"id": entry.get('id'),
            f"createdAt": entry.get('createdAt'),
            f"commandType": entry.get('commandType'),
            f"status": entry.get('status'),
            f"startedAt": entry.get('startedAt'),
            f"completedAt": entry.get('completedAt'),
            f"intent": entry.get('intent'),
        })

        if 'pipetteId' in entry.get('params', {}):
            pipette_query = f"""
                MERGE (p:Pipette {{id: $pipetteId}})
                MERGE (p)-[:USED_IN]->(m)
            """
            params[f"pipetteId"] = entry['params']['pipetteId']

        if 'labwareId' in entry.get('params', {}) and 'wellName' in entry.get('params', {}) and 'wellLocation' in entry.get('params', {}):
            well_query = f"""
                MERGE (mo:Opentron_Module{{module_id: $labwareId}})
                MERGE(mo)-[:HAS_PART]->(w:Well {{well_id: $wellName}})
                MERGE (m)-[:BY]->(mo)
                MERGE (m)-[:IN]->(w)
            """
            params[f"labwareId"] = entry['params']['labwareId']
            params[f"wellName"] = entry['params']['wellName']
            params[f"wellLocation"] = json.dumps(entry['params']['wellLocation'])

        queries.append(common_query + pipette_query + labware_query + well_query)

        if command_type == 'dispense' or command_type == 'aspirate':
            params[f"flowRate"] = entry['params'].get('flowRate')
            params[f"volume"] = entry['params'].get('volume')
            queries[-1] += f"""
                CREATE (pa:Parameter {{name: "flowRate", value: $flowRate}})
                CREATE (pa1:Parameter {{name: "volume", value: $volume}})
                MERGE (pa)<-[:HAS_PARAMETR]-(m)
                MERGE (pa1)<-[:HAS_PARAMETER]-(m)
                
                SET m.flowRate = $flowRate,
                    m.volume = $volume
            """

        full_query = " ".join(queries)
        db.cypher_query(full_query, params)
        return {"id": entry.get('id'), "response": entry.get('status')}


