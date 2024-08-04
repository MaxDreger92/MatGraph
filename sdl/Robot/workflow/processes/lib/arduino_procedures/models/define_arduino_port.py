import logging

import serial
from pydantic import Field

from sdl.Robot.workflow.processes.lib.arduino_utils import ArduinoBaseProcedure


class DefineArduinoPort(ArduinoBaseProcedure):
    search_string: str = Field(..., description="Search string to identify the Arduino port")

    def execute(self, search_string: str):
        ports = list(serial.tools.list_ports.comports())
        logging.info("List of USB ports:")
        for p in ports:
            logging.info(f"{p}")
        arduino_ports = [p.device for p in ports if search_string in p.description]
        if not arduino_ports:
            logging.error("No Arduino found")
            raise IOError("No Arduino found")
        if len(arduino_ports) > 1:
            logging.warning("Multiple Arduinos found - using the first")

        # Automatically find Arduino
        arduino = str(serial.Serial(arduino_ports[0]).port)
        logging.info(f"Arduino found on port: {arduino}")
        return arduino