"""
Tests for perftrace.cli.commands.system_monitor
Covers helper functions, table builders, and the Click command interface.
"""
import datetime
import time
from collections import deque
from unittest.mock import MagicMock, patch
import pytest

from perftrace.cli.commands.system_monitor import (
    _fmt_bytes,
    _fmt_bytes_per_sec,
    _pct_color,
    _progress_bar,
    _sparkline,
    _fmt_uptime,
    _build_cpu_table,
    _build_memory_table,
    _build_disk_net_table,
    _build_system_table,
    _build_layout,
    system_monitor,
)
from click.testing import CliRunner


# ── _fmt_bytes ──────────────────────────────────────────────────────────────

class TestFmtBytes:
    def test_none_returns_dash(self):
        assert _fmt_bytes(None) == "-"

    def test_bytes_range(self):
        assert "B" in _fmt_bytes(512)

    def test_kilobytes_range(self):
        result = _fmt_bytes(2048)
        assert "KB" in result

    def test_megabytes_range(self):
        result = _fmt_bytes(2 * 1024 ** 2)
        assert "MB" in result

    def test_gigabytes_range(self):
        result = _fmt_bytes(3 * 1024 ** 3)
        assert "GB" in result

    def test_invalid_type(self):
        result = _fmt_bytes("not-a-number")
        assert result == "not-a-number"

    def test_zero(self):
        assert "0" in _fmt_bytes(0)


# ── _fmt_bytes_per_sec ───────────────────────────────────────────────────────

class TestFmtBytesPerSec:
    def test_appends_per_second(self):
        result = _fmt_bytes_per_sec(1024)
        assert "/s" in result

    def test_none_returns_dash(self):
        assert _fmt_bytes_per_sec(None) == "-"


# ── _pct_color ───────────────────────────────────────────────────────────────

class TestPctColor:
    def test_low_is_green(self):
        assert _pct_color(10) == "green"

    def test_medium_is_yellow(self):
        assert _pct_color(60) == "yellow"

    def test_high_is_red(self):
        assert "red" in _pct_color(85)

    def test_boundary_50(self):
        assert _pct_color(50) == "yellow"

    def test_boundary_80(self):
        assert "red" in _pct_color(80)

    def test_zero(self):
        assert _pct_color(0) == "green"

    def test_100(self):
        assert "red" in _pct_color(100)


# ── _progress_bar ────────────────────────────────────────────────────────────

class TestProgressBar:
    def test_returns_string(self):
        result = _progress_bar(50)
        assert isinstance(result, str)

    def test_contains_block_chars(self):
        result = _progress_bar(50)
        assert "█" in result or "░" in result

    def test_zero_percent_all_empty(self):
        result = _progress_bar(0)
        assert "█" not in result

    def test_100_percent_all_filled(self):
        result = _progress_bar(100)
        assert "░" not in result

    def test_custom_width(self):
        result = _progress_bar(50, width=10)
        # 5 filled + 5 empty = 10 chars (markup stripped)
        assert isinstance(result, str)


# ── _sparkline ───────────────────────────────────────────────────────────────

class TestSparkline:
    def test_empty_returns_no_data(self):
        result = _sparkline([])
        assert "no data" in result

    def test_non_empty_returns_string(self):
        result = _sparkline([10, 50, 90])
        assert isinstance(result, str)
        assert len(result) > 0

    def test_all_zero(self):
        result = _sparkline([0, 0, 0])
        assert isinstance(result, str)

    def test_all_max(self):
        result = _sparkline([100, 100, 100])
        assert "█" in result

    def test_length_matches_input(self):
        history = [10, 20, 30, 40, 50]
        result = _sparkline(history)
        # Result contains Rich markup + actual characters; count non-markup chars
        stripped = result.replace("[green]", "").replace("[/green]", "") \
                         .replace("[yellow]", "").replace("[/yellow]", "") \
                         .replace("[bold red]", "").replace("[/bold red]", "")
        assert len(stripped) == len(history)


# ── _fmt_uptime ──────────────────────────────────────────────────────────────

class TestFmtUptime:
    def test_seconds_only(self):
        now = datetime.datetime.now()
        boot = (now - datetime.timedelta(seconds=45)).timestamp()
        result = _fmt_uptime(boot)
        assert "m" in result

    def test_hours_shown(self):
        now = datetime.datetime.now()
        boot = (now - datetime.timedelta(hours=2, minutes=30)).timestamp()
        result = _fmt_uptime(boot)
        assert "h" in result

    def test_days_shown(self):
        now = datetime.datetime.now()
        boot = (now - datetime.timedelta(days=3, hours=5)).timestamp()
        result = _fmt_uptime(boot)
        assert "d" in result

    def test_returns_string(self):
        boot = (datetime.datetime.now() - datetime.timedelta(minutes=10)).timestamp()
        assert isinstance(_fmt_uptime(boot), str)


# ── Table builder smoke tests ─────────────────────────────────────────────────

SAMPLE_DATA = {
    "cpu_percent":              25.0,
    "total_system_memory":      8 * 1024 ** 3,
    "used_memory":              4 * 1024 ** 3,
    "available_system_memory":  3 * 1024 ** 3,
    "free_memory":              1 * 1024 ** 3,
    "memory_percentage":        50.0,
    "total_disk_space":         500 * 1024 ** 3,
    "used_disk_space":          200 * 1024 ** 3,
    "free_disk_space":          300 * 1024 ** 3,
    "uptime":                   (datetime.datetime.now() - datetime.timedelta(hours=1)).timestamp(),
}

