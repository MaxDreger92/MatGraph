from typing import Optional

from pydantic import Field

from sdl.Robot.workflow.processes.lib.arduino_utils import ArduinoBaseProcedure


class WaitForArduino(ArduinoBaseProcedure):
    command: str = "wait_for_arduino"
    max_wait_time: Optional[int] = Field(2000, description="Maximum wait time in milliseconds")

