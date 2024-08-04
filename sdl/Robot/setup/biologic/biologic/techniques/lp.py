""" This file contains the dataclass for the LP technique
| Author: Daniel Persaud <da.persaud@mail.utoronto.ca>
| Author: Mike Werezak <mike.werezak@nrcan-rncan.gc.ca>
| Created: 2024/06/05 12:03:35
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
    'LPStep',
    'LPParams',
    'LPData',
    'LPTechnique',
)

# Technique timebase in seconds
LP_TIMEBASE = 40e-6

@dataclass
class LPStep:
    voltage_scan: float
    scan_rate: float
    vs_initial_scan: bool

    def to_json(self) -> Json:
        return dict(
            voltage_scan=self.voltage_scan,
            scan_rate=self.scan_rate,
            vs_initial_scan=self.vs_initial_scan,
        )
    
    @classmethod
    def from_json(cls, json: Json) -> Self:
        return cls(
            voltage_scan=json['voltage_scan'],
            scan_rate=json['scan_rate'],
            vs_initial_scan=json['vs_initial_scan'],
        )
    
@dataclass
class LPParams(TechniqueParams):
    record_every_dEr: float = Parameter(
        'Record_every_dEr', float, units="V", data_range=DataRange(0, None),
    )
    rest_time_T: float = Parameter(
        'Rest_time_T', float, units="s", data_range=DataRange(0, LP_TIMEBASE*(1<<31)),
    )
    record_every_dTr: float = Parameter(
        'Record_every_dTr', float, units="s", data_range=DataRange(0, None),
    )
    oc1: bool = Parameter(
        'OC1', bool, create_field=False, default=False,
    )
    e1: float = Parameter(
        'E1', float, units="V", data_range=DataRange(0, None), create_field=False, default=0,
    )
    t1: float = Parameter(
        'T1', float, units="s", data_range=DataRange(0, None), create_field=False, default=0,
    )
    Ei: LPStep = Parameter(
        to_json=lambda value: value.to_json(),
        from_json=lambda json: LPStep.from_json(json),
    )
    El: LPStep = Parameter(
        to_json=lambda value: value.to_json(),
        from_json=lambda json: LPStep.from_json(json),
    )
    scan_number: int = Parameter(
        'Scan_number', int, default=0, create_field=False,  # always 0
    ) 
    record_every_dE: float = Parameter(
        'Record_every_dE', float, units="V", data_range=DataRange(0, None),
    )
    average_over_dE: bool = Parameter(
        'Average_over_dE', bool,
    )
    begin_measuring_I: float = Parameter(
        'Begin_measuring_I', float, data_range=DataRange(0, 1),
    )
    end_measuring_I: float = Parameter(
        'End_measuring_I', float, data_range=DataRange(0, 1),
    )


    # these parameters are derived from Ei and El
    vs_initial_scan = Parameter(
        'vs_initial_scan', bool,
        create_field=False,
    )
    voltage_scan = Parameter(
        'Voltage_scan', float, units="V",
        create_field=False,
    )
    scan_rate = Parameter(
        'Scan_Rate', float, units="mV/s", data_range=DataRange(0, None),
        create_field=False,
    )

    @vs_initial_scan.property
    def vs_initial_scan(self) -> Sequence[bool]:
        return [ step.vs_initial_scan for step in self._step_sequence() ]
    
    @voltage_scan.property
    def voltage_scan(self) -> Sequence[float]:
        return [ step.voltage_scan for step in self._step_sequence() ]
    
    @scan_rate.property
    def scan_rate(self) -> Sequence[float]:
        return [ step.scan_rate for step in self._step_sequence() ]
    
    def _step_sequence(self) -> Sequence[LPStep]:
        return self.Ei, self.El

    def validate(self, device_info: DeviceInfo) -> Iterable[ValidationError]:
        yield from yield_errors([
            validate_type(self.record_every_dEr, 'record_every_dEr', Number),
            validate_type(self.rest_time_T, 'rest_time_T', Number),
            validate_type(self.record_every_dTr, 'record_every_dTr', Number),
            validate_len(self.vs_initial_scan, 'vs_initial_scan', 2),
            validate_len(self.voltage_scan, 'voltage_scan', 2),
            validate_len(self.scan_rate, 'scan_rate', 2),
            *(
                item for idx in range(2) for item in (
                    validate_type(self.vs_initial_scan[idx], f'vs_initial_scan[{idx}]', bool),
                    validate_type(self.voltage_scan[idx], f'voltage_scan[{idx}]', Number),
                    validate_type(self.scan_rate[idx], f'scan_rate[{idx}]', Number),
                )
            ),
            validate_type(self.record_every_dE, 'record_every_dE', Number),
            validate_type(self.average_over_dE, 'average_over_dE', bool),
            validate_type(self.begin_measuring_I, 'begin_measuring_I', Number),
            validate_type(self.end_measuring_I, 'end_measuring_I', Number),
        ])
        yield from super().validate(device_info)

@dataclass(frozen=True)
class LPData(TimeSeriesData):
    Ewe: Optional[float] = Field(units="V")
    Ec: Optional[float] = Field(units="V")
    I_avg: Optional[float] = Field(units="A")
    Ewe_avg: Optional[float] = Field(units="V")

class LPTechnique(Technique, tech_id=TECH_ID.LP, params=LPParams, data=LPData):
    """
    Linear Polarization technique

    The linear polarization technique is used in corrosion monitoring. This technique is
    especially designed for the determination of a polarization resistance Rp of a material
    and Icorr through potential steps around the corrosion potentia l.
    Rp is defined as the slope of the potential
    current density curve at the free corrosion
    potential: Rp = (dE/dI) dE -->0
    Rp is determined using the ''Rp fit'' graphic tool. Contrary to the Potentiodynamic Pitting
    (PDP) technique, no current limitation is available with the linear polarization technique.
    """

    timebase = LP_TIMEBASE

    ecc_path = {
        DeviceFamily.VMP3  : 'lp.ecc',
        DeviceFamily.SP300 : 'lp4.ecc',
    }

    def unpack_data(self, bl:BioLogic, data: BLData) -> Iterable[LPData]:
        process_idx = data.data_info.ProcessIndex
        for data_row in data.iter_data():
            t_high, t_low, *row = data_row

            time = data.convert_time(t_high, t_low)
            total_time = time + data.start_time

            if process_idx == 0:
                (Ewe,) = row
                Ewe = bl.extract_float(Ewe)
                yield LPData(time, total_time, Ewe, None, None, None)

            elif process_idx == 1:
                Ewe = None
                if bl.device_info.family == DeviceFamily.VMP3:
                    Ec, I_avg, Ewe_avg = row
                elif bl.device_info.family == DeviceFamily.SP300:
                    I_avg, Ewe_avg = row
                    Ec = None
                else:
                    raise ValueError("unsupported device family")

                I_avg = bl.extract_float(I_avg)
                Ewe_avg = bl.extract_float(Ewe_avg)
                if Ec is not None:
                    Ec = bl.extract_float(Ec)
                yield LPData(time, total_time, Ewe, Ec, I_avg, Ewe_avg)

            else:
                raise ValueError("unsupported process index")
                              

