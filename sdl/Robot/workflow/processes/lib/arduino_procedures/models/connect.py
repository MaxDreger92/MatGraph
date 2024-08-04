import time

import serial
from pydantic import Field

from sdl.Robot.workflow.processes.lib.arduino_utils import ArduinoBaseProcedure


class Connect(ArduinoBaseProcedure):
    command: str = "connect"
    port: str = Field(..., description="Port to connect to")
    baud_rate: int = Field(..., description="Baud rate to connect at")
    timeout: int = Field(2000, description="Timeout in milliseconds")

    def execute(self):
        connection = serial.Serial(
            port=self.port,
            baudrate=self.baud_rate,
            timeout=self.timeout
        )
        time.sleep(2)
        return connection
