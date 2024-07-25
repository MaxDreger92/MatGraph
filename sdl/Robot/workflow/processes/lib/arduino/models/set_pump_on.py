from pydantic import Field

from sdl.Robot.workflow.processes.lib.arduino_utils import ArduinoBaseProcedure


class SetPumpOn(ArduinoBaseProcedure):
    pump: int = Field(..., description="Pump number to turn on")
    time: float = Field(..., description="Time in seconds to turn on the pump")
    command: str = f"<set_relay_on_time,{pump},{round(time * 1000, 0)}>"


    def execute(self, *args, **kwargs):
        self.LOGGER.info(f"Switching relay {self.pump} on for {self.time} seconds")
        self.connection.write(self.command.encode())
        self.wait_for_arduino()


