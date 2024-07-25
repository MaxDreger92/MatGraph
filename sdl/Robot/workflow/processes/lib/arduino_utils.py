from sdl.Robot.workflow.utils import BaseProcedure


class ArduinoBaseProcedure(BaseProcedure):

    name_space = "arduino"

    def execute(self, *args, **kwargs):
        raise NotImplementedError


    def wait_for_arduino(self, max_wait_time: int = 2000, CONNECTION_TIMEOUT: int = 0.1):
        """To make sure arduino completed the particular task.

        Args:
            max_wait_time (int, optional): Maximum wait time to get response
            from arduino in seconds. Defaults to 2000.

        Raises:
            RuntimeWarning: Arduino did not finish the job in given time.
        """
        max_try = (1 / CONNECTION_TIMEOUT) * max_wait_time
        count = 0
        while count < max_try:
            self.LOGGER.debug("waiting for arduino to finish the task")
            state = self.connection.read().decode()
            if state == "#":
                self.LOGGER.debug("Arduino finished the task")
                break
            count += 1
        else:
            raise RuntimeWarning(
                "Arduino did not finish the job.",
                "Check arduino IDE or increase the value of max_wait_time.",
            )