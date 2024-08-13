from pydantic import Field, BaseModel

from sdl.processes.arduino_procedures.set_relay_on_time import SetRelayOnTime, SetRelayParams
from sdl.processes.arduino_utils import ArduinoBaseProcedure


class DispenseMLParams(BaseModel):
    volume: float = Field(..., description="Volume in ml to be dispensed")
    pump_name: str = Field(None, description="Name of the pump to dispense from")
    from_loc: dict = Field(None, description="Location to dispense from")
    to_loc: dict = Field(None, description="Location to dispense to")
    relay_num: int = Field(None, description="Relay number to dispense from")
    device_type = "pump"

class DispenseMl(ArduinoBaseProcedure[DispenseMLParams]):

    def get_relay_from_pump_name(self):
        if self.params.pump_name:
            for relay in self.config['relays']:
                if relay['name'] == self.params.pump_name:
                    return relay['relay']
                raise ValueError(f"Could not find relay for pump {self.params.pump_name}")

    def get_relay_from_location(self, config):
        for relay in config['relays']:
            inlet = relay['properties'].get('inlet', {})
            outlet = relay['properties'].get('outlet', {})
            inlet_match = self.params.from_loc and inlet.get('device') == self.params.from_loc.get('device') and inlet.get('properties') == self.params.from_loc.get('properties')
            outlet_match = self.params.to_loc and outlet.get('device') == self.params.to_loc.get('device') and outlet.get('properties') == self.params.to_loc.get('properties')
            if inlet_match and outlet_match:
                return relay['relay']
            elif self.params.from_loc and self.params.to_loc is None and inlet_match:
                return relay['relay']
            elif self.to_loc and self.from_loc is None and outlet_match:
                return relay['relay']
        raise ValueError(f"Could not find relay for {self.params.from_loc} to {self.params.to_loc}")

    def get_pump_calibration(self, arduino_config, relay_num):
        print("arduino_config", arduino_config)
        for relay in arduino_config['relays']:
            if relay['relay'] == relay_num:
                return relay['properties']['calibration']['slope'], relay['properties']['calibration']['intercept']
        raise ValueError(f"Could not find calibration for relay {relay_num}")

    def get_pumping_time(self, volume, slope, intercept):
        return slope * volume + intercept


    def execute(self,
                connection,
                from_mat=None,
                to_mat= None,
                *args,
                **kwargs):
        arduino_config = kwargs.get("arduino_config")
        if self.params.relay_num:
            relay_num = self.params.relay_num
        elif self.params.pump_name:
            relay_num = self.get_relay_from_pump_name()
        elif self.params.from_loc or self.params.to_loc:
            relay_num  = self.params.get_relay_from_location(arduino_config)
        pump_slope, intercept = self.params.get_pump_calibration(arduino_config, relay_num)
        time_on = self.params.get_pumping_time(self.params.volume, pump_slope, intercept)

        start_relay = SetRelayOnTime(SetRelayParams(relay_num=relay_num, time_on=time_on, **kwargs))
        start_relay.execute(connection, *args, **kwargs)
