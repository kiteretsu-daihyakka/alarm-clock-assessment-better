"""Shared constants for the alarm clock."""

from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")

WEEKDAY_NAMES = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")

WEEKDAY_ALIASES = {
  "mon": 0,
  "monday": 0,
  "tue": 1,
  "tues": 1,
  "tuesday": 1,
  "wed": 2,
  "wednesday": 2,
  "thu": 3,
  "thur": 3,
  "thurs": 3,
  "thursday": 3,
  "fri": 4,
  "friday": 4,
  "sat": 5,
  "saturday": 5,
  "sun": 6,
  "sunday": 6,
}
