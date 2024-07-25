from pydantic import Field

from sdl.Robot.workflow.processes.lib.arduino_utils import ArduinoBaseProcedure


class SetTemperature(ArduinoBaseProcedure):
    cartridge: int = Field(..., description="Cartridge number to set the temperature for")
    temperature: float = Field(..., description="Temperature setpoint in degree Celsius")
    command: str = f"setpoint{cartridge},{temperature}"

    def execute(self, connection):
        connection.write(self.command.decode())
        connection.readline().decode()


