# Calendar Performance Test Plan

This plan captures the target scenarios, data shapes, and success criteria for the calendar performance suite. The intent is to keep regression checks fast, deterministic, and representative of production usage.

## Key User Flows

| Flow | Endpoint / Component | Primary Metric | Stretch Metrics |
| --- | --- | --- | --- |
| Calendar feed aggregation | `GET /oobc-management/calendar/feed/json/` (`common:oobc_calendar_feed_json`) | ≤ 18 DB queries, ≤ 750 ms response on seeded dataset | payload size logged for trend analysis |
| Coordination calendar HTMX fragment | `GET /common/coordination/calendar/` (`common:coordination_calendar`) | ≤ 20 DB queries, ≤ 900 ms response | rendered HTML ≤ 350 KB |
| Resource booking conflict lookup | `CalendarResourceBooking` overlap query | ≤ 2 DB queries, ≤ 120 ms lookup | overlap boolean reused across validation paths |
| Attendance check-in (manual) | `POST /coordination/events/<id>/check-in/` | ≤ 8 DB queries, ≤ 450 ms response | redirect completes in single request |
| ICS export | `GET /oobc-management/calendar/feed/ics/` | ≤ 18 DB queries, ≤ 1.5 s response | generated ICS size logged |

_The suite will start with the feed aggregation and booking validation flows. Additional flows will be added once shared fixtures are in place._

## Dataset Strategy

- **Seed volume**: baseline dataset seeds ~80 events, 30 bookings, and 8 leave entries; the stress dataset scales to ~320 events, 120 bookings, and 24 leaves.
- **Temporal distribution**: Spread dates across the previous month, current week, and upcoming month to trigger both “upcoming” and “past” logic branches.
- **Ownership**: all records created under a privileged “performance” user so the suite can force-login without extra setup.

## Measurement Approach

- Shared utility wrappers collect:
  - Wall-clock duration (`time.perf_counter`).
  - Number of SQL statements via `CaptureQueriesContext`.
  - Payload size (JSON/HTML/ICS) when applicable.
- Each test asserts an upper bound for the primary metric and records the measured numbers for trend dashboards.
- Optional JSON reports (stored in `var/perf_reports/` when the CLI script is used) capture the duration, query count, and payload size for trend monitoring.

### Environment Assumptions

- Tests run with `DEBUG=0` using the standard Django production configuration.
- The default in-memory cache backend (`locmem`) is sufficient; Redis is not required for regression checks.
- Celery workers remain offline; any notification tasks must be short-circuited during measurement.
- SQLite is acceptable for smoke tests, but nightly CI should target PostgreSQL to mirror staging query plans.

### Metrics Capture

- If `PERF_METRICS_FILE` is set, each scenario appends a JSON object similar to:

  ```json
  {
    "name": "calendar_feed",
    "label": "stress",
    "duration_ms": 640.2,
    "query_count": 17,
    "payload_bytes": 48231
  }
  ```
- `scripts/run_calendar_perf.sh` exports this variable and stores the aggregated metrics under `var/perf_reports/` using a timestamped filename.

## Execution Modes

| Mode | Command | Frequency |
| --- | --- | --- |
| Local smoke | `pytest -m performance --maxfail=1` | Developer initiated |
| CI nightly | `scripts/run_calendar_perf.sh` | Scheduled job |
| Pre-release | Same as CI, run on staging data | Release gating |

## Ownership & Maintenance

- The calendar team owns threshold updates and data set adjustments.
- The testing team maintains `tests/perf_utils/`, the execution script, and CI wiring.
- A quarterly review ensures metrics still match real-world expectations.

## Continuous Improvement Backlog

- Track memory footprint for feed generation once Django 5.x upgrade lands.
- Add HTMX drag-and-drop reschedule timing once the optimistic UI work is complete.
- Capture metrics from the attendance QR POST once we introduce Celery-based notifications.
- Feed JSON results into a lightweight dashboard (e.g. GitHub Pages + JSON artifacts) for trend analysis.

---

_Last updated: 2025-10-02_
