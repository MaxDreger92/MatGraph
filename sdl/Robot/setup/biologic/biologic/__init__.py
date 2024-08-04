""" BioLogic multi-channel potentiostat driver API.
| Author: Mike Werezak <mike.werezak@nrcan-rncan.gc.ca>
| Created: 2024/02/22
"""

from __future__ import annotations

import os.path
import logging
from typing import TYPE_CHECKING

from kbio import ECLIB_NAME, BLFIND_NAME
from kbio.api import KBIO_api, KBIOError
from kbio.types import (
    DEVICE,
    I_RANGE,
    E_RANGE,
    BANDWIDTH,
    ERROR,
)

from biologic.channel import Channel
from biologic.deviceinfo import (
    DeviceFamily, DeviceInfo, ChannelInfo, format_device_info, format_channel_info,
)

if TYPE_CHECKING:
    from typing import Any, Optional
    from collections.abc import Iterable, Collection
    from biologic.technique import Technique

__all__ = (
    'connect',
    'get_kbio_api',
    'BioLogic',
    'DeviceFamily',
    'DeviceInfo',
    'Channel',
    'ChannelInfo',
    'KBIOError',
    'BioLogicError',
    'DEVICE',
    'I_RANGE',
    'E_RANGE',
    'BANDWIDTH',
    'ERROR',
)


_log = logging.getLogger(__name__)

class BioLogicError(Exception): pass


def get_kbio_api(eclab_path: Optional[str]) -> KBIO_api:
    if eclab_path is not None:
        eclib_file = os.path.join(eclab_path, ECLIB_NAME)
        blfind_file = os.path.join(eclab_path, BLFIND_NAME)
        return KBIO_api(eclib_file, blfind_file)
    return KBIO_api()


def connect(
        address: str, *,
        timeout: int = 5,
        force_load: bool = False,
        eclab_path: Optional[str] = None,
    ) -> BioLogic:
    """Connect to a BioLogic device.
    You can use the blfind utility to find addresses that can be used with this function.
    The timeout parameter will set the timeout for all API calls that access the network."""

    api = get_kbio_api(eclab_path)

    version = api.GetLibVersion()
    _log.info(f"EcLib version: {version}")

    _log.info(f"Connecting to {address}...")
    dev_id, raw_info = api.Connect(address, int(timeout))
    if not api.TestConnection(dev_id):
        raise RuntimeError("failed to connect to instrument")

    dev_info = DeviceInfo.from_kbio(raw_info)
    _log.info(f"Device info:\n{dev_info}")

    bl = BioLogic(address, api, dev_id, dev_info, force_load=force_load)
    bl.log.info("Device connected.")

    for chan in bl.channels():
        chan.start_message_listener()

    return bl


class BioLogic:
    """Represents a BioLogic potentiostat device."""

    _chan: dict[int, Channel]

    _fw_name = {
        DeviceFamily.VMP3  : 'kernel.bin',
        DeviceFamily.SP300 : 'kernel4.bin',
    }

    _fpga_name = {
        DeviceFamily.VMP3  : 'Vmp_ii_0437_a6.xlx',
        DeviceFamily.SP300 : 'Vmp_iv_0395_aa.xlx',
    }

    api: KBIO_api
    id: int
    device_info: DeviceInfo
    api_version: str

    def __init__(
            self, address: str, api: KBIO_api, device_id: int, device_info: DeviceInfo, *,
            fw_path: Optional[str] = None,
            fpga_path: Optional[str] = None,
            force_load: bool = False,
    ):
        self.api = api
        self.id = device_id
        self.device_info = device_info
        self.api_version = api.GetLibVersion()

        self._log = logging.LoggerAdapter(_log, dict(address=address, dev_id=device_id))

        ch_numbers = ( i+1 for i in range(device_info.num_channels) )
        self._chan = { n : Channel(self, n) for n in ch_numbers }

        load_channels = [
            chan.num for chan in self._chan.values()
            if force_load or not chan.get_info().is_kernel_loaded()
        ]
        if len(load_channels) > 0:
            if fw_path is None:
                fw_path = self._fw_name[device_info.family]
            if fpga_path is None:
                fpga_path = self._fpga_name[device_info.family]
            self._load_firmware(load_channels, fw_path, fpga_path, force=force_load)

        self._test_all_channels()

    def _load_firmware(self, channels: Collection[int], fw_path: str, fpga_path: str, force: bool = False) -> None:
        self._log.info(f"Load firmware on channel(s): {','.join(str(n) for n in channels)}")
        self._log.debug(f"Load firmware={fw_path}, fpga={fpga_path}, force={force}.")
        channel_map = [ ch_num in channels for ch_num in sorted(self._chan.keys()) ]
        self.api.LoadFirmware(self.id, channel_map, firmware=fw_path, fpga=fpga_path, silent=True, force=force)

    def _test_all_channels(self) -> None:
        self._log.info("Testing device channels...")
        errors = []
        for ch_num, chan in self._chan.items():
            try:
                chan_info = chan.get_info()
            except Exception as error:
                self._log.error(f"Failed to read channel info for Channel #{ch_num}.")
                errors.append(error)
            else:
                self._log.debug(f"Channel info:\n{format_channel_info(chan_info)}")

        if len(errors) > 0:
            raise ExceptionGroup("could not read all channel info, channel firmware is probably corrupted", errors)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}: id={self.id}>'

    def __del__(self) -> None:
        self.close()

    def __enter__(self) -> BioLogic:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> Any:
        self.close()
        return None

    @property
    def log(self) -> logging.Logger:
        # noinspection PyTypeChecker
        return self._log

    @property
    def channel_numbers(self) -> Collection[int]:
        return self._chan.keys()

    def get_channel(self, chan_num: int) -> Channel:
        chan = self._chan.get(chan_num)
        if chan is None:
            raise ValueError(f"invalid channel number: {chan_num}")
        return chan

    def channels(self) -> Iterable[Channel]:
        return self._chan.values()

    def is_connected(self) -> bool:
        return self.api.TestConnection(self.id)

    def close(self) -> None:
        """Disconnect the potentiostat."""
        for chan in self._chan.values():
            chan.stop_message_listener()

        if self.is_connected():
            self.api.Disconnect(self.id)
            self.log.info("Connection closed.")

    ## Helper for implementing Technique subclasses
    def extract_float(self, vi: Any) -> float:
        """Perform data conversion using BL_ConvertNumericIntoSingle"""
        return self.api.ConvertNumericIntoSingle(vi)