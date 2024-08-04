"""
| Author: Mike Werezak <mike.werezak@nrcan-rncan.gc.ca>
| Created: 2024/02/22
"""

from __future__ import annotations

from numbers import Number
from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable

from kbio.tech import TECH_ID

from biologic import DeviceFamily, DeviceInfo
from biologic.technique import Technique
from biologic.data import TimeSeriesData, Field
from biologic.params import (
    TechniqueParams,
    Parameter,
    ValidationError,
    DataRange,
    yield_errors,
    validate_type,
)

if TYPE_CHECKING:
    from typing import Optional
    from biologic import BioLogic
    from biologic.channel import BLData

__all__ = (
    'OCVParams',
    'OCVData',
    'OCVTechnique',
)

OCV_TIMEBASE = 20.0e-6  # seconds

@dataclass
class OCVParams(TechniqueParams):
    rest_time_T: float = Parameter(
        'Rest_time_T', float, units="s", data_range=DataRange(0, OCV_TIMEBASE*(1<<31)),
    )
    record_every_dE: float = Parameter(
        'Record_every_dE', float, units="V", data_range=DataRange(0, None),
    )
    record_every_dT: float = Parameter(
        'Record_every_dT', float, units="s", data_range=DataRange(0, None),
    )

    def validate(self, device_info: DeviceInfo) -> Iterable[ValidationError]:
        yield from yield_errors([
            validate_type(self.rest_time_T, 'rest_time_T', Number),
            validate_type(self.record_every_dT, 'record_every_dT', Number),
            validate_type(self.record_every_dE, 'record_every_dE', Number),
        ])
        yield from super().validate(device_info)


@dataclass(frozen=True)
class OCVData(TimeSeriesData):
    Ewe: float = Field(units="V")
    Ece: Optional[float] = Field(units="V")


class OCVTechnique(Technique, tech_id=TECH_ID.OCV, params=OCVParams, data=OCVData):
    """Open Circuit Voltage technique.

    The Open Circuit Voltage (OCV) technique consists of a period during which no potential
    or current is applied to the working electrode. The cell is disconnected from the power
    amplifier. Only, the potential measurement is available. So the evolution of the rest
    potential can be recorded."""

    timebase = OCV_TIMEBASE

    ecc_path = {
        DeviceFamily.VMP3  : 'ocv.ecc',
        DeviceFamily.SP300 : 'ocv4.ecc',
    }

    def unpack_data(self, bl: BioLogic, data: BLData) -> Iterable[OCVData]:
        # loop through the number of points saved in the buffer
        for data_row in data.iter_data():
            # extract timestamp and one row
            t_high, t_low, *row = data_row

            time = data.convert_time(t_high, t_low)
            total_time = time + data.start_time

            Ewe = bl.extract_float(row[0])
            Ece = bl.extract_float(row[1]) if bl.device_info.family == DeviceFamily.SP300 else None

            yield OCVData(time, total_time, Ewe, Ece)
