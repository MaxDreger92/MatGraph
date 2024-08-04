""" BioLogic device and channel information.
| Author: Mike Werezak <mike.werezak@nrcan-rncan.gc.ca>
| Created: 2024/03/05
"""

from __future__ import annotations

from enum import Enum, auto
from datetime import date, datetime
from dataclasses import dataclass, fields
from collections.abc import Sequence, Mapping
from typing import TYPE_CHECKING

from kbio.types import (
    DEVICE,
    VMP3_FAMILY,
    VMP300_FAMILY,
    DeviceInfo as kbio_DeviceInfo,
    CHANNEL_BOARD,
    FIRMWARE,
    AMPLIFIER,
    PROG_STATE,
    I_RANGE,
    BANDWIDTH,
    ChannelInfo as kbio_ChannelInfo,
)

if TYPE_CHECKING:
    from typing import Self, Optional
    from collections.abc import Iterable

__all__ = (
    'DeviceFamily',
    'get_device_family',
    'DeviceInfo',
    'ChannelInfo',
    'format_device_info',
    'format_channel_info',
    'Json',
    'DEVICE',
    'CHANNEL_BOARD',
    'FIRMWARE',
    'AMPLIFIER',
    'PROG_STATE',
    'I_RANGE',
    'BANDWIDTH',
)


# allowed types for JSON serialization
Json = None | bool | int | float | str | Sequence['Json'] | Mapping[str, 'Json']


class DeviceFamily(Enum):
    VMP3 = auto()
    SP300 = auto()

    def __str__(self) -> str:
        return self.name


def get_device_family(model: DEVICE) -> DeviceFamily:
    """Lookup the device series for a particular device model."""
    if model not in _device_series_mapping:
        raise ValueError(f"unknown device model: {model.name}")
    return _device_series_mapping[model]

_device_series_mapping = {}
for name in VMP3_FAMILY:
    _device_series_mapping[DEVICE[name]] = DeviceFamily.VMP3
for name in VMP300_FAMILY:
    _device_series_mapping[DEVICE[name]] = DeviceFamily.SP300


DATE_FORMAT = '%Y/%m/%d'

@dataclass(frozen=True, kw_only=True)
class DeviceInfo:
    model: DEVICE
    family: DeviceFamily
    ram_size: int
    cpu: int
    num_channels: int
    num_slots: int
    firmware_version: int
    firmware_date: date
    ht_display_on: int
    num_connected_pc: int

    def __str__(self) -> str:
        return format_device_info(self)

    @property
    def fields(self) -> Iterable[str]:
        for field in fields(self):
            yield field.name

    def to_json(self) -> Json:
        return dict(
            model=self.model.name,
            family=self.family.name,
            ram_size=self.ram_size,
            cpu=self.cpu,
            num_channels=self.num_channels,
            num_slots=self.num_slots,
            firmware_version=self.firmware_version,
            firmware_date=self.firmware_date.strftime(DATE_FORMAT),
            ht_display_on=self.ht_display_on,
            num_connected_pc=self.num_connected_pc,
        )

    @classmethod
    def from_json(cls, json: dict[str, Json]) -> Self:
        firmware_date = datetime.strptime(json['firmware_date'], DATE_FORMAT).date()
        return cls(
            model=DEVICE[json['model']],
            family=DeviceFamily[json['family']],
            ram_size=json['ram_size'],
            cpu=json['cpu'],
            num_channels=json['num_channels'],
            num_slots=json['num_slots'],
            firmware_version=json['firmware_version'],
            firmware_date=firmware_date,
            ht_display_on=json['ht_display_on'],
            num_connected_pc=json['num_connected_pc'],
        )

    @classmethod
    def from_kbio(cls, src: kbio_DeviceInfo) -> Self:
        model = DEVICE(src.DeviceCode)
        firmware_date = date(src.FirmwareDate_yyyy, src.FirmwareDate_mm, src.FirmwareDate_dd)

        return cls(
            model=model,
            family=get_device_family(model),
            ram_size=src.RAMSize,
            cpu=src.CPU,
            num_channels=src.NumberOfChannels,
            num_slots=src.NumberOfSlots,
            firmware_version=src.FirmwareVersion,
            firmware_date=firmware_date,
            ht_display_on=src.HTdisplayOn,
            num_connected_pc=src.NbOfConnectedPC,
        )


