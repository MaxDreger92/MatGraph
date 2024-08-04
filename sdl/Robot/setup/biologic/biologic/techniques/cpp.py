"""
| Author: Mike Werezak <mike.werezak@nrcan-rncan.gc.ca>
| Created: 2024/04/02
"""

from __future__ import annotations

from numbers import Number
from dataclasses import dataclass
from typing import TYPE_CHECKING

from biologic import BioLogic, DeviceFamily, DeviceInfo
from biologic.channel import BLData
from kbio.tech import TECH_ID

from biologic.technique import Technique
from biologic.data import TimeSeriesData, Field
from biologic.params import (
    TechniqueParams,
    Parameter,
    ValidationError,
    DataRange,
    yield_errors,
    validate_type,
    validate_len,
)

if TYPE_CHECKING:
    from typing import Optional
    from collections.abc import Iterable


# Technique timebase in seconds
CPP_TIMEBASE = {
    DeviceFamily.VMP3 : 40e-6,
    DeviceFamily.SP300 : 44e-6,
}

@dataclass
class CPPParams(TechniqueParams):
    record_every_dEr: float = Parameter(
        'Record_every_dEr', float, units="V", data_range=DataRange(0, None),
    )
    rest_time_T: float = Parameter(
        'Rest_time_T', float, units="s",
        data_range=lambda device: DataRange(0, CPP_TIMEBASE[device.family]*(1<<31)),
    )
    record_every_dTr: float = Parameter(
        'Record_every_dTr', float, units="s", data_range=DataRange(0, None),
    )
    vs_initial_scan: tuple[bool, bool, bool] = Parameter(
        'vs_initial_scan', bool,
    )
    voltage_scan: tuple[float, float, float] = Parameter(
        'Voltage_scan', float, units="V",
    )
    scan_rate: tuple[float, float, float] = Parameter(
        'Scan_Rate', float, units="V/s", data_range=DataRange(0, None),
    )
    scan_number: int = Parameter(
        'Scan_number', int, default=1, create_field=False,  # always 1
    )
    I_pitting: float = Parameter(
        'I_pitting', float, units="A", data_range=DataRange(0, None),
    )
    t_b: float = Parameter(
        't_b', float, units="s", data_range=DataRange(0, None),
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
    record_every_dT: float = Parameter(
        'Record_every_dT', float, units="s", data_range=DataRange(0, None),
    )

    def validate(self, device_info: DeviceInfo) -> Iterable[ValidationError]:
        yield from yield_errors([
            validate_type(self.record_every_dEr, 'record_every_dEr', Number),
            validate_type(self.rest_time_T, 'rest_time_T', Number),
            validate_type(self.record_every_dTr, 'record_every_dTr', Number),

            validate_len(self.vs_initial_scan, 'vs_initial_scan', 3),
            validate_len(self.voltage_scan, 'voltage_scan', 3),
            validate_len(self.scan_rate, 'scan_rate', 3),
            *(
                item for idx in range(3) for item in (
                    validate_type(self.vs_initial_scan[idx], f'vs_initial_scan[{idx}]', bool),
                    validate_type(self.voltage_scan[idx], f'voltage_scan[{idx}]', Number),
                    validate_type(self.scan_rate[idx], f'scan_rate[{idx}]', Number),
                )
            ),

            validate_type(self.I_pitting, 'I_pitting', Number),
            validate_type(self.t_b, 't_b', Number),
            validate_type(self.record_every_dE, 'record_every_dE', Number),
            validate_type(self.average_over_dE, 'average_over_dE', bool),
            validate_type(self.begin_measuring_I, 'begin_measuring_I', Number),
            validate_type(self.end_measuring_I, 'end_measuring_I', Number),
            validate_type(self.record_every_dT, 'record_every_dT', Number),
        ])
        yield from super().validate(device_info)


@dataclass(frozen=True)
class CPPData(TimeSeriesData):
    Ewe: Optional[float] = Field(units="V")
    Ec: Optional[float] = Field(units="V")
    I_avg: Optional[float] = Field(units="A")
    Ewe_avg: Optional[float] = Field(units="V")


class CPPTechnique(Technique, tech_id=TECH_ID.CPP, params=CPPParams, data=CPPData):
    """Cyclic PotentioDynamic Polarization technique.

    The Cyclic Potentiodynamic Polarization is often used to evaluate pitting susceptibility.
    It is the most common electrochemical test for localized corrosion resistance. The
    potential is swept in a single cycle or slightly less than one cycle. The size of the
    hysteresis is examined along with the difference between the values of the starting
    Open circuit corrosion potential and the return passivation potential. The existence of
    hysteresis is usually indicative of pitting, while the size of the loop is often related to
    the amount of pitting. This technique can be used to determine the pitting potential and
    the repassivation potential.

    This technique is based both on the PDP and PSP techniques. It begins with a
    potentiodynamic phase where the potential increases. This phase is limited either with
    a limit potential (EL) or with a pitting current (Ip) defined by the user. If the pitting
    current is not reached during the potentiodynamic phase, then a potentiostatic phase
    is applied until pitting (Ip is reached). Ip can be used as a safety parameter in order to
    avoid damages on the working electrode. Then an additional potentiodynamic phase is
    done as a reverse scan."""

    timebase = CPP_TIMEBASE

    ecc_path = {
        DeviceFamily.VMP3  : 'cpp.ecc',
        DeviceFamily.SP300 : 'cpp4.ecc',
    }

    def unpack_data(self, bl: BioLogic, data: BLData) -> Iterable[CPPData]:
        process_idx = data.data_info.ProcessIndex
        for data_row in data.iter_data():
            t_high, t_low, *row = data_row

            time = data.convert_time(t_high, t_low)
            total_time = time + data.start_time

            if process_idx == 0:
                (Ewe,) = row
                Ewe = bl.extract_float(Ewe)
                yield CPPData(time, total_time, Ewe, None, None, None)

            elif process_idx == 1:
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
                yield CPPData(time, total_time, None, Ec, I_avg, Ewe_avg)

            else:
                raise ValueError("invalid process index")
