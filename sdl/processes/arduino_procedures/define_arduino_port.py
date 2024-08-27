import logging

import serial
from pydantic import Field, BaseModel

from sdl.processes.arduino_utils import ArduinoBaseProcedure


class DefineArduinoPortParams(BaseModel):
    search_string: str = Field(..., description="Search string to identify the Arduino port")


class DefineArduinoPort(ArduinoBaseProcedure):
    def __init__(self, params: DefineArduinoPortParams):
        super().__init__(params)

    def execute(self):
        ports = list(serial.tools.list_ports.comports())
        logging.info("List of USB ports:")
        for p in ports:
            logging.info(f"{p}")
        arduino_ports = [p.device for p in ports if self.params.search_string in p.description]
        if not arduino_ports:
            logging.error("No Arduino found")
            raise IOError("No Arduino found")
        if len(arduino_ports) > 1:
            logging.warning("Multiple Arduinos found - using the first")

        # Automatically find Arduino
        arduino = str(serial.Serial(arduino_ports[0]).port)
        logging.info(f"Arduino found on port: {arduino}")
        return arduino