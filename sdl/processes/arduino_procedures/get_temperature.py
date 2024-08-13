from datetime import time

from pydantic import Field, BaseModel

from sdl.processes.arduino_utils import ArduinoBaseProcedure


class GetTemperatureParams(BaseModel):
    sensor: int = Field(..., description="Sensor number to get the temperature from")
    command: str = f"<read_temp{sensor}>"


class GetTemperature(ArduinoBaseProcedure[GetTemperatureParams]):

    def execute(self, connection):
        connection.write(f"<{self.params.command}{self.params.sensor}>".encode())
        received_response = False
        while received_response is False:
            try:
                temperature = connection.readline().decode()
                temperature = float(temperature)
                received_response = True
            except Exception:
                time.sleep(1)

        return temperature


class GetAmbientTemperatureParams(BaseModel):
    sensor: int = Field(..., description="Sensor number to get the temperature from")
    command: str = f"<read_temp{sensor}>"


class GetAmbientTemperature(ArduinoBaseProcedure[GetAmbientTemperatureParams]):

    def execute(self, connection):
        connection.write(f"<{self.params.command}{self.params.sensor}>".encode())
        received_response = False
        while received_response is False:
            try:
                temperature = connection.readline().decode()
                temperature = float(temperature)
                received_response = True
            except Exception:
                time.sleep(1)

        return temperature
