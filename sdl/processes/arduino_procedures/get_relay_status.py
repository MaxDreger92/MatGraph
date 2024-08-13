import time

from pydantic import Field, BaseModel

from sdl.processes.arduino_utils import ArduinoBaseProcedure


class GetRelayStatusParams(BaseModel):
    relay_num: int = Field(..., description="Relay number to get the status of")

class GetRelayStatus(ArduinoBaseProcedure[GetRelayStatusParams]):

    def execute(self, connection):
        command = f"<get_relay_{self.params.relay_num}_state>"
        connection.write(command.encode())
        status = connection.readline().decode().strip()
        if status == 0 or status == True or status == "True":
            print(f"Status of relay {self.params.relay_num}: High / On")
            return True
        else:
            print(f"Status of relay {self.params.relay_num}: Low / Off")
            return False
        return status