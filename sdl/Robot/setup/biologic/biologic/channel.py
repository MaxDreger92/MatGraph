"""
| Author: Mike Werezak <mike.werezak@nrcan-rncan.gc.ca>
| Created: 2024/02/23
"""

from __future__ import annotations

import time
import logging
from threading import Thread, Lock
from typing import TYPE_CHECKING, NamedTuple

from kbio.api import KBIO_api
from kbio.tech import TECH_ID
from kbio.types import CurrentValues, DataInfo, DataBuffer, PROG_STATE

from biologic.runner import TechniqueRunner
from biologic.deviceinfo import ChannelInfo

if TYPE_CHECKING:
    from typing import Optional
    from collections.abc import Generator, Iterable, Sequence
    from biologic import BioLogic
    from biologic.technique import Technique

__all__ = (
    'BLData',
    'Channel',
    'ChannelStopped',
)


_log = logging.getLogger(__name__)


class ChannelStopped(Exception): pass


class BLData(NamedTuple):
    current_values: CurrentValues
    data_info: DataInfo
    data_record: DataBuffer

    @property
    def prog_state(self) -> PROG_STATE:
        return PROG_STATE(self.current_values.State)

    @property
    def tech_index(self) -> int:
        return self.data_info.TechniqueIndex

    @property
    def tech_id(self) -> TECH_ID:
        return TECH_ID(self.data_info.TechniqueID)

    @property
    def start_time(self) -> float:
        return self.data_info.StartTime

    def convert_time(self, t_high: int, t_low: int) -> float:
        """Common time conversion calculation."""
        t_rel = (t_high << 32) + t_low
        return self.current_values.TimeBase * t_rel

    def iter_data(self) -> Iterable[Sequence[int]]:
        num_rows = self.data_info.NbRows
        row_len = self.data_info.NbCols
        for offset in range(0, num_rows*row_len, row_len):
            yield self.data_record[offset:offset+row_len]


