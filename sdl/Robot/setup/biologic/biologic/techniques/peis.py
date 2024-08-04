"""
| Author: Mike Werezak <mike.werezak@nrcan-rncan.gc.ca>
| Created: 2024/06/07
"""

from __future__ import annotations

from enum import Enum
from numbers import Number
from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable

from biologic import BioLogic, DeviceFamily, DeviceInfo
from biologic.channel import BLData
from kbio.tech import TECH_ID

from biologic.technique import Technique
from biologic.data import TechniqueData, TimeSeriesData, Field
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


PEIS_TIMEBASE = 24e-6  # seconds


class SweepMode(Enum):
    Linear = True
    Logarithmic = False


@dataclass
class PEISParams(TechniqueParams):
    vs_initial: bool = Parameter('vs_initial', bool)
    vs_final = Parameter('vs_final', bool, create_field=False)

    @vs_final.property
    def vs_final(self) -> bool:
        return self.vs_initial  # always equal to vs_initial

    initial_voltage_step: float = Parameter(
        'Initial_Voltage_step', float, units="V",
    )
    final_voltage_step = Parameter(
        'Final_Voltage_step', float, units="V", create_field=False,
    )

    @final_voltage_step.property
    def final_voltage_step(self) -> float:
        return self.initial_voltage_step  # always equal to initial_voltage_step

    duration_step: float = Parameter(
        'Duration_step', float, units="s", data_range=DataRange(0, PEIS_TIMEBASE*(1<<31)),
    )

    step_number = Parameter(
        'Step_number', int, create_field=False, default=0,  # always 0
    )

    record_every_dT: float = Parameter(
        'Record_every_dT', float, units="s", data_range=DataRange(0, None),
    )
    record_every_dI: float = Parameter(
        'Record_every_dI', float, units="A", data_range=DataRange(0, None),
    )
    final_frequency: float = Parameter(
        'Final_frequency', float, units="Hz",
    )
    initial_frequency: float = Parameter(
        'Initial_frequency', float, units="Hz",
    )
    sweep: SweepMode = Parameter(
        'sweep', bool,
        pack=lambda o: o.value,
        to_json=lambda o: o.name,
        from_json=lambda s: SweepMode[s],
    )

    amplitude_voltage: float = Parameter(
        'Amplitude_Voltage', float, units="V",
    )

    frequency_number: int = Parameter(
        "Frequency_number", int, data_range=DataRange(1, None),
    )
    average_n_times: int = Parameter(
        "Average_N_times", int, data_range=DataRange(1, None),
    )

    correction: bool = Parameter('Correction', bool)

    wait_for_steady: float = Parameter('Wait_for_steady', float, data_range=DataRange(0, None))

    def validate(self, device_info: DeviceInfo) -> Iterable[ValidationError]:
        yield from yield_errors([
            validate_type(self.vs_initial, 'vs_initial', bool),
            validate_type(self.initial_voltage_step, 'initial_voltage_step', Number),
            validate_type(self.duration_step, 'duration_step', Number),
            validate_type(self.record_every_dT, 'record_every_dT', Number),
            validate_type(self.record_every_dI, 'record_every_dI', Number),
            validate_type(self.final_frequency, 'final_frequency', Number),
            validate_type(self.initial_frequency, 'initial_frequency', Number),
            validate_type(self.sweep, 'sweep', SweepMode),
            validate_type(self.amplitude_voltage, 'amplitude_voltage', Number),
            validate_type(self.frequency_number, 'frequency_number', int),
            validate_type(self.average_n_times, 'average_n_times', int),
            validate_type(self.correction, 'correction', bool),
            validate_type(self.wait_for_steady, 'wait_for_steady', Number),
        ])
        yield from super().validate(device_info)


@dataclass(frozen=True)
class PEISData(TechniqueData):
    process_index: int = Field()
    process_data: PEISProcess0Data | PEISProcess1Data = Field()

@dataclass(frozen=True)
class PEISProcess0Data(TimeSeriesData):
    Ewe: float = Field(units="V")
    I: float = Field(units="A")

@dataclass(frozen=True)
class PEISProcess1Data(TechniqueData):
    freq: float = Field()
    Ewe_mod: float = Field()
    I_mod: float = Field()
    phase_Zwe: float = Field()
    Ewe: float = Field()
    I: float = Field()
    Ece_mod: float = Field()
    Ice_mod: float = Field()
    phase_Zce: float = Field()
    Ece: float = Field()
    total_time: float = Field()
    I_range: Optional[float] = Field()  # no idea what the units are for this


class PEISTechnique(Technique, tech_id=TECH_ID.PEIS, params=PEISParams, data=PEISData):
    """Potentio Electrochemical Impedance Spectroscopy technique.

    The Potentio Electrochemical Impedance Spectroscopy (PEIS) technique performs
    impedance measurements into potentiostatic mode in applying a sine wave around a
    DC potential E that can be set to a fixed value or relatively to the cell equilibrium
    potential.

    For very capacitive or low impedance electrochemical systems, the potential amplitude
    can lead to a current overflow that can stop the experiment in order to protect the unit
    from overheating. Using GEIS instead of PEIS can avoid this inconvenient situation.

    Moreover, during corrosion experiment, a potential shift of the electrochemical system
    can occur. PEIS technique can lead to impedance measurements far from the corrosion
    potential while GEIS can be performed at a zero current."""

    timebase = PEIS_TIMEBASE

    ecc_path = {
        DeviceFamily.VMP3  : 'peis.ecc',
        DeviceFamily.SP300 : 'peis4.ecc',
    }

    def unpack_data(self, bl: BioLogic, data: BLData) -> Iterable[PEISData]:
        process_idx = data.data_info.ProcessIndex
        for data_row in data.iter_data():
            if process_idx == 0:
                t_high, t_low, *row = data_row

                time = data.convert_time(t_high, t_low)
                total_time = time + data.start_time

                Ewe, I = row
                Ewe = bl.extract_float(Ewe)
                I = bl.extract_float(I)
                yield PEISData(
                    process_index=0,
                    process_data=PEISProcess0Data(time, total_time, Ewe, I),
                )

            elif process_idx == 1:
                if bl.device_info.family == DeviceFamily.VMP3:
                    (
                        freq, Ewe_mod, I_mod, phase_Zwe, Ewe, I, _, Ece_mod,
                        Ice_mod, phase_Zce, Ece, _, _, t, I_range,
                    ) = data_row
                elif bl.device_info.family == DeviceFamily.SP300:
                    (
                        freq, Ewe_mod, I_mod, phase_Zwe, Ewe, I, _, Ece_mod,
                        Ice_mod, phase_Zce, Ece, _, _, t,
                    ) = data_row
                    I_range = None
                else:
                    raise ValueError("unsupported device family")

                yield PEISData(
                    process_index=1,
                    process_data=PEISProcess1Data(
                        freq = bl.extract_float(freq),
                        Ewe_mod = bl.extract_float(Ewe_mod),
                        I_mod = bl.extract_float(I_mod),
                        phase_Zwe = bl.extract_float(phase_Zwe),
                        Ewe = bl.extract_float(Ewe),
                        I = bl.extract_float(I),
                        Ece_mod = bl.extract_float(Ece_mod),
                        Ice_mod = bl.extract_float(Ice_mod),
                        phase_Zce = bl.extract_float(phase_Zce),
                        Ece = bl.extract_float(Ece),
                        total_time = bl.extract_float(t),
                        I_range = None if I_range is None else bl.extract_float(I_range),
                    ),
                )

            else:
                raise ValueError("invalid process index")
