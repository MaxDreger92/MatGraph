from pydantic import Field, BaseModel

from sdl.processes.arduino_utils import ArduinoBaseProcedure


class SetRelayOnTimeParams(BaseModel):
    relay_num: int = Field(..., description="Relay number to set on time for")
    time_on: float = Field(..., description="Time in seconds to turn on the relay")


class SetRelayOnTime(ArduinoBaseProcedure[SetRelayOnTimeParams]):

    def execute(self, connection, *args, **kwargs):
        command = f"<set_relay_on_time,{self.params.relay_num},{round(float(self.params.time_on) * 1000, 0)}>"
        logger = kwargs.get("logger")
        logger.info(f"Setting relay {self.params.relay_num} on for {self.params.time_on} seconds")
        print("relay_num:", self.params.relay_num)
        connection.write(command.encode())
        self.wait_for_arduino(connection, **kwargs)
