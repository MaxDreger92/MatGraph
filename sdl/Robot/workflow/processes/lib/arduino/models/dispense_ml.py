from pydantic import Field

from sdl.Robot.workflow.processes.lib.arduino_utils import ArduinoBaseProcedure


class DispenseMl(ArduinoBaseProcedure):
    command: str = "dispense_ml"
    pump: int = Field(..., description="Pump number to dispense from")
    volume: float = Field(..., description="Volume in ml to be dispensed")