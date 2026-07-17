"""Alarm and AlarmClock class definitions."""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Set

from constants import WEEKDAY_NAMES


@dataclass
class Alarm:
  id: int
  title: str
  hour: int
  minute: int
  weekdays: Set[int] = field(default_factory=set)
  enabled: bool = True
  snooze_until: Optional[datetime] = None
  last_rung_at: Optional[datetime] = None

  @property
  def is_repeating(self) -> bool:
    return bool(self.weekdays)

  def time_label(self) -> str:
    return f"{self.hour:02d}:{self.minute:02d}"

  def weekdays_label(self) -> str:
    if not self.weekdays:
      return "Once"
    return ", ".join(WEEKDAY_NAMES[d] for d in sorted(self.weekdays))


class AlarmClock:
  def __init__(self) -> None:
    self.alarms: list[Alarm] = []
    self._next_id = 1
    self._lock = threading.Lock()

  def _allocate_id(self) -> int:
    alarm_id = self._next_id
    self._next_id += 1
    return alarm_id

  def find_alarm(self, alarm_id: int) -> Optional[Alarm]:
    for alarm in self.alarms:
      if alarm.id == alarm_id:
        return alarm
    return None
