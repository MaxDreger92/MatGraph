from pydantic import Field, BaseModel

from sdl.processes.arduino_utils import ArduinoBaseProcedure
from sdl.processes.utils import ProcessOutput


class SetPumpOnParams(BaseModel):
    pump: int = Field(..., description="Pump number to turn on")
    time: float = Field(..., description="Time in seconds to turn on the pump")
    command: str = f"<set_relay_on_time,{pump},{round(time * 1000, 0)}>"


class SetPumpOn(ArduinoBaseProcedure[SetPumpOnParams]):

    def execute(self, *args, **kwargs):
        self.LOGGER.info(f"Switching relay {self.pump} on for {self.time} seconds")
        self.connection.write(self.command.encode())
        self.wait_for_arduino()
        return ProcessOutput(input=self.params.dict(), output={})
