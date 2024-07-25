from pydantic import Field

from sdl.Robot.workflow.processes.lib.arduino_utils import ArduinoBaseProcedure


class GetRelayStatus(ArduinoBaseProcedure):
    relay_num: int = Field(..., description="Relay number to get the status of")
    command: str = f"<get_relay_{relay_num}_state>"

    def execute(self, connection):
        connection.write(self.command.encode())
        status = connection.readline().decode()
        return status
