# Release calendars

One yaml per publisher. Each file names its official source (`source_url`) and holiday rule
(`next_working_day`, `previous_working_day` or `none`). Entries:
`{date, title, period, series: [ids], show?: level|yoy, time_ist?, estimated?, highlight?, source_url?}`.

- Dates are copied from the publisher's advance release calendar. When only a rule exists
  ("by the 15th"), set `estimated: true`.
- Weekend dates are shifted by the holiday rule at build time (`pipelines/build/calendar.py`)
  and shown as adjusted. Public holidays are not known to the build, so a person should
  check the coming month's dates against the official calendar (runbook, monthly task).
- `series` links a release to the series it updates, so the calendar can show the last value.
