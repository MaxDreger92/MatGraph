
from typing import Any, Dict, Optional

from pydantic import BaseModel

from sdl.processes.opentrons_utils import OpentronsBaseProcedure

class HomeRobotParams(BaseModel):
    pass


class HomeRobot(OpentronsBaseProcedure[HomeRobotParams]):
    commandType = 'home'
    url = '/robot/home'
    intent = None