@dataclass(frozen=True, kw_only=True)
class ChannelInfo:
    channel: int  # channel number
    board_version: CHANNEL_BOARD
    board_serial: int
    firmware: FIRMWARE
    firmware_version: int
    xilinx_version: int
    amplifier: AMPLIFIER
    num_amplifiers: int
    lc_board: int
    z_board: int
    mux_board: int
    gpra_board: int
    mem_size: int
    mem_filled: int
    state: PROG_STATE
    max_I_range: Optional[I_RANGE]
    min_I_range: Optional[I_RANGE]
    max_bandwidth: Optional[BANDWIDTH]
    num_techniques: int

    def __str__(self) -> str:
        return format_channel_info(self)

    @property
    def fields(self) -> Iterable[str]:
        for field in fields(self):
            yield field.name

    def is_busy(self) -> bool:
        return self.state != PROG_STATE.STOP

    def is_kernel_loaded(self) -> bool:
        return self.firmware == FIRMWARE.KERNEL  # based on kbio examples

    def to_json(self) -> Json:
        return dict(
            channel=self.channel,
            board_version=self.board_version.name,
            board_serial=self.board_serial,
            firmware=self.firmware.name,
            firmware_version=self.firmware_version,
            xilinx_version=self.xilinx_version,
            amplifier=self.amplifier.name,
            num_amplifiers=self.num_amplifiers,
            lc_board=self.lc_board,
            z_board=self.z_board,
            mux_board=self.mux_board,
            gpra_board=self.gpra_board,
            mem_size=self.mem_size,
            mem_filled=self.mem_filled,
            state=self.state.name,
            max_I_range=self.max_I_range.name,
            min_I_range=self.min_I_range.name,
            max_bandwidth=self.max_bandwidth.name,
            num_techniques=self.num_techniques,
        )

    @classmethod
    def from_json(cls, json: dict[str, Json]) -> Self:
        return cls(
            channel=json['channel'],
            board_version=CHANNEL_BOARD[json['board_version']],
            board_serial=json['board_serial'],
            firmware=FIRMWARE[json['firmware']],
            firmware_version=json['firmware_version'],
            xilinx_version=json['xilinx_version'],
            amplifier=AMPLIFIER[json['amplifier']],
            num_amplifiers=json['num_amplifiers'],
            lc_board=json['lc_board'],
            z_board=json['z_board'],
            mux_board=json['mux_board'],
            gpra_board=json['gpra_board'],
            mem_size=json['mem_size'],
            mem_filled=json['mem_filled'],
            state=PROG_STATE[json['state']],
            max_I_range=I_RANGE[json['max_I_range']],
            min_I_range=I_RANGE[json['min_I_range']],
            max_bandwidth=BANDWIDTH[json['max_bandwidth']],
            num_techniques=json['num_techniques'],
        )

    @classmethod
    def from_kbio(cls, src: kbio_ChannelInfo) -> Self:
        firmware = FIRMWARE(src.FirmwareCode)

        max_I_range = I_RANGE(src.MaxIRange) if src.MaxIRange else None
        min_I_range = I_RANGE(src.MinIRange) if src.MinIRange else None
        max_bandwidth = BANDWIDTH(src.MaxBandwidth) if src.MaxBandwidth else None

        return cls(
            channel=src.Channel+1,
            board_version=CHANNEL_BOARD(src.BoardVersion),
            board_serial=src.BoardSerialNumber,
            firmware=firmware,
            firmware_version=src.FirmwareVersion,
            xilinx_version=src.XilinxVersion,
            amplifier=AMPLIFIER(src.AmpCode),
            num_amplifiers=src.NbAmps,
            lc_board=src.Lcboard,
            z_board=src.Zboard,
            mux_board=src.MUXboard,
            gpra_board=src.GPRAboard,
            mem_size=src.MemSize,
            mem_filled=src.MemFilled,
            state=PROG_STATE(src.State),
            max_I_range=max_I_range,
            min_I_range=min_I_range,
            max_bandwidth=max_bandwidth,
            num_techniques=src.NbOfTechniques,
        )

## Formatting detailed info strings
## Adapted from kbio

def _pp_plural (nb: int, label: str, *, num: bool = True, nothing: str = '') :
    """Return a user friendly version of an ordinal and a label.

       num is used to force a numeral instead of 'no' or 'one',
       nothing is what to say if there is nothing
    """
    if nb == 0:
        return nothing if nothing else f"{0 if num else 'no'} {label}"
    if nb == 1:
        return f"{1 if num else 'one'} {label}"
    return f"{nb} {label}s"

def format_device_info(info: DeviceInfo) -> str:
    fragments = list()

    fragments.append(
        f"{info.model.name} {info.ram_size}MB, CPU={info.cpu}"
        f", {_pp_plural(info.num_channels,'channel')}"
        f", {_pp_plural(info.num_slots,'slot')}"
    )
    fragments.append(
        f"Firmware: v{info.firmware_version/100:.2f} "
        f"{info.firmware_date.strftime('%Y/%m/%d')}"
    )

    cnx = info.num_connected_pc
    fragments.append(
        f"{_pp_plural(cnx,'connection')}"
        f", HTdisplay {'on' if info.ht_display_on else 'off'}")

    return '\n'.join(fragments)

def format_channel_info(info: ChannelInfo) -> str:
    fragments = list()

    if info.firmware == FIRMWARE.NONE:
        fragments.append(f"{info.board_version.name} board, no firmware")
    elif info.firmware == FIRMWARE.KERNEL:
        fragments.append(f"Channel: {info.channel}")
        fragments.append(f"{info.board_version.name} board, S/N {info.board_serial}")
        fragments.append(f"{'has a' if info.lc_board else 'no'} LC head")
        fragments.append(f"{'with' if info.z_board else 'no'} EIS capabilities")
        fragments.append(_pp_plural(info.num_techniques,"technique"))
        fragments.append(f"State: {info.state.name}")

        if info.num_amplifiers:
            fragments.append(f"{info.amplifier.name} amplifier (x{info.num_amplifiers})")
        else:
            fragments.append(f"no amplifiers")

        fragments.append(f"IRange: [{info.min_I_range.name}, {info.max_I_range.name}]")
        fragments.append(f"MaxBandwidth: {info.max_bandwidth.name}")

        if info.mem_size:
            fragments.append(
                f"Memory: {info.mem_size/1024:.1f}KB"
                f" ({(info.mem_filled/info.mem_size*100.):.2f}% filled)"
            )
        else :
            fragments.append("Memory: 0KB")

        version = info.firmware_version/1000
        vstr = f"{version*10:.2f}" if version < 1. else f"{version:.3f}"

        fragments.append(
            f"{info.firmware.name} (v{vstr}), "
            f"FPGA ({info.xilinx_version:04X})"
        )

    else:
        version = info.firmware_version/100
        vstr = f"{version*10:.2f}" if version < 1. else f"{version:.3f}"
        fragments.append(
            f"{info.firmware.name} (v{vstr}), "
            f"FPGA ({info.xilinx_version:04X})"
        )

    return '\n'.join(fragments)