class Channel:
    """A potentiostat channel."""

    _gen: Optional[Generator]

    def __init__(self, bl: BioLogic, chan_id: int):
        self._bl = bl
        self._chan = chan_id

        self._log = logging.LoggerAdapter(bl.log, dict(chan=self._chan))
        self.message_level = logging.INFO  #: the logging level to use for channel messages

        self._msg_thread = Thread(None, self._message_listener)
        self._msg_stop = False

        self._gen = None  # a generator used to pump data for the currently running technique
        self._runner = None
        self._lock = Lock()

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}: id={self._bl.id}, chan={self._chan}>'

    def __str__(self) -> str:
        return f"channel #{self._chan}"

    def __del__(self) -> None:
        self.stop_message_listener()

    @property
    def bl(self) -> BioLogic:
        return self._bl

    @property
    def num(self) -> int:
        """Channel number."""
        return self._chan

    @property
    def log(self) -> logging.Logger:
        # noinspection PyTypeChecker
        return self._log

    @property
    def _api(self) -> KBIO_api:
        return self._bl.api

    @property
    def _id(self) -> int:
        return self._bl.id

    def get_info(self) -> ChannelInfo:
        """Query channel info."""
        raw_info = self._api.GetChannelInfo(self._id, self._chan)
        return ChannelInfo.from_kbio(raw_info)

    def is_plugged(self) -> bool:
        """Check if the channel is plugged in."""
        return self._api.IsChannelPlugged(self._id, self._chan)

    def stop(self) -> None:
        """Stop the channel.
        This will cause any active TechniqueRunner to fail with a ChannelStopped exception."""
        with self._lock:
            info = self.get_info()
            if info.state == PROG_STATE.STOP:
                return

            self._close_gen()
            self._api.StopChannel(self.bl.id, self._chan)

            self._gen = None
            self._runner = None

    def is_busy(self) -> bool:
        info = self.get_info()
        return info.is_busy()

    def is_active(self, runner: TechniqueRunner) -> bool:
        """Return True if the channel is running with the given runner instance."""
        with self._lock:
            info = self.get_info()
            if info.state == PROG_STATE.RUN:
                return self._runner is runner
        return False

    def run_techniques(self, techs: Sequence[Technique]) -> TechniqueRunner:
        """Start the technique and return a TechniqueRunner."""
        if not self.is_plugged():
            raise RuntimeError("channel is not connected")

        with self._lock:
            info = self.get_info()
            if info.state != PROG_STATE.STOP:
                raise RuntimeError("channel is busy")

            for tech in techs:
                if not tech.is_device_supported(self._bl.device_info):
                    raise ValueError(f"device does not support technique: {tech}")

            self._check_limits(info, techs)

            self._load_techniques(techs)
            self._api.StartChannel(self._bl.id, self._chan)

            if self._gen is not None:
                self._gen.close()
            self._gen = self._get_data()
            self._runner = TechniqueRunner(self, techs, self._gen)
            return self._runner

    def _load_techniques(self, techs: Sequence[Technique]) -> None:
        last_idx = len(techs) - 1
        for idx, tech in enumerate(techs):
            self._load_technique(tech, idx == 0, idx == last_idx)

    def _load_technique(self, tech: Technique, first: bool, last: bool) -> None:
        errors = list(tech.validate(self._bl.device_info))
        if len(errors) > 0:
            raise ExceptionGroup("technique parameters failed validation", errors)

        ecc_parms = tech.pack_parameters(self._bl)
        ecc_file = tech.get_ecc(self._bl)
        self._api.LoadTechnique(self._bl.id, self._chan, ecc_file, ecc_parms, first, last)

    @staticmethod
    def _check_limits(info: ChannelInfo, techs: Iterable[Technique]) -> None:
        if not info.is_kernel_loaded():
            raise RuntimeError("kernel must be loaded before any techniques can run")

        if info.max_I_range < info.min_I_range:
            raise ValueError(f"invalid I_range limits: {info.min_I_range} > {info.max_I_range}")

        for tech in techs:
            params = tech.param_values
            if params.I_range > info.max_I_range:
                raise ValueError(f"channel can't support {params.I_range}, max I_range={info.max_I_range}")
            if params.I_range < info.min_I_range:
                raise ValueError(f"channel can't support {params.I_range}, min I_range={info.max_I_range}")
            if params.bandwidth > info.max_bandwidth:
                raise ValueError(f"channel can't support {params.bandwidth}, max bandwidth={info.max_bandwidth}")

    def _get_data(self) -> Generator[BLData]:
        while True:
            yield BLData(*self._api.GetData(self._bl.id, self._chan))

    def _close_gen(self) -> None:
        if self._gen is None:
            return

        try:
            self._gen.throw(ChannelStopped(f"{self} was stopped"))
        except StopIteration:
            pass

        try:
            self._gen.close()
        except ChannelStopped:
            pass

        self._gen = None

    def start_message_listener(self) -> None:
        """Start the message listener thread, which will log informational messages emitted by
        the potentiostat channel. This is normally called by the connect() function when the
        potentiostat is connected."""
        if not self._msg_thread.is_alive():
            self._msg_thread.start()

    def stop_message_listener(self) -> None:
        """Stop the message listener thread. This is normally called by the close() method when
        the potentiostat is closed."""
        if not self._msg_thread.is_alive():
            return

        self._msg_stop = True
        self._msg_thread.join(5.0)
        if self._msg_thread.is_alive():
            self._log.warning("Timeout expired while waiting for message listener to exit.")

    _msg_loop_interval = 1.0
    def _message_listener(self) -> None:
        self._log.debug("Starting message listener.")

        errors = 0
        while errors < 10 and not self._msg_stop:
            try:
                msg = self._api.GetMessage(self._id, self._chan)
                while msg:
                    self._log.log(self.message_level, msg)
                    msg = self._api.GetMessage(self._id, self._chan)
            except:
                self._log.error("Unhandled exception raised from message listener!", exc_info=True)
                errors += 1
            else:
                errors = 0

            time.sleep(self._msg_loop_interval)

        self._log.debug("Message listener stopped.")
