"""
| Author: Mike Werezak <mike.werezak@nrcan-rncan.gc.ca>
| Created: 2024/03/04
"""

from __future__ import annotations

from datetime import datetime
from dataclasses import dataclass, fields
from typing import TYPE_CHECKING

from biologic.deviceinfo import DeviceInfo, ChannelInfo

if TYPE_CHECKING:
    from typing import Optional, Self
    from collections.abc import Iterable
    from biologic.deviceinfo import Json

__all__ = (
    'TechniqueMetadata',
)


DATETIME_FORMAT = '%Y/%m/%d %H:%M:%S%z'

@dataclass(frozen=True, kw_only=True)
class TechniqueMetadata:
    """Contains metadata about a technique run."""

    eclab_version: str
    device_info: DeviceInfo
    channel_info: ChannelInfo
    channel: int
    start_time: Optional[datetime]
    stop_time: Optional[datetime]
    status: str

    @property
    def fields(self) -> Iterable[str]:
        for field in fields(self):
            yield field.name

    def to_json(self) -> Json:
        json = dict(
            eclab_version = self.eclab_version,
            device_info = self.device_info.to_json(),
            channel_info = self.channel_info.to_json(),
            channel = self.channel,
            status = self.status,
        )
        if self.start_time is not None:
            json['start_time'] = self.start_time.strftime(DATETIME_FORMAT)
        if self.stop_time is not None:
            json['stop_time'] = self.stop_time.strftime(DATETIME_FORMAT)
        return json

    @classmethod
    def from_json(cls, json: dict[str, Json]) -> Self:
        start_time = json.get('start_time')
        if start_time is not None:
            start_time = datetime.strptime(start_time, DATETIME_FORMAT)

        stop_time = json.get('stop_time')
        if stop_time is not None:
            stop_time = datetime.strptime(stop_time, DATETIME_FORMAT)

        return cls(
            eclab_version = json['eclab_version'],
            device_info = DeviceInfo.from_json(json['device_info']),
            channel_info = ChannelInfo.from_json(json['channel_info']),
            channel = json['channel'],
            start_time = start_time,
            stop_time = stop_time,
            status = json['status'],
        )
