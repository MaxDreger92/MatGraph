import time

from sdl.Robot.workflow.processes.lib.arduino_utils import ArduinoBaseProcedure


class Disconnect(ArduinoBaseProcedure):
    command_type: str = "disconnect"

    def execute(self, connection):
        connection.close()
        time.sleep(31)
        return connection
