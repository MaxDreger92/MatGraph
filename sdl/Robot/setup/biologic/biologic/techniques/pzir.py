"""
| Author: Mike Werezak <mike.werezak@nrcan-rncan.gc.ca>
| Created: 2024/06/07
"""

from __future__ import annotations

from enum import Enum
from numbers import Number
from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable

from biologic import DeviceFamily, I_RANGE
from biologic.channel import BLData
from biologic.technique import (
    TECH_ID,
    Technique,
    TechniqueData,
    TechniqueParams,
    ValidationError,
)
from biologic.params import (
    Parameter,
    DataRange,
    yield_errors,
    validate_type,
)
from biologic.data import Field

if TYPE_CHECKING:
    from typing import Optional
    from biologic import BioLogic, DeviceInfo


PZIR_TIMEBASE = 24e-6  # seconds


class RcmpMode(Enum):
    Software = 0
    Hardware = 1


@dataclass
class PZIRParams(TechniqueParams):
    frequency: float = Parameter(units="Hz")

    # PZIR only uses one frequency.
    # But since the docs call for two frequency parameters we stick to that here,
    # but derive their values from the single frequency parameter above.
    final_frequency = Parameter(
        'Final_frequency', float, units="Hz", create_field=False,
    )
    initial_frequency = Parameter(
        'Initial_frequency', float, units="Hz", create_field=False,
    )

    @final_frequency.property
    def final_frequency(self) -> float:
        return self.frequency
    @initial_frequency.property
    def initial_frequency(self) -> float:
        return self.frequency

    amplitude_voltage: float = Parameter(
        'Amplitude_Voltage', float, units="V",
    )

    average_n_times: int = Parameter(
        'Average_N_times', int, data_range=DataRange(1, None),
    )

    wait_for_steady: float = Parameter(
        'Wait_for_steady', float, data_range=DataRange(0, None),
    )

    sweep = Parameter('sweep', bool, create_field=False, default=True)  # must be always True

    # NOTE: To deactivate the compensation, you can simply set the Rcomp_Level to 0 and Rcmp_Mode to software.
    rcomp_level: float = Parameter(
        'Rcomp_Level', float, units="%IR", data_range=DataRange(0, None),
    )

    rcmp_mode: RcmpMode = Parameter(
        'Rcmp_Mode', int,
        default=RcmpMode.Software,
        supports_devices=lambda device: device.family == DeviceFamily.SP300,
        pack=lambda o: o.value,
        to_json=lambda o: o.name,
        from_json=lambda s: RcmpMode[s],
    )

    def validate(self, device_info: DeviceInfo) -> Iterable[ValidationError]:
        yield from yield_errors([
            validate_type(self.frequency, 'frequency', Number),
            validate_type(self.amplitude_voltage, 'amplitude_voltage', Number),
            validate_type(self.average_n_times, 'average_n_times', int),
            validate_type(self.wait_for_steady, 'wait_for_steady', Number),
            validate_type(self.rcomp_level, 'rcomp_level', Number),
            validate_type(self.rcmp_mode, 'rcmp_mode', RcmpMode),
        ])
        yield from super().validate(device_info)


@dataclass(frozen=True)
class PZIRData(TechniqueData):
    freq: float = Field(units="Hz")
    Ewe_mod: float = Field(units="V")
    I_mod: float = Field(units="A")
    phase_Zwe: float = Field(units="rad")
    Ewe: float = Field(units="V")
    I: float = Field(units="A")
    Ece_mod: float = Field(units="V")
    Ice_mod: float = Field(units="A")
    phase_Zce: float = Field(units="rad")
    Ece: float = Field(units="V")
    t: float = Field()  # not sure what this is. time?
    I_range: Optional[I_RANGE] = Field()  # member of the I_RANGE enum maybe?


class PZIRTechnique(Technique, tech_id=TECH_ID.PZIR, params=PZIRParams, data=PZIRData):
    """IR Determination with PotentioStatic Impedance technique.

    The ohmic drop iRu is the voltage drop developed across the solution resistance Ru
    between the reference electrode and the working electrode, when current is flowing
    through. When the product iRu gets significant it introduces an important error in the
    control of the working electrode potential and should be compensated.

    The IR Determination with Potentiostatic Impedance (PZIR) technique utilizes
    Impedance measurements to determine the Ru Value. This technique applies a
    sinusoidal excitation around the DC potential measured at the beginning of the
    technique. PZIR technique determines the solution resistance Ru, for one high frequency
    value, as the real part of the measured impedance. A percentage of the Ru value will
    be used to compensate next potentio techniques. It is highly recommended to not
    exceed 85% of the Ru measured value in order to avoid oscillations of the instrument.
    The Rcmp_Mode parameter will allow to specify the compensation mode for the next
    potentio techniques (only for SP-300 series).

    When used in linked techniques including loops, Ru value can change during the
    experiment. PZIR can be an ideal tool to do a dynamic ohmic drop compensation
    between repeated techniques.
    For low impedance electrochemical systems it is recommended to use GZIR instead of
    PZIR."""

    timebase = PZIR_TIMEBASE

    ecc_path = {
        DeviceFamily.VMP3 : 'pzir.ecc',
        DeviceFamily.SP300 : 'pzir4.ecc',
    }

    def unpack_data(self, bl: BioLogic, data: BLData) -> Iterable[PZIRData]:
        if bl.device_info.family == DeviceFamily.VMP3:
            yield from self._unpack_data_vmp3(bl, data)
        elif bl.device_info.family == DeviceFamily.SP300:
            yield from self._unpack_data_sp300(bl, data)
        else:
            raise ValueError("unsupported device family")

    def _unpack_data_vmp3(self, bl: BioLogic, data: BLData) -> Iterable[PZIRData]:
        for data_row in data.iter_data():
            (
                freq, Ewe_mod, I_mod, phase_Zwe, Ewe, I, _, Ece_mod,
                Ice_mod, phase_Zce, Ece, _, _, t, I_range,
            ) = data_row

            yield PZIRData(
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
                t = bl.extract_float(t),
                I_range = I_RANGE(I_range),
            )

    def _unpack_data_sp300(self, bl: BioLogic, data: BLData) -> Iterable[PZIRData]:
        for data_row in data.iter_data():
            (
                freq, Ewe_mod, I_mod, phase_Zwe, Ewe, I, _, Ece_mod,
                Ice_mod, phase_Zce, Ece, _, t,
            ) = data_row

            yield PZIRData(
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
                t = bl.extract_float(t),
                I_range=None,
            )
