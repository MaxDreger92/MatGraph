import logging
import time
import serial
import serial.tools.list_ports

LOGGER = logging.getLogger(__name__)


class Arduino:
    """Class for the arduino robot relate activities for the openTron setup."""

    def __init__(
        self,
        arduino_search_string: str = "CH340",
        list_of_cartridges: list = [0, 1],
        list_of_pump_relays: list = [0, 1, 2, 3, 4, 5],
        list_of_ultrasonic_relays: list = [6, 7],
        pump_slope: dict = {0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0},
        pump_intercept: dict = {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0},
    ):
        """Initialize the arduino robotic parts. The robot consist of
        cartridges that are inserted into the openTron robot. Each cartridge
        has a temperature sensor, heating elements that are PID controlled
        through a setpoint and an ultrasonic transducer.
        Pumps and ultrasonic drivers that are all connected to relays.

        The robot assumes that cartridges are numbered from 0 and up.
        The robot assumes that relays are used both for pumps and ultrasonic
        sensors.
        The robot assumes that cartridge 0 is connected to the first ultrasound
        relay and so on; eg. cartridge 0 is connected to ultrasonic relay 6,
        while cartridge 1 is connected to ultrasonic relay 7.

        The pump calibration is done by a linear calibration, by the following
        equation: volume = pump_slope * relay_time_on + pump_intercept
        It can be measured by running the pump while measuring the weight
        dispensed, at eg. 0.5 seconds, 1 seconds, 2 seconds, 5 seconds,
        10 seconds, 20 seconds.

        Args:
            arduino_search_string (str, optional): _description_. Defaults to
                "CH340".
            list_of_cartridges (list, optional): List of cartridge numbers.
                Defaults to [0, 1].
            list_of_pump_relays (list, optional): List of pump relay numbers.
                Must correspond with wirering.  Defaults to [0, 1, 2, 3, 4, 5].
            list_of_ultrasonic_relays (list, optional): List of ultrasonic
                relay numbers. Must correspond with wirering.
                Defaults to [6, 7].
            pump_slope (dict, optional): Dictionary with pump number as key and
                slope as value.
                Defaults to {0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0}.
            pump_intercept (dict, optional): Dictionary with pump number as
                key and intercept as value.
                Defaults to {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0}.
        """
        self.SERIAL_PORT = self.define_arduino_port(arduino_search_string)
        self.BAUD_RATE = 115200
        self.CONNECTION_TIMEOUT = 30  # seconds
        self.list_of_cartridges = list_of_cartridges
        self.list_of_pump_relays = list_of_pump_relays
        self.list_of_ultrasonic_relays = list_of_ultrasonic_relays
        self.pump_slope = pump_slope
        self.pump_intercept = pump_intercept
        self._check_pump_coefficients()
        self._check_catridges_vs_ultrasonic()
        self._check_ultrasound_pump_relays_dont_overlap()
        self.connect()

    def connect(
        self,
    ) -> None:
        """Connects to serial port of arduino"""
        # Connection to arduino
        self.connection = serial.Serial(
            port=self.SERIAL_PORT,
            baudrate=self.BAUD_RATE,
            timeout=self.CONNECTION_TIMEOUT,
        )
        time.sleep(2)  # initialization loadtime needs to be > 2 seconds

    def disconnect(self) -> None:
        """Disconnects from serial port of arduino"""
        self.connection.close()
        time.sleep(31)

    def get_temperature0(self) -> float:
        """Measure the temeprature of the temperature sensor 0

        Returns:
            float: The measured temperature of the system in degree celsius.
        """
        LOGGER.info("Reading sample temperature sensor 0")
        self.connection.write("<read_temp0>".encode())
        temperature = self._read_temperature()
        return temperature

    def get_temperature0_ambient(self) -> float:
        """Measure the ambient temperature of the temperature sensor 0

        Returns:
            float: The measured temperature of the system in degree celsius.
        """

        LOGGER.info("Reading ambient temperature sensor 0")
        self.connection.write("<read_temp0_ambient>".encode())
        temperature = self._read_temperature()
        return temperature

    def get_temperature1(self) -> float:
        """Measure the temeprature of the temperature sensor 1

        Returns:
            float: The measured temperature of the system in degree celsius.
        """

        LOGGER.info("Reading sample temperature sensor 1")
        self.connection.write("<read_temp1>".encode())
        temperature = self._read_temperature()
        return temperature

    def get_temperature1_ambient(self) -> float:
        """Measure the ambient temperature of the temperature sensor 1

        Returns:
            float: The measured temperature of the system in degree celsius.
        """

        LOGGER.info("Reading ambient temperature sensor 1")
        self.connection.write("<read_temp1_ambient>".encode())
        temperature = self._read_temperature()
        return temperature

    def _read_temperature(self):
        """Read the temperature from the arduino.

        Returns:
            float: The measured temperature of the system in degree celsius.
        """

        received_response = False
        while received_response is False:
            try:
                temperature = self.connection.readline().decode()
                LOGGER.debug(f"Returned raw temperature: {temperature}")
                temperature = float(temperature)
                received_response = True
            except Exception:
                LOGGER.info("Waiting for arduino to respond")
                time.sleep(1)

        LOGGER.info(f"Temperature sensor: {temperature} C")
        return temperature

    def set_temperature(self, cartridge: int, temperature: float) -> None:
        """Set the temperature setpoint for a specific cartridge for the PID
        controller.

        Args:
            cartridge (int): Cartridge number
            temperature (float): Setpoint of the temperature in degree celsius.
        """
        temperature = round(
            temperature, 1
        )  # PID only take temperature upto 1 decimal place.
        # The input for PID controllers should be rid of decimals.
        # However the last digit is read as a decimal point.

        temp = temperature * 10

        self.connection.write(f"<setpoint{cartridge},{temp}>".encode())
        self.connection.readline().decode()
        LOGGER.info(f"Set temperature to {temperature} C")

    def _check_number_of_cartridges(self, cartridge: int) -> None:
        """Check if the cartridge number is within the range.

        Args:
            cartridge (int): Cartridge number
        """
        if cartridge not in self.list_of_cartridges:
            raise ValueError(
                f"Cartridge number {cartridge} is out of range. "
                f"Available cartridges: {self.list_of_cartridges}"
            )

    def _check_pump_number(self, pump: int) -> None:
        """Check if the pump number is within the range.

        Args:
            pump (int): Pump number
        """
        if pump not in self.list_of_pump_relays:
            raise ValueError(
                f"Pump number {pump} is out of range. "
                f"Available pumps: {self.list_of_pump_relays}"
            )

    def _check_ultrasonic_number(self, ultrasonic: int) -> None:
        """Check if the ultrasonic number is within the range.

        Args:
            ultrasonic (int): Ultrasonic number
        """
        if ultrasonic not in self.list_of_ultrasonic_relays:
            raise ValueError(
                f"Ultrasonic number {ultrasonic} is out of range. "
                f"Available ultrasonics: {self.list_of_ultrasonic_relays}"
            )

    def _check_catridges_vs_ultrasonic(self) -> None:
        """Check if the number of cartridges and ultrasonics match."""
        if len(self.list_of_cartridges) != len(self.list_of_ultrasonic_relays):
            raise ValueError("Number of cartridges and ultrasonics should be same.")

    def _check_ultrasound_pump_relays_dont_overlap(self) -> None:
        """Check if the ultrasonic and pump relays don't overlap."""
        if any(
            relay in self.list_of_ultrasonic_relays
            for relay in self.list_of_pump_relays
        ):
            raise ValueError("Ultrasonic and pump relays should not overlap.")

    def _check_pump_coefficients(self) -> None:
        """Check if the pump coefficients are valid."""
        # Check that the length of the coefficients match the number of pumps
        if len(self.pump_slope) != len(self.list_of_pump_relays) or len(
            self.pump_intercept
        ) != len(self.list_of_pump_relays):
            raise ValueError("Number of pumps and coefficients should be same.")

        # Check that the index (pump number) are integers
        if not all(isinstance(pump, int) for pump in self.pump_slope.keys()):
            raise ValueError("Pump numbers should be integers.")

        # Check that self.pumps_slope values are all floats
        if not all(isinstance(slope, float) for slope in self.pump_slope.values()):
            raise ValueError("Pump slopes should be floats.")

        # Check that self.pumps_intercept values are all floats
        if not all(
            isinstance(intercept, float) for intercept in self.pump_intercept.values()
        ):
            raise ValueError("Pump intercepts should be floats.")

    def set_ultrasound_on(self, cartridge: int, time: float):
        """Turns on the ultrasound for the given time.

        Args:
            cartridge (int): Cartridge number
            time (float): Time in seconds which ultrasound should turned on.
        """
        self._check_number_of_cartridges(cartridge)

        # Find the index number of the cartridge
        cartridge_index = self.list_of_cartridges.index(cartridge)
        ultrasound_relay = self.list_of_ultrasonic_relays[cartridge_index]

        LOGGER.info(
            f"Turning on ultrasound for {time} seconds on cartridge {cartridge}."
        )

        self.set_relay_on_time(ultrasound_relay, time)

    def set_pump_on(self, pump: int, time: float):
        """Turns on the pump for the given time.

        Args:
            pump (int): Pump number
            time (float): Time in seconds which pump should turned on.
        """
        self._check_pump_number(pump)

        LOGGER.info(f"Turning on pump {pump} for {time} seconds.")

        self.set_relay_on_time(pump, time)

    def dispense_ml(self, pump: int, volume: float):
        """Dispense the given volume in ml.

        Args:
            pump (int): Pump number
            volume (float): Volume in ml to be dispensed.
        """
        self._check_pump_number(pump)

        # Calculate the time to turn on the pump
        time_on = self.pump_slope[pump] * volume + self.pump_intercept[pump]

        LOGGER.info(f"Dispensing {volume} ml from pump {pump}.")

        self.set_pump_on(pump, time_on)

    def wait_for_arduino(self, max_wait_time: int = 2000):
        """To make sure arduino completed the particular task.

        Args:
            max_wait_time (int, optional): Maximum wait time to get response
            from arduino in seconds. Defaults to 2000.

        Raises:
            RuntimeWarning: Arduino did not finish the job in given time.
        """
        max_try = (1 / self.CONNECTION_TIMEOUT) * max_wait_time
        count = 0
        while count < max_try:
            LOGGER.debug("waiting for arduino to finish the task")
            state = self.connection.read().decode()
            if state == "#":
                LOGGER.debug("Arduino finished the task")
                break
            count += 1
        else:
            raise RuntimeWarning(
                "Arduino did not finish the job.",
                "Check arduino IDE or increase the value of max_wait_time.",
            )

    def define_arduino_port(self, search_string: str) -> str:
        """Find the port of the Arduino.

        Args:
            search_string (str, optional): Name of the Arduino.

        Returns:
            str: Port of the Arduino.
        """

        # List Arduinos on computer
        ports = list(serial.tools.list_ports.comports())
        logging.info("List of USB ports:")
        for p in ports:
            logging.info(f"{p}")
        arduino_ports = [p.device for p in ports if search_string in p.description]
        if not arduino_ports:
            logging.error("No Arduino found")
            raise IOError("No Arduino found")
        if len(arduino_ports) > 1:
            logging.warning("Multiple Arduinos found - using the first")

        # Automatically find Arduino
        arduino = str(serial.Serial(arduino_ports[0]).port)
        logging.info(f"Arduino found on port: {arduino}")
        return arduino

    def set_relay_on_time(self, relay_num: int, time_on: float) -> None:
        """Turn on the relay for the given time.

        Args:
            relay_num (int): Number of the relay.
            time_on (float): Time in seconds which relay should turned on.
        """
        LOGGER.info(f"Switching relay {relay_num} on for {time_on} seconds")
        time_ms = round(time_on * 1000, 0)
        self.connection.write(f"<set_relay_on_time,{relay_num},{time_ms}>".encode())
        self.wait_for_arduino()

    def get_relay_status(self, relay_num: int) -> bool:
        """Get the status of the relay.

        Args:
            relay_num (int): Number of the relay.

        Returns:
            bool: Status of the relay.
        """

        LOGGER.info(f"Getting status of relay {relay_num}")
        self.connection.write(f"<get_relay_{relay_num}_state>".encode())
        status = self.connection.readline().decode()
        if status == "True":
            LOGGER.info(f"Status of relay {relay_num}: High / On")
            return True
        else:
            LOGGER.info(f"Status of relay {relay_num}: Low / Off")
            return False
