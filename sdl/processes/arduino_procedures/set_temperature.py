from pydantic import Field, BaseModel

from sdl.processes.arduino_utils import ArduinoBaseProcedure
from sdl.processes.utils import ProcessOutput


class SetTemperatureParams(BaseModel):
    relay_num: int = Field(None, description="Relay number to set temperature for")
    cartridge: str = Field(None, description="Cartridge name")
    temperature: float = Field(..., description="Temperature setpoint in degree Celsius")

class SetTemperature(ArduinoBaseProcedure[SetTemperatureParams]):

    def execute(self, connection, *args, **kwargs):
        temperature  = round(
            self.params.temperature, 1
        ) * 10  # PID only take temperature upto 1 decimal place.
        # The input for PID controllers should be rid of decimals.
        # However the last digit is read as a decimal point.
        if self.params.relay_num:
            relay_num = self.params.relay_num
        connection.write(self.command.decode())
        connection.readline().decode()
        return ProcessOutput(input=self.params.dict(), output={})


