from pydantic import Field

from sdl.Robot.workflow.processes.lib.arduino_utils import ArduinoBaseProcedure


class SetTemperature(ArduinoBaseProcedure):
    relay_num: int = Field(None, description="Relay number to set temperature for")
    cartridge: str = Field(None, description="Cartridge name")
    temperature: float = Field(..., description="Temperature setpoint in degree Celsius")

    def execute(self, connection, *args, **kwargs):
        temperature  = round(
            self.temperature, 1
        ) * 10  # PID only take temperature upto 1 decimal place.
        # The input for PID controllers should be rid of decimals.
        # However the last digit is read as a decimal point.
        if self.relay_num:
            relay_num = self.relay_num
        print("Logger", self.logger)
        connection.write(self.command.decode())
        connection.readline().decode()


