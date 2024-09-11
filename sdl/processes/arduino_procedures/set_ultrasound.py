from typing import Union

from pydantic import Field, BaseModel

from sdl.processes.arduino_procedures.set_relay_on_time import SetRelayOnTime, SetRelayOnTimeParams
from sdl.processes.arduino_utils import Location, ArduinoBaseProcedure


class SetUltrasoundParams(BaseModel):
    time: float = Field(..., description="Time in seconds to turn on the ultrasound")
    relay_num: int = Field(None, description="Relay number to turn on")
    apply_on: Union[dict, Location] = Field(None, description="Location to apply the ultrasound to")


class SetUltrasoundOn(ArduinoBaseProcedure[SetUltrasoundParams]):

    def execute(self, connection, *args, **kwargs):
        if self.params.relay_num:
            self.params.relay_num = self.params.relay_num
        elif self.params.apply_on:
            self.params.relay_num = self.params.get_relay_from_location(self.params.apply_on)
        set_realay_on = SetRelayOnTime(SetRelayOnTimeParams(relay_num=self.params.relay_num, time_on=self.params.time))
        response = set_realay_on.execute(connection, *args, **kwargs)
        response.output["type"] =  "ultrasound"
        self.store_to_graph(response.id, *args, **kwargs)
        return response

