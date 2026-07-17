"""Shared helper functions for the alarm clock."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Set

from constants import IST, WEEKDAY_ALIASES

if TYPE_CHECKING:
  from models import Alarm


def get_current_time_ist() -> datetime:
  """Return the current time in IST."""
  return datetime.now(IST)


def print_current_time_ist() -> datetime:
  """Print and return the current time in IST."""
  now = get_current_time_ist()
  print(f"Current time (IST): {now.strftime('%A, %d %b %Y %H:%M:%S')}")
  return now


def parse_time(value: str) -> tuple[int, int]:
  """Parse HH:MM into hour and minute."""
  parts = value.strip().split(":")
  if len(parts) != 2:
    raise ValueError("Time must be in HH:MM format.")

  hour = int(parts[0])
  minute = int(parts[1])

  if not (0 <= hour <= 23 and 0 <= minute <= 59):
    raise ValueError("Hour must be 0-23 and minute must be 0-59.")

  return hour, minute


def parse_weekdays(value: str) -> Set[int]:
  """Parse weekday input like 'mon,tue' or '0,1,2'."""
  cleaned = value.strip()
  if not cleaned:
    return set()

  weekdays: Set[int] = set()
  for token in cleaned.replace(";", ",").split(","):
    part = token.strip().lower()
    if not part:
      continue

    if part.isdigit():
      day = int(part)
      if day < 0 or day > 6:
        raise ValueError("Weekday numbers must be between 0 (Mon) and 6 (Sun).")
      weekdays.add(day)
      continue

    if part not in WEEKDAY_ALIASES:
      raise ValueError(f"Unknown weekday: {token.strip()}")

    weekdays.add(WEEKDAY_ALIASES[part])

  return weekdays


def matches_weekday(alarm: Alarm, now: datetime) -> bool:
  """Return True if the alarm should run on this weekday."""
  if not alarm.weekdays:
    return True
  return now.weekday() in alarm.weekdays


def already_rung_this_minute(alarm: Alarm, now: datetime) -> bool:
  """Return True if the alarm already rang in the current minute."""
  if alarm.last_rung_at is None:
    return False
  return alarm.last_rung_at.strftime("%Y-%m-%d %H:%M") == now.strftime("%Y-%m-%d %H:%M")
