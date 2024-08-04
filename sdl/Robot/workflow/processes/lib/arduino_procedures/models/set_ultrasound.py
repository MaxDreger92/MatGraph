from typing import Union

from pydantic import Field

from sdl.Robot.workflow.processes.lib.arduino_procedures.models.set_relay_on_time import SetRelayOnTime
from sdl.Robot.workflow.processes.lib.arduino_utils import ArduinoBaseProcedure, Location


class SetUltrasoundOn(ArduinoBaseProcedure):
    time: float = Field(..., description="Time in seconds to turn on the ultrasound")
    relay_num: int = Field(None, description="Relay number to turn on")
    device_type = "ultrasound"
    apply_on: Union[dict, Location] = Field(None, description="Location to apply the ultrasound to")

    def execute(self, connection, *args, **kwargs):
        time_ms = round(self.time * 1000, 0)
        if self.relay_num:
            relay_num = self.relay_num
        elif self.apply_on:
            relay_num = self.get_relay_from_location(self.apply_on)
        set_realay_on = SetRelayOnTime(relay_num=relay_num, time_on=self.time)
        set_realay_on.execute(connection, *args, **kwargs)

