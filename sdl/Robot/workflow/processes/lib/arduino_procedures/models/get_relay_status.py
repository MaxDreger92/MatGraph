import time

from pydantic import Field

from sdl.Robot.workflow.processes.lib.arduino_utils import ArduinoBaseProcedure


class GetRelayStatus(ArduinoBaseProcedure):
    relay_num: int = Field(..., description="Relay number to get the status of")
    command: str = f"<get_relay_{relay_num}_state>"

    def execute(self, connection):
        command = f"<get_relay_{self.relay_num}_state>"
        connection.write(command.encode())
        status = connection.readline().decode().strip()
        if status == 0 or status == True or status == "True":
            print(f"Status of relay {self.relay_num}: High / On")
            return True
        else:
            print(f"Status of relay {self.relay_num}: Low / Off")
            return False
        return status