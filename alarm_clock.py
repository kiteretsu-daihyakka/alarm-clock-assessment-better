"""IST-based CLI alarm clock with snooze and weekday repeat."""

from __future__ import annotations

import sys
import threading
import time
from datetime import timedelta
from typing import Optional, Set

from helpers import (
  already_rung_this_minute,
  get_current_time_ist,
  matches_weekday,
  parse_time,
  parse_weekdays,
  print_current_time_ist,
)
from models import Alarm, AlarmClock


def set_alarm(
  clock: AlarmClock,
  title: str,
  hour: int,
  minute: int,
  weekdays: Optional[Set[int]] = None,
) -> Alarm:
  """Create and register a new alarm."""
  alarm = Alarm(
    id=clock._allocate_id(),
    title=title.strip() or "Alarm",
    hour=hour,
    minute=minute,
    weekdays=weekdays or set(),
    enabled=True,
  )

  with clock._lock:
    clock.alarms.append(alarm)

  repeat_label = alarm.weekdays_label()
  print(
    f"Alarm #{alarm.id} set: '{alarm.title}' at {alarm.time_label()} "
    f"({repeat_label})"
  )
  return alarm


def list_alarms(clock: AlarmClock) -> list[Alarm]:
  """Print all alarms and return them."""
  with clock._lock:
    alarms = list(clock.alarms)

  if not alarms:
    print("No alarms set.")
    return alarms

  print("\n--- Alarms ---")
  for alarm in alarms:
    status = "enabled" if alarm.enabled else "disabled"
    snooze = ""
    if alarm.snooze_until:
      snooze = f" | snoozed until {alarm.snooze_until.strftime('%H:%M:%S')}"
    print(
      f"#{alarm.id:>2} | {alarm.time_label()} | {alarm.title} | "
      f"{alarm.weekdays_label()} | {status}{snooze}"
    )
  print()
  return alarms


def disable_alarm(clock: AlarmClock, alarm_id: int) -> bool:
  """Disable an alarm by id."""
  with clock._lock:
    alarm = clock.find_alarm(alarm_id)
    if alarm is None:
      print(f"Alarm #{alarm_id} not found.")
      return False

    alarm.enabled = False
    alarm.snooze_until = None
    print(f"Alarm #{alarm_id} disabled.")
    return True


def snooze_alarm(clock: AlarmClock, alarm_id: int, minutes: int = 5) -> bool:
  """Snooze an alarm for the given number of minutes."""
  if minutes <= 0:
    raise ValueError("Snooze minutes must be greater than 0.")

  with clock._lock:
    alarm = clock.find_alarm(alarm_id)
    if alarm is None:
      print(f"Alarm #{alarm_id} not found.")
      return False

    now = get_current_time_ist()
    base = alarm.snooze_until if alarm.snooze_until and alarm.snooze_until > now else now
    alarm.snooze_until = base + timedelta(minutes=minutes)
    alarm.enabled = True
    print(
      f"Alarm #{alarm_id} snoozed until "
      f"{alarm.snooze_until.strftime('%H:%M:%S')} IST."
    )
    return True


def check_due_alarms(clock: AlarmClock) -> list[Alarm]:
  """Return alarms that should ring right now."""
  now = get_current_time_ist()
  due: list[Alarm] = []

  with clock._lock:
    for alarm in clock.alarms:
      if not alarm.enabled:
        continue

      if alarm.snooze_until:
        if now >= alarm.snooze_until.replace(second=0, microsecond=0):
          if now.minute == alarm.snooze_until.minute and now.hour == alarm.snooze_until.hour:
            if not already_rung_this_minute(alarm, now):
              due.append(alarm)
        continue

      if now.hour != alarm.hour or now.minute != alarm.minute:
        continue

      if not matches_weekday(alarm, now):
        continue

      if already_rung_this_minute(alarm, now):
        continue

      due.append(alarm)

  return due


def ring_alarm(alarm: Alarm) -> None:
  """Alert the user that an alarm is ringing."""
  banner = "=" * 48
  print(f"\n{banner}")
  print(f"ALARM: {alarm.title}")
  print(f"Time: {alarm.time_label()} IST")
  print(banner)

  try:
    if sys.platform == "win32":
      import winsound

      for _ in range(3):
        winsound.Beep(1000, 500)
        time.sleep(0.15)
    else:
      print("\a", end="", flush=True)
  except Exception:
    print("[Beep unavailable]")


def _mark_alarm_rung(clock: AlarmClock, alarm: Alarm) -> None:
  now = get_current_time_ist()
  with clock._lock:
    alarm.last_rung_at = now
    alarm.snooze_until = None

    if not alarm.is_repeating:
      alarm.enabled = False
      print(f"One-shot alarm #{alarm.id} auto-disabled.")


def _prompt_alarm_action(clock: AlarmClock, alarm: Alarm) -> None:
  while True:
    choice = input("Snooze for 5 min? [Y/n]: ").strip().lower()
    if choice in ("", "y", "yes"):
      snooze_alarm(clock, alarm.id, minutes=5)
      return
    if choice in ("n", "no"):
      if alarm.is_repeating:
        print(f"Alarm #{alarm.id} dismissed until next scheduled time.")
      else:
        disable_alarm(clock, alarm.id)
      return
    print("Please enter Y or N.")


def alarm_checker_loop(clock: AlarmClock, stop_event: threading.Event) -> None:
  """Background loop that checks and rings due alarms."""
  while not stop_event.is_set():
    due_alarms = check_due_alarms(clock)
    for alarm in due_alarms:
      ring_alarm(alarm)
      _mark_alarm_rung(clock, alarm)
      _prompt_alarm_action(clock, alarm)
    stop_event.wait(1)


def prompt_set_alarm(clock: AlarmClock) -> None:
  """Interactive prompt to create a new alarm."""
  title = input("Alarm title: ").strip() or "Alarm"

  while True:
    time_value = input("Alarm time (HH:MM): ").strip()
    try:
      hour, minute = parse_time(time_value)
      break
    except ValueError as exc:
      print(exc)

  weekdays_value = input(
    "Repeat on weekdays (mon,tue,... or 0-6, blank for once): "
  ).strip()

  try:
    weekdays = parse_weekdays(weekdays_value)
    set_alarm(clock, title=title, hour=hour, minute=minute, weekdays=weekdays)
  except ValueError as exc:
    print(exc)


def prompt_disable_alarm(clock: AlarmClock) -> None:
  list_alarms(clock)
  value = input("Alarm id to disable: ").strip()
  if not value.isdigit():
    print("Please enter a numeric alarm id.")
    return
  disable_alarm(clock, int(value))


def prompt_snooze_alarm(clock: AlarmClock) -> None:
  list_alarms(clock)
  value = input("Alarm id to snooze: ").strip()
  if not value.isdigit():
    print("Please enter a numeric alarm id.")
    return

  minutes_value = input("Snooze minutes [5]: ").strip() or "5"
  if not minutes_value.isdigit():
    print("Please enter a numeric snooze duration.")
    return

  try:
    snooze_alarm(clock, int(value), minutes=int(minutes_value))
  except ValueError as exc:
    print(exc)


def print_menu() -> None:
  print("\n=== IST Alarm Clock ===")
  print("1. Set alarm")
  print("2. Current time (IST)")
  print("3. List alarms")
  print("4. Disable alarm")
  print("5. Snooze alarm")
  print("6. Quit")


def main() -> None:
  clock = AlarmClock()
  stop_event = threading.Event()

  checker = threading.Thread(
    target=alarm_checker_loop,
    args=(clock, stop_event),
    daemon=True,
    name="alarm-checker",
  )
  checker.start()

  print("Welcome to the IST Alarm Clock.")
  print("Alarms are checked every second in the background.")

  try:
    while True:
      print_menu()
      choice = input("Choose an option: ").strip()

      if choice == "1":
        prompt_set_alarm(clock)
      elif choice == "2":
        print_current_time_ist()
      elif choice == "3":
        list_alarms(clock)
      elif choice == "4":
        prompt_disable_alarm(clock)
      elif choice == "5":
        prompt_snooze_alarm(clock)
      elif choice == "6":
        print("Goodbye.")
        break
      else:
        print("Invalid choice. Please select 1-6.")
  except KeyboardInterrupt:
    print("\nGoodbye.")
  finally:
    stop_event.set()
    checker.join(timeout=2)


if __name__ == "__main__":
  main()
