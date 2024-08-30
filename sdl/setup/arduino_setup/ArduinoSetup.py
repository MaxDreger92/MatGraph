import time

import serial
import serial.tools.list_ports
from serial.tools import list_ports

from sdl.models import ArduinoBoard
from sdl.setup.ExperimentalSetup import BaseSetup
from sdl.setup.arduino_setup.PIDs import PIDController
from sdl.setup.arduino_setup.Relays import PumpRelay, UltrasonicRelay


class ArduinoSetup(BaseSetup):
    def __init__(self, config, relay_config, logger, model=ArduinoBoard, *args, **kwargs):
        """
        Initialize the Arduino setup with configuration source and model.

        Args:
            model (Model): Django model for database operations.
        """
        super().__init__(config_source = config, db_model= ArduinoSetup)
        # self.logger = logger
        self.relay_config = relay_config
        self.relays = []
        self.pids = []
        self.init_relays(relay_config['relays'])
        self.init_pids(relay_config['pids'])
        self.logger = logger
        self.simulate = False

        self.arduino_search_string = config.get("arduino_search_string")
        self.ip = None
        self.name_space = "arduino"  # Important for mapping to procedures
        self.BAUD_RATE = 115200
        self.CONNECTION_TIMEOUT = 30  # seconds


    @property
    def info(self):
        return {
            "name_space": self.name_space,
            "arduino_config": self.config,
            "relays": self.relays,
            "pids": self.pids,
            "ip": self.ip,
            "SERIAL_PORT": self.SERIAL_PORT,
            "BAUD_RATE": self.BAUD_RATE,
            "CONNECTION_TIMEOUT": self.CONNECTION_TIMEOUT,
        }

    def connect(self, simulate = True) -> None:
        """Connects to the serial port of the Arduino and verifies the connection."""
        if simulate:
            self.logger.warning("Simulating connection to Arduino.")
            self.SERIAL_PORT = "SimulatedPort"
            return
        self.SERIAL_PORT = self.define_arduino_port(self.arduino_search_string)
        try:
            self.logger.info(f"Attempting to connect to {self.SERIAL_PORT} at {self.BAUD_RATE} baud.")
            self.connection = serial.Serial(
                port=self.SERIAL_PORT,
                baudrate=self.BAUD_RATE,
                timeout=self.CONNECTION_TIMEOUT,
            )
            time.sleep(2)  # initialization load time needs to be > 2 seconds

            if self.connection.is_open:
                self.logger.info(f"Successfully connected to {self.SERIAL_PORT}.")
            else:
                self.logger.error(f"Failed to connect to {self.SERIAL_PORT}.")
                raise IOError(f"Failed to connect to {self.SERIAL_PORT}.")

        except serial.SerialException as e:
            if self.simulate:
                self.logger.warning(f"Simulating connection to {self.SERIAL_PORT}.")
                return
            self.logger.error(f"SerialException: {e}")
            raise e
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise e


    def define_arduino_port(self, search_string: str) -> str:
        """Find the port of the Arduino.

        Args:
            search_string (str, optional): Name of the Arduino.

        Returns:
            str: Port of the Arduino.
        """

        # List Arduinos on computer
        ports = list(list_ports.comports())
        self.logger.info("List of USB ports:")
        for p in ports:
            self.logger.info(f"{p}")

        arduino_ports = [p.device for p in ports if search_string in p.description]
        if not arduino_ports:
            self.logger.error("No Arduino found")
            if self.simulate:
                self.logger.warning("Simulating connection to Arduino.")
                return "COM3"
            raise IOError("No Arduino found")
        if len(arduino_ports) > 1:
            self.logger.warning("Multiple Arduinos found - using the first")

        # Automatically find Arduino
        arduino = str(serial.Serial(arduino_ports[0]).port)
        self.logger.info(f"Arduino found on port: {arduino}")
        return arduino

    def save_graph(self, **kwargs):
        arduino = ArduinoBoard(
            baud_rate=self.BAUD_RATE,
            port=self.SERIAL_PORT

        )
        arduino.save()
        for relay in self.relays:
            relay.save(**kwargs)
            arduino.relay.connect(relay.relay_node)
        for pid in self.pids:
            pid.save()
            arduino.pid.connect(pid.pid_node)
        pass


    def setup(self, simulate=False):
        """
        Load configuration, validate it, initialize the Arduino, and save the setup ID.
        """
        self.simulate = simulate
        self.load_config()
        self.validate_config()
        print(self.config)
        print("relays", self.relays)

        self.initialize_arduino()

    def initialize_arduino(self):
        """
        Initialize the Arduino based on the configuration.
        """
        self.connect()
        self.logger.info("Arduino connected")
        self.logger.info("Initializing relays")


    def init_relays(self, relay_configs: list):
        for config in relay_configs:
            if config["device"] == "pump":
                relay = PumpRelay(
                    relay_num=config["relay"],
                    name=config["name"],
                    properties=config["properties"]
                )
            elif config["device"] == "ultrasonic":
                relay = UltrasonicRelay(
                    relay_num=config["relay"],
                    name=config["name"],
                    properties=config["properties"]
                )
            else:
                raise ValueError(f"Unknown relay device type: {config['device']}")
            self.relays.append(relay)

    def init_pids(self, pid_configs: list):
        pids = []
        for config in pid_configs:
            pid_properties = config["heating_element_pid"]
            pid_controller = PIDController(
                connected_to=pid_properties["connected_to"]
            )
            pid = {
                "number": config["number"],
                "pid_controller": pid_controller
            }
            pids.append(pid)
        return pids