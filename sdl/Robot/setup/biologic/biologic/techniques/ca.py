"""
| Author: Mike Werezak <mike.werezak@nrcan-rncan.gc.ca>
| Created: 2024/04/05
"""

from __future__ import annotations

from numbers import Number
from dataclasses import dataclass
from typing import TYPE_CHECKING

from biologic import BioLogic, DeviceFamily, DeviceInfo
from biologic.channel import BLData
from biologic.technique import Technique, TECH_ID
from biologic.params import (
    TechniqueParams,
    Parameter,
    DataRange,
    ValidationError,
    yield_errors,
    validate_type,
)
from biologic.data import TimeSeriesData, Field
from biologic.json import Json

if TYPE_CHECKING:
    from typing import Self
    from collections.abc import Iterable, Sequence


CA_TIMEBASE = {
    DeviceFamily.VMP3  : 24e-6,
    DeviceFamily.SP300 : 21e-6,
}

@dataclass
class CAStep:
    voltage: float
    duration: float
    vs_initial: bool

    def to_json(self) -> Json:
        return dict(
            voltage=self.voltage,
            duration=self.duration,
            vs_initial=self.vs_initial,
        )

    @classmethod
    def from_json(cls, json: Json) -> Self:
        return cls(
            voltage=json['voltage'],
            duration=json['duration'],
            vs_initial=json['vs_initial'],
        )


@dataclass
class CAParams(TechniqueParams):
    record_every_dT: float = Parameter(
        'Record_every_dT', float, units="s", data_range=DataRange(0, None),
    )
    record_every_dI: float = Parameter(
        'Record_every_dI', float, units="A", data_range=DataRange(0, None),
    )
    n_cycles: int = Parameter(
        'N_Cycles', int, data_range=DataRange(0, None),
    )

    steps: Sequence[CAStep] = Parameter(
        to_json=lambda s: [ step.to_json() for step in s ],
        from_json=lambda s: [ CAStep.from_json(step) for step in s ],
    )

    # these parameters are derived from steps
    voltage_step = Parameter(
        'Voltage_step', float, units="V",
        create_field=False,
    )
    vs_initial = Parameter(
        'vs_initial', bool,
        create_field=False,
    )
    duration_step = Parameter(
        'Duration_step', float, units="s",
        data_range=lambda device: DataRange(0, CA_TIMEBASE[device.family]*(1<<31)),
        create_field=False,
    )
    step_number = Parameter(
        'Step_number', int, data_range=DataRange(0, 98),
        create_field=False,
    )

    @voltage_step.property
    def voltage_step(self) -> Sequence[float]:
        return [ step.voltage for step in self.steps ]

    @duration_step.property
    def duration_step(self) -> Sequence[float]:
        return [ step.duration for step in self.steps ]

    @vs_initial.property
    def vs_initial(self) -> Sequence[bool]:
        return [ step.vs_initial for step in self.steps ]

    @step_number.property
    def step_number(self) -> int:
        return len(self.steps) - 1

    def validate(self, device_info: DeviceInfo) -> Iterable[ValidationError]:
        yield from yield_errors([
            validate_type(self.record_every_dT, 'record_every_dT', Number),
            validate_type(self.record_every_dI, 'record_every_dI', Number),
            validate_type(self.n_cycles, 'n_cycles', int),

            *(
                validate_type(o, f'voltage_step[{idx}]', Number)
                for idx, o in enumerate(self.voltage_step)
            ),
            *(
                validate_type(o, f'vs_initial[{idx}]', bool)
                for idx, o in enumerate(self.vs_initial)
            ),
            *(
                validate_type(o, f'duration_step[{idx}]', Number)
                for idx, o in enumerate(self.duration_step)
            ),

        ])
        yield from super().validate(device_info)



@dataclass(frozen=True)
class CAData(TimeSeriesData):
    Ewe: float = Field(units="V")
    I: float = Field(units="A")
    cycle: int = Field()


class CATechnique(Technique, tech_id=TECH_ID.CA, params=CAParams, data=CAData):
    """Chrono-Amperometry technique.

    The basis of the controlled-potential techniques is the measurement of the current
    response to an applied potential step.

    The Chronoamperometry (CA) technique involves stepping the potential of the working
    electrode from an initial potential, at which (generally) no faradic reaction occurs, to a
    potential Ei at which the faradic reaction occurs. The current-time response reflects the
    change in the concentration gradient in the vicinity of the surface.
    Chronoamperometry is often used for measuring the diffusion coefficient of
    electroactive species or the surface area of the working electrode. This technique can
    also be applied to the study of electrode processes mechanisms.

    An alternative and very useful mode for recording the electrochemical response is to
    integrate the current, so that one obtains the charge passed as a function of time. This
    is the chronocoulometric mode that is particularly used for measuring the quantity of
    adsorbed reactants."""

    timebase = CA_TIMEBASE

    ecc_path = {
        DeviceFamily.VMP3  : 'ca.ecc',
        DeviceFamily.SP300 : 'ca4.ecc',
    }

    def unpack_data(self, bl: BioLogic, data: BLData) -> Iterable[CAData]:
        for data_row in data.iter_data():
            t_high, t_low, Ewe, I, cycle = data_row

            time = data.convert_time(t_high, t_low)
            total_time = time + data.start_time
            Ewe = bl.extract_float(Ewe)
            I = bl.extract_float(I)
            yield CAData(time, total_time, Ewe, I, cycle)