_MOCK_SWAP = MagicMock(used=1 * 1024 ** 3, total=4 * 1024 ** 3, percent=25.0)
_MOCK_FREQ = MagicMock(current=2400.0, max=3600.0)
_MOCK_PIDS = list(range(200))


class TestBuildCpuTable:
    @patch("perftrace.cli.commands.system_monitor.psutil.cpu_percent",
           return_value=[10.0, 20.0, 30.0, 40.0])
    @patch("perftrace.cli.commands.system_monitor.psutil.cpu_freq",
           return_value=_MOCK_FREQ)
    @patch("perftrace.cli.commands.system_monitor.psutil.cpu_count",
           side_effect=lambda logical=True: 4 if logical else 2)
    def test_returns_table(self, *_):
        from rich.table import Table
        table = _build_cpu_table(SAMPLE_DATA, [10.0, 50.0, 90.0])
        assert isinstance(table, Table)

    @patch("perftrace.cli.commands.system_monitor.psutil.cpu_percent",
           return_value=[5.0])
    @patch("perftrace.cli.commands.system_monitor.psutil.cpu_freq", return_value=None)
    @patch("perftrace.cli.commands.system_monitor.psutil.cpu_count",
           side_effect=lambda logical=True: 1 if logical else 1)
    def test_no_freq_info(self, *_):
        from rich.table import Table
        table = _build_cpu_table(SAMPLE_DATA, [])
        assert isinstance(table, Table)


class TestBuildMemoryTable:
    @patch("perftrace.cli.commands.system_monitor.psutil.swap_memory",
           return_value=_MOCK_SWAP)
    def test_returns_table(self, _):
        from rich.table import Table
        table = _build_memory_table(SAMPLE_DATA)
        assert isinstance(table, Table)

    @patch("perftrace.cli.commands.system_monitor.psutil.swap_memory",
           return_value=_MOCK_SWAP)
    def test_handles_zero_memory(self, _):
        from rich.table import Table
        data = dict(SAMPLE_DATA)
        data.update({"total_system_memory": 0, "used_memory": 0,
                     "available_system_memory": 0, "free_memory": 0})
        table = _build_memory_table(data)
        assert isinstance(table, Table)


class TestBuildDiskNetTable:
    def test_returns_table(self):
        from rich.table import Table
        table = _build_disk_net_table(SAMPLE_DATA, 1024, 2048, 10000, 20000)
        assert isinstance(table, Table)

    def test_zero_disk(self):
        from rich.table import Table
        data = dict(SAMPLE_DATA)
        data.update({"total_disk_space": 0, "used_disk_space": 0, "free_disk_space": 0})
        table = _build_disk_net_table(data, 0, 0, 0, 0)
        assert isinstance(table, Table)


class TestBuildSystemTable:
    @patch("perftrace.cli.commands.system_monitor.psutil.pids",
           return_value=_MOCK_PIDS)
    def test_returns_table(self, _):
        from rich.table import Table
        table = _build_system_table(SAMPLE_DATA, 5, 3, len(_MOCK_PIDS))
        assert isinstance(table, Table)

    def test_no_uptime(self):
        from rich.table import Table
        data = dict(SAMPLE_DATA)
        data["uptime"] = None
        table = _build_system_table(data, 1, 3, 100)
        assert isinstance(table, Table)


# ── _build_layout smoke test ─────────────────────────────────────────────────

class TestBuildLayout:
    @patch("perftrace.cli.commands.system_monitor.psutil.cpu_percent",
           return_value=[5.0, 10.0, 15.0, 20.0])
    @patch("perftrace.cli.commands.system_monitor.psutil.cpu_freq",
           return_value=_MOCK_FREQ)
    @patch("perftrace.cli.commands.system_monitor.psutil.cpu_count",
           side_effect=lambda logical=True: 4 if logical else 2)
    @patch("perftrace.cli.commands.system_monitor.psutil.swap_memory",
           return_value=_MOCK_SWAP)
    @patch("perftrace.cli.commands.system_monitor.psutil.net_io_counters")
    @patch("perftrace.cli.commands.system_monitor.psutil.pids",
           return_value=_MOCK_PIDS)
    def test_returns_renderable(self, mock_pids, mock_net, *_):
        mock_net.return_value = MagicMock(
            bytes_sent=100_000, bytes_recv=200_000,
            packets_sent=500, packets_recv=800,
        )
        layout = _build_layout(SAMPLE_DATA, 1, 3)
        assert layout is not None


# ── CLI command ───────────────────────────────────────────────────────────────

class TestSystemMonitorCommand:
    def test_help_text(self):
        runner = CliRunner()
        result = runner.invoke(system_monitor, ["--help"])
        assert result.exit_code == 0
        assert "interval" in result.output.lower() or "refresh" in result.output.lower()

    def test_default_interval_option(self):
        runner = CliRunner()
        result = runner.invoke(system_monitor, ["--help"])
        assert "3" in result.output

    def test_invalid_interval_type(self):
        runner = CliRunner()
        result = runner.invoke(system_monitor, ["--interval", "abc"])
        assert result.exit_code != 0
