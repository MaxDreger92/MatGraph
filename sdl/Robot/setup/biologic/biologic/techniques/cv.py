""" This file contains the dataclass for the CV technique
| Author: Daniel Persaud <da.persaud@mail.utoronto.ca>
| Author: Mike Werezak <mike.werezak@nrcan-rncan.gc.ca>
| Created: 2024/05/08 15:02:54
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
    validate_len
)

if TYPE_CHECKING:
    from typing import Optional, Self
    from collections.abc import Sequence
    from biologic import BioLogic
    from biologic.channel import BLData
    from biologic.json import Json

__all__ = (
    'CVStep',
    'CVParams',
    'CVData',
    'CVTechnique',
)

# Technique timebase in seconds
CV_TIMEBASE = {
    DeviceFamily.VMP3 : 40e-6,
    DeviceFamily.SP300 : 45e-6,
}


@dataclass
class CVStep:
    voltage: float
    scan_rate: float
    vs_initial: bool

    def to_json(self) -> Json:
        return dict(
            voltage=self.voltage,
            scan_rate=self.scan_rate,
            vs_initial=self.vs_initial,
        )

    @classmethod
    def from_json(cls, json: Json) -> Self:
        return cls(
            voltage=json['voltage'],
            scan_rate=json['scan_rate'],
            vs_initial=json['vs_initial'],
        )


@dataclass
class CVParams(TechniqueParams):
    scan_number: int = Parameter(
        'Scan_number', int, default=2, create_field=False,  # always 2
    )
    record_every_dE: float = Parameter(
        'Record_every_dE', float, units="V", data_range=DataRange(0, None),
    )
    average_over_dE: bool = Parameter(
        'Average_over_dE', bool,
    )
    n_cycles: int = Parameter(
        'N_Cycles', int, data_range=DataRange(0, None),
    )
    begin_measuring_i: float = Parameter(
        'Begin_measuring_I', float, data_range=DataRange(0, 1),
    )
    end_measuring_i: float = Parameter(
        'End_measuring_I', float, data_range=DataRange(0, 1),
    )

    Ei: CVStep = Parameter(
        to_json=lambda value: value.to_json(),
        from_json=lambda json: CVStep.from_json(json),
    )
    E1: CVStep = Parameter(
        to_json=lambda value: value.to_json(),
        from_json=lambda json: CVStep.from_json(json),
    )
    E2: CVStep = Parameter(
        to_json=lambda value: value.to_json(),
        from_json=lambda json: CVStep.from_json(json),
    )
    Ef: CVStep = Parameter(
        to_json=lambda value: value.to_json(),
        from_json=lambda json: CVStep.from_json(json),
    )

    # these parameters are derived from Ei, E1, E2, Ef
    vs_initial = Parameter(
        'vs_initial', bool,
        create_field=False,
    )
    voltage_step = Parameter(
        'Voltage_step', float, units="V",
        create_field=False,
    )
    scan_rate = Parameter(
        'Scan_Rate', float, units="mV/s", data_range=DataRange(0, None),
        create_field=False,
    )

    @vs_initial.property
    def vs_initial(self) -> Sequence[bool]:
        return [ step.vs_initial for step in self._step_sequence() ]

    @voltage_step.property
    def voltage_step(self) -> Sequence[float]:
        return [ step.voltage for step in self._step_sequence() ]

    @scan_rate.property
    def scan_rate(self) -> Sequence[float]:
        return [ step.scan_rate for step in self._step_sequence() ]

    def _step_sequence(self) -> Sequence[CVStep]:
        return self.Ei, self.E1, self.E2, self.Ei, self.Ef

    def validate(self, device_info: DeviceInfo) -> Iterable[ValidationError]:
        yield from yield_errors([
            validate_len(self.vs_initial, 'vs_initial', 5),
            validate_len(self.voltage_step, 'voltage_step', 5),
            validate_len(self.scan_rate, 'scan_rate', 5),
            *(
                item for idx in range(5) for item in (
                    validate_type(self.vs_initial[idx], f'vs_initial[{idx}]', bool),
                    validate_type(self.voltage_step[idx], f'voltage_step[{idx}]', Number),
                    validate_type(self.scan_rate[idx], f'scan_rate[{idx}]', Number),
                )
            ),

            validate_type(self.record_every_dE, 'record_every_dE', Number),
            validate_type(self.average_over_dE, 'average_over_dE', bool),
            validate_type(self.n_cycles, 'n_cycles', Number),
            validate_type(self.begin_measuring_i, 'begin_measuring_i', Number),
            validate_type(self.end_measuring_i, 'end_measuring_i', Number),
        ])
        yield from super().validate(device_info)
    

@dataclass(frozen=True)
class CVData(TimeSeriesData):
    Ec: Optional[float] = Field(units="V")
    I_avg: float = Field(units="A")
    Ewe_avg: float = Field(units="V")
    cycle: int = Field()

class CVTechnique(Technique, tech_id=TECH_ID.CV, params=CVParams, data=CVData):
    """
    Cyclic Voltammetry technique.

    Cyclic voltammetry (CV) is the most widely used technique for acquiring qualitative
    information about electrochemical reactions. CV provides information on redox
    processes, heterogeneous electron-transfer reactions and adsorption processes. It
    offers a rapid location of redox potential of the electroactive species.
    CV consists of scanning linearly the potential of a stationary working electrode using a
    triangular potential waveform. During the potential sweep, the potentiostat measures
    the current resulting from electrochemical reactions (consecutive to the applied
    potential). The cyclic voltammogram is a current response as a function of the applied
    potential.
    """

    timebase = CV_TIMEBASE

    ecc_path = {
        DeviceFamily.VMP3  : 'cv.ecc',
        DeviceFamily.SP300 : 'cv4.ecc',
    }

    def unpack_data(self, bl:BioLogic, data: BLData) -> Iterable[CVData]:
        for data_row in data.iter_data():
            t_high, t_low, *row = data_row

            time = data.convert_time(t_high, t_low)
            total_time = time + data.start_time

            if bl.device_info.family == DeviceFamily.VMP3:
                Ec, I_avg, Ewe_avg, cycle = row
            elif bl.device_info.family == DeviceFamily.SP300:
                I_avg, Ewe_avg, cycle = row
                Ec = None
            else:
                raise ValueError("unsupported device family")
            
            I_avg = bl.extract_float(I_avg)
            Ewe_avg = bl.extract_float(Ewe_avg)
            if Ec is not None:
                Ec = bl.extract_float(Ec)

            yield CVData(time, total_time, Ec, I_avg, Ewe_avg, cycle)
