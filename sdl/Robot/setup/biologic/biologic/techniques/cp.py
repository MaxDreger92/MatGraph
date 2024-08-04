"""
| Author: Mike Werezak <mike.werezak@nrcan-rncan.gc.ca>
| Created: 2024/04/05
"""

from __future__ import annotations

from numbers import Number
from dataclasses import dataclass
from typing import TYPE_CHECKING

from biologic import BioLogic, DeviceFamily, I_RANGE, DeviceInfo
from biologic.channel import BLData
from biologic.technique import Technique, TECH_ID
from biologic.params import (
    TechniqueParams,
    Parameter,
    DataRange,
    yield_errors,
    validate_type,
    ValidationError,
)
from biologic.data import TimeSeriesData, Field
from biologic.json import Json

if TYPE_CHECKING:
    from typing import Self
    from collections.abc import Iterable, Sequence


CP_TIMEBASE = 21e-6

@dataclass
class CPStep:
    current: float
    duration: float
    vs_initial: bool

    def to_json(self) -> Json:
        return dict(
            current=self.current,
            duration=self.duration,
            vs_initial=self.vs_initial,
        )

    @classmethod
    def from_json(cls, json: Json) -> Self:
        return cls(
            current=json['current'],
            duration=json['duration'],
            vs_initial=json['vs_initial'],
        )


@dataclass
class CPParams(TechniqueParams):
    record_every_dT: float = Parameter(
        'Record_every_dT', float, units="V", data_range=DataRange(0, None),
    )
    record_every_dE: float = Parameter(
        'Record_every_dE', float, units="V", data_range=DataRange(0, None),
    )
    n_cycles: int = Parameter(
        'N_Cycles', int, data_range=DataRange(0, None),
    )

    steps: Sequence[CPStep] = Parameter(
        to_json=lambda s: [ step.to_json() for step in s ],
        from_json=lambda s: [CPStep.from_json(step) for step in s],
    )

    # these parameters are derived from steps
    current_step = Parameter(
        'Current_step', float, units="A",
        create_field=False,
    )
    vs_initial = Parameter(
        'vs_initial', bool,
        create_field=False,
    )
    duration_step = Parameter(
        'Duration_step', float, units="s",
        data_range=DataRange(0, CP_TIMEBASE*(1<<31)),
        create_field=False,
    )
    step_number = Parameter(
        'Step_number', int, data_range=DataRange(0, 98),
        create_field=False,
    )

    @current_step.property
    def current_step(self) -> Iterable[float]:
        for step in self.steps:
            yield step.current

    @duration_step.property
    def duration_step(self) -> Iterable[float]:
        for step in self.steps:
            yield step.duration

    @vs_initial.property
    def vs_initial(self) -> Iterable[bool]:
        for step in self.steps:
            yield step.vs_initial

    @step_number.property
    def step_number(self) -> int:
        return len(self.steps) - 1

    def validate(self, device_info: DeviceInfo) -> Iterable[ValidationError]:
        if self.I_range == I_RANGE.I_RANGE_AUTO:
            yield ValidationError('I_range', "I auto-range is not allowed for this technique")

        yield from yield_errors([
            validate_type(self.record_every_dT, 'record_every_dT', Number),
            validate_type(self.record_every_dE, 'record_every_dI', Number),
            validate_type(self.n_cycles, 'n_cycles', int),

            *(
                validate_type(o, f'current_step[{idx}]', Number)
                for idx, o in enumerate(self.current_step)
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
class CPData(TimeSeriesData):
    Ewe: float = Field(units="V")
    I: float = Field(units="A")
    cycle: int = Field()


class CPTechnique(Technique, tech_id=TECH_ID.CP, params=CPParams, data=CPData):
    """Chrono-Potentiometry technique.

    The Chronopotentiometry (CP) is a controlled current technique. The current is
    controlled and the potential is the variable determined as a function of time. The
    chronopotentiometry technique is similar to the Chronoamperometry technique,
    potential steps being replaced by current steps. The current is applied between the
    working and the counter electrode.

    This technique can be used for different kind of analysis or to investigate electrode
    kinetics. It is considered less sensitive than voltammetric techniques for analytical uses.
    Generally, the curves Ewe = f(t) contains plateaus that correspond to the redox potential
    of electroactive species."""

    timebase = CP_TIMEBASE

    ecc_path = {
        DeviceFamily.VMP3  : 'cp.ecc',
        DeviceFamily.SP300 : 'cp4.ecc',
    }

    def unpack_data(self, bl: BioLogic, data: BLData) -> Iterable[CPData]:
        for data_row in data.iter_data():
            t_high, t_low, Ewe, I, cycle = data_row

            time = data.convert_time(t_high, t_low)
            total_time = time + data.start_time
            Ewe = bl.extract_float(Ewe)
            I = bl.extract_float(I)
            yield CPData(time, total_time, Ewe, I, cycle)
