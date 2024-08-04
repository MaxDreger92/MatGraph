"""
| Author: Mike Werezak <mike.werezak@nrcan-rncan.gc.ca>
| Created: 2024/02/29
"""

from __future__ import annotations

from enum import Enum
from datetime import datetime
from collections.abc import Iterable
from typing import TYPE_CHECKING, NamedTuple

from kbio.tech import TECH_ID
from kbio.types import PROG_STATE

from biologic.technique import Technique
from biologic.metadata import TechniqueMetadata

if TYPE_CHECKING:
    from typing import Optional
    from collections.abc import Iterator, Generator, Sequence
    from biologic.channel import Channel, BLData
    from biologic.data import TechniqueData


__all__ = (
    'RunState',
    'IndexData',
    'Signal',
    'TechniqueRunner',
)


class RunState(Enum):
    """Indicates the status of a run technique."""
    Init = 'INIT'
    Running = 'RUNNING'
    Paused = 'PAUSED'
    Complete = 'COMPLETE'
    Error = 'ERROR'
    Unknown = 'UNKNOWN'


class IndexData(NamedTuple):
    tech_index: int
    data: TechniqueData


class Signal:
    def __init__(self, name: str):
        self.name = name
    def __eq__(self, other) -> bool:
        if isinstance(other, Signal):
            return self.name == other.name
        return NotImplemented
    def __bool__(self) -> bool:
        return False
    def __str__(self) -> str:
        return self.name
    def __repr__(self) -> str:
        return f'{self.__class__.__qualname__}({self.name!r})'


class TechniqueRunner(Iterable):
    """Manage a running technique."""

    #: yielded by the TechniqueRunner to indicate that the channel is paused
    Paused = Signal('Paused')

    #: yielded when there is no additional data and the client can poll less frequently
    DataWait = Signal('DataWait')

    _last_state: Optional[PROG_STATE]
    _start_time: Optional[datetime]
    _stop_time: Optional[datetime]

    def __init__(self, chan: Channel, techs: Sequence[Technique], gen: Generator[BLData], start_time: Optional[datetime] = None):
        self._chan = chan
        self._bl = chan.bl
        self._api = chan.bl.api
        self._techs = techs
        self._gen = gen

        self._last_state = None
        self._error = None
        self.start_time = start_time or datetime.now().astimezone()
        self.stop_time = None

    @property
    def techniques(self) -> Sequence[Technique]:
        return self._techs

    @property
    def state(self) -> RunState:
        """Get the status of the run technique."""
        if self._error is not None:
            return RunState.Error
        if self._last_state is None:
            return RunState.Init
        if self._last_state == PROG_STATE.RUN:
            return RunState.Running
        if self._last_state == PROG_STATE.PAUSE:
            return RunState.Paused
        if self._last_state == PROG_STATE.STOP:
            return RunState.Complete
        return RunState.Unknown

    @property
    def exception(self) -> Optional[BaseException]:
        """Holds the last error raised while iterating, or None."""
        return self._error

    def __iter__(self) -> Iterator[Signal | IndexData]:
        return self._iter_data()

    def stop(self) -> None:
        """Stop the currently running technique."""
        if self._chan.is_active(self):
            self._chan.stop()

    def _iter_data(self) -> Iterator[Signal | IndexData]:
        """An iterator that can be used to control the flow of data collection."""
        try:
            while True:
                data = next(self._gen)
                self._last_state = data.prog_state

                if data.tech_id != TECH_ID.NONE:
                    tech_idx = data.tech_index
                    try:
                        tech = self._techs[tech_idx]
                    except IndexError:
                        self._chan.log.warning(f"invalid technique index: {tech_idx}")
                        continue

                    if data.tech_id != tech.tech_id:
                        self._chan.log.warning(f"technique ID mismatch: {data.tech_id} != {tech.tech_id}")
                        continue

                    for result_data in tech.unpack_data(self._chan.bl, data):
                        yield IndexData(tech_idx, result_data)

                elif self._last_state == PROG_STATE.STOP:
                    break

                elif self._last_state == PROG_STATE.PAUSE:
                    yield self.Paused
                else:
                    yield self.DataWait

        except BaseException as error:
            self._error = error
            self.stop()
            raise
        finally:
            self.stop_time = datetime.now().astimezone()
            self._gen.close()

    def get_metadata(self) -> TechniqueMetadata:
        """Get metadata about the run, such as start/stop time, device and channel info."""
        return TechniqueMetadata(
            eclab_version=self._bl.api_version,
            device_info=self._bl.device_info,
            channel_info=self._chan.get_info(),
            channel=self._chan.num,
            start_time=self.start_time,
            stop_time=self.stop_time,
            status=self.state.value,
        )
