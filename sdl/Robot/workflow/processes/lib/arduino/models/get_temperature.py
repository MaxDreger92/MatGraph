from datetime import time

from pydantic import Field

from sdl.Robot.workflow.processes.lib.arduino_utils import ArduinoBaseProcedure


class GetTemperature(ArduinoBaseProcedure):
    sensor: int = Field(..., description="Sensor number to get the temperature from")
    command: str = f"<read_temp{sensor}>"

    def execute(self, connection):
        connection.write(f"<{self.command}{self.sensor}>".encode())
        received_response = False
        while received_response is False:
            try:
                temperature = self.connection.readline().decode()
                temperature = float(temperature)
                received_response = True
            except Exception:
                print("Waiting for response...")
                time.sleep(1)

        return temperature

class GetAmbientTemperature(GetTemperature):
    sensor: int = Field(..., description="Sensor number to get the temperature from")
    command: str = f"<read_temp{sensor}_ambient>"

