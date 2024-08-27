from typing import Optional

from pydantic import Field, BaseModel

from sdl.processes.arduino_utils import ArduinoBaseProcedure


class WaitForArduinoParams(BaseModel):
    max_wait_time: Optional[int] = Field(2000, description="Maximum wait time in milliseconds")
    command: str = "wait_for_arduino"


class WaitForArduino(ArduinoBaseProcedure[WaitForArduinoParams]):

    def execute(self, connection, *args, **kwargs):
        self.LOGGER.info(f"Waiting for Arduino to finish executing command")
        self.connection.write(self.params.command.encode())
        self.wait_for_arduino()


