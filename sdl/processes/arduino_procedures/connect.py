import time

import serial
from pydantic import Field, BaseModel

from sdl.processes.arduino_utils import ArduinoBaseProcedure

class ConnectParams(BaseModel):
    command: str = "connect"
    port: str = Field(..., description="Port to connect to")
    baud_rate: int = Field(..., description="Baud rate to connect at")
    timeout: int = Field(2000, description="Timeout in milliseconds")

class Connect(ArduinoBaseProcedure):
    def __init__(self, params: ConnectParams):
        super().__init__(params)

    def execute(self):
        connection = serial.Serial(
            port=self.params.port,
            baudrate=self.params.baud_rate,
            timeout=self.params.timeout
        )
        time.sleep(2)
        return connection
