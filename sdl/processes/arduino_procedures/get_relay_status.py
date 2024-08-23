import time

from pydantic import Field, BaseModel

from sdl.processes.arduino_utils import ArduinoBaseProcedure
from sdl.processes.utils import ProcessOutput


class GetRelayStatusParams(BaseModel):
    relay_num: int = Field(..., description="Relay number to get the status of")

class GetRelayStatus(ArduinoBaseProcedure[GetRelayStatusParams]):

    def execute(self, connection):
        command = f"<get_relay_{self.params.relay_num}_state>"
        connection.write(command.encode())
        status = connection.readline().decode().strip()
        return ProcessOutput( input= self.params.dict(), output = {"status": bool(status)})