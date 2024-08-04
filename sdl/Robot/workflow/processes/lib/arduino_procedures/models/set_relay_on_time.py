from pydantic import Field

from sdl.Robot.workflow.processes.lib.arduino_utils import ArduinoBaseProcedure


class SetRelayOnTime(ArduinoBaseProcedure):
    relay_num: int = Field(..., description="Relay number to set on time for")
    time_on: float = Field(..., description="Time in seconds to turn on the relay")

    def execute(self, connection, *args, **kwargs):
        command = f"<set_relay_on_time,{self.relay_num},{round(float(self.time_on) * 1000, 0)}>"
        logger = kwargs.get("logger")
        logger.info(f"Setting relay {self.relay_num} on for {self.time_on} seconds")
        print("relay_num:",self.relay_num)
        connection.write(command.encode())
        self.wait_for_arduino(connection, **kwargs)
