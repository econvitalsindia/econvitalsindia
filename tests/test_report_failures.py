"""scripts/report_failures.py: network blips wait a day, other errors report at once."""
import importlib.util
from datetime import datetime, timedelta, timezone
from pathlib import Path

spec = importlib.util.spec_from_file_location("rf", Path(__file__).parents[1] / "scripts" / "report_failures.py")
rf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rf)
NOW = datetime(2026, 10, 31, 12, tzinfo=timezone.utc)


def test_network_blip_waits():
    dns = "RuntimeError: GET https://www.amfiindia.com/x failed: [Errno -3] Temporary failure in name resolution"
    assert not rf.should_report(dns, NOW - timedelta(hours=5), NOW)
    assert not rf.should_report("RuntimeError: GET https://www.aai.aero/x failed: timed out", NOW - timedelta(hours=5), NOW)
    assert rf.should_report(dns, NOW - timedelta(hours=30), NOW)          # down for over a day
    assert rf.should_report(dns, None, NOW)                               # never succeeded


def test_parser_error_reports_at_once():
    assert rf.should_report("RuntimeError: no CPI-IW press note linked on the Labour Bureau home page",
                            NOW - timedelta(hours=1), NOW)
