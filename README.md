# IST Alarm Clock (CLI)

A simple Python command-line alarm clock using Indian Standard Time (IST).

## Requirements

- Python 3.9+

No external packages required.

## Run

```bash
cd alarm-clock
python alarm_clock.py
```

## Layout

- `constants.py` — IST timezone and weekday constants
- `helpers.py` — time/parsing helpers
- `models.py` — `Alarm` and `AlarmClock` classes
- `alarm_clock.py` — feature functions and CLI menu

## Features

- Set alarm with title and time (`HH:MM`)
- Show current IST time
- List all alarms
- Disable an alarm
- Snooze an alarm (default 5 minutes)
- Repeat alarms on selected weekdays (`mon,tue,wed` or `0,1,2`)
- Background checker rings due alarms automatically

## Weekday format

- Names: `mon`, `tue`, `wed`, `thu`, `fri`, `sat`, `sun`
- Numbers: `0` = Monday through `6` = Sunday
- Leave blank for a one-shot alarm (auto-disables after ringing)

## Example

```
1. Set alarm
Alarm title: Morning standup
Alarm time (HH:MM): 09:30
Repeat on weekdays (mon,tue,wed,thu,fri, blank for once): mon,tue,wed,thu,fri
```
