import json
from typing import Dict, Optional

import requests
from pydantic import BaseModel

from sdl.Robot.workflow.utils import BaseProcedure


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

    def execute(self,
                robot_ip: str,
                headers: Dict[str, str],
                run_id: str,
                LOGGER,
                additional_params: Optional[Dict] = None,
                offline: bool = False,

                ):
        """
        Executes a command on the Opentrons robot using a JSON structure.

        Parameters:
        - robot_ip: The IP address of the robot.
        - headers: Headers for the HTTP request.
        - run_id: The ID of the run.
        - command_json: JSON structure containing the command details.
        - additional_params: Additional parameters to override or add to the command.
        - offline: Flag to indicate offline mode (optional).

        Returns:
        - Response data from the Opentrons API.
        """
        # Extract necessary fields from the JSON structure
        command_type = self.dict().get('commandType')
        params = self.dict().get('params', {})
        intent = self.dict().get('intent')


        # Override or add additional parameters if provided
        if additional_params:
            params.update(additional_params)

        command_url = f"http://{robot_ip}:31950/runs/{run_id}/commands"

        dic_command = {
            "data": {
                "commandType": command_type,  # Convert Enum to its value
                "params": params,
                "intent": "setup"
            }
        }

        if intent:
            dic_command["data"]["intent"] = intent

        str_command = json.dumps(dic_command)
        # LOGGER.info(f"Executing command: {command_type}")
        # LOGGER.debug(f"Command: {str_command}")
        print("Executing command: ", command_type)
        print("Command: ", str_command)
        # if offline:
            # LOGGER.info(f"Offline mode: Command {command_type} executed with params: {params}")

        response = requests.post(
            url=command_url,
            headers=headers,
            data=str_command,
            params = {"waitUntilComplete": True},
        )

        # LOGGER.debug(f"Response: {response.text}")

        if response.status_code == 201:
            dic_response = json.loads(response.text)
            # LOGGER.info(f"Command {command_type} executed successfully.")
            print("Response: ", dic_response)
            print(f"Command {command_type} executed successfully.")
            return dic_response
        else:
            raise Exception(f"Failed to execute command.\nError code: {response.status_code}\n Error message: {response.text}")



