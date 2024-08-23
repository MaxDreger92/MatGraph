from pydantic import BaseModel, Field

from sdl.workflow.utils import BaseProcedure, P


class Location(BaseModel):
    device: str = Field(None, description="Name of the device")

class OpentronsLocation(BaseModel):
    slot: int = Field(None, description="Slot number")
    well: str = Field(None, description="Well ID")



class ArduinoBaseProcedure(BaseProcedure[P]):

    def __init__(self, params):
        super().__init__(params)

    name_space = "arduino"

    def execute(self, *args, **kwargs):
        raise NotImplementedError


    def wait_for_arduino(self, connection, max_wait_time: int = 2000, CONNECTION_TIMEOUT: int = 0.1, *args, **kwargs):
        """To make sure arduino completed the particular task.

        Args:
            max_wait_time (int, optional): Maximum wait time to get response
            from arduino in seconds. Defaults to 2000.

        Raises:
            RuntimeWarning: Arduino did not finish the job in given time.
        """
        logger = kwargs.get("logger")
        max_try = (1 / CONNECTION_TIMEOUT) * max_wait_time
        count = 0
        while count < max_try:
            logger.info("waiting for arduino to finish the task")
            state = connection.read().decode()
            if state == "#":
                logger.debug("Arduino finished the task")
                break
            count += 1
        else:
            raise RuntimeWarning(
                "Arduino did not finish the job.",
                "Check arduino IDE or increase the value of max_wait_time.",
            )