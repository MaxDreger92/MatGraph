from pydantic import Field

from sdl.Robot.workflow.processes.lib.arduino_utils import ArduinoBaseProcedure


class SetRelayOnTime(ArduinoBaseProcedure):
    relay_num: int = Field(..., description="Relay number to set on time for")
    time_on: float = Field(..., description="Time in seconds to turn on the relay")
    command: str = f"<set_relay_on_time,{relay_num},{round(time_on * 1000, 0)}>"

    def execute(self, connection):
        connection.write(self.command.encode())
        self.wait_for_arduino()
