# generated by datamodel-codegen:
#   filename:  load_labware.json
#   timestamp: 2024-07-17T18:49:32+00:00

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from sdl.processes.opentrons_utils import OpentronsBaseProcedure


class LoadLabwareParams(BaseModel):
    slotName: str
    loadName: str
    namespace: str
    version: int


class LoadLabware(OpentronsBaseProcedure[LoadLabwareParams]):
    url = '/runs/{run_id}/commands'
    commandType = 'load_labware'
    intent = None
