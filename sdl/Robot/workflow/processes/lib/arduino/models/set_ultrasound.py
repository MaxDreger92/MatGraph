from pydantic import Field

from sdl.Robot.workflow.processes.lib.arduino_utils import ArduinoBaseProcedure


class SetUltrasoundOn(ArduinoBaseProcedure):
    cartridge: int = Field(..., description="Cartridge number to turn on ultrasound for")
    time: float = Field(..., description="Time in seconds to turn on the ultrasound")
    command: str = f"<set_relay_on_time,{cartridge},{time}>"

    def execute(self, connection):
        print("STOP HERE CHECK CORRECTNESS OF RELAYS")
        time_ms = round(self.time * 1000, 0)
        self.connection.write(f"<set_relay_on_time,{self.cartridge},{time_ms}>".encode())
        self.wait_for_arduino()

