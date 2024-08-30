import time

from openai import BaseModel

from sdl.processes.arduino_utils import ArduinoBaseProcedure


class DisconnectParams(BaseModel):
    command_type: str = "disconnect"

class Disconnect(ArduinoBaseProcedure):
    def __init__(self, params: DisconnectParams):
        super().__init__(params)

    command_type: str = "disconnect"

    def execute(self, connection):
        connection.close()
        time.sleep(31)
        return connection
