"""
Tests for perftrace.cli.commands.summary
Covers: no-data path, exception path, function rows, context rows,
mixed data, hotspot detection, and --help.
"""
import json
import datetime
from io import StringIO
from unittest.mock import patch, MagicMock

import pandas as pd
import pytest
from click.testing import CliRunner
from rich.console import Console as RichConsole

from perftrace.cli.commands.summary import summary

RUNNER = CliRunner()

_MODULE   = "perftrace.cli.commands.summary"
_DB_PATH  = f"{_MODULE}.check_retrieve_data"
_CON_PATH = f"{_MODULE}.console"
_SYS_PATH = f"{_MODULE}.SystemCollector"


# ── Shared helpers ─────────────────────────────────────────────────────────────

def make_row(function_name=None, context_tag=None, exec_time=0.01,
             peak_mem=1_048_576, avg_cpu=15.0, ram_delta=0.5):
    return {
        "timestamp": datetime.datetime(2026, 6, 22, 10, 0, 0),
        "function_name": function_name,
        "context_tag": context_tag,
        "execution_collector": json.dumps(
            {"execution_time": exec_time, "start_time": 0.0, "end_time": exec_time}
        ),
        "memory_collector": json.dumps(
            {"current_memory": int(peak_mem * 0.8), "peak_memory": peak_mem}
        ),
        "cpu_collector": json.dumps(
            {"avg_cpu_percentage": avg_cpu, "ram_delta": ram_delta,
             "start_ram": 100.0, "end_ram": 100.5}
        ),
        "file_io_collector": json.dumps(
            {"read_bytes": 0, "write_bytes": 0, "read_count": 0, "write_count": 0}
        ),
        "garbage_collector": json.dumps(
            {"initial_gc_count": 10, "final_gc_count": 10, "delta_gc_count": 0}
        ),
        "thread_context_collector": json.dumps(
            {"threads_delta": 0, "ctx_switches_voluntary_delta": 5,
             "ctx_switches_involuntary_delta": 1, "initial_threads": 4, "final_threads": 4}
        ),
        "network_activity_collector": json.dumps(
            {"tcp_connection_delta": 0, "udp_connection_delta": 0,
             "bytes_sent": 0, "bytes_received": 0}
        ),
        "exception_collector": json.dumps(
            {"occurred": False, "exception_type": None,
             "exception_message": None, "traceback": None}
        ),
    }


def _mock_sys_collector():
    """Return a MagicMock that mimics SystemCollector().report()."""
    mock_cls  = MagicMock()
    mock_inst = MagicMock()
    mock_inst.report.return_value = {"cpu_percent": 20.0, "memory_percentage": 40.0}
    mock_cls.return_value = mock_inst
    return mock_cls


def _invoke(df_or_exc, args=None):
    """
    Invoke the summary command.

    Pass a DataFrame for normal operation, or an Exception instance to make
    check_retrieve_data raise that exception.
    """
    buf = StringIO()
    rich_con = RichConsole(file=buf, width=200, highlight=False, markup=False)

    if isinstance(df_or_exc, Exception):
        db_side_effect = df_or_exc
        db_return      = None
    else:
        db_side_effect = None
        db_return      = df_or_exc

    mock_db = MagicMock(side_effect=db_side_effect, return_value=db_return)

    with patch(_DB_PATH, mock_db), \
         patch(_CON_PATH, rich_con), \
         patch(_SYS_PATH, _mock_sys_collector()):
        result = RUNNER.invoke(summary, args or [])

    return result, buf.getvalue()


# ── TestSummaryNoData ──────────────────────────────────────────────────────────

class TestSummaryNoData:
    """Covers empty DataFrame and exception paths."""

    def test_empty_df_exits_cleanly(self):
        df = pd.DataFrame()
        result, _ = _invoke(df)
        assert result.exit_code == 0

    def test_empty_df_prints_no_data_panel(self):
        df = pd.DataFrame()
        _, out = _invoke(df)
        assert "No performance data recorded yet" in out

    def test_empty_df_does_not_print_records_table(self):
        df = pd.DataFrame()
        _, out = _invoke(df)
        assert "Total Records" not in out

    def test_empty_df_does_not_print_execution_table(self):
        df = pd.DataFrame()
        _, out = _invoke(df)
        assert "Execution Timing" not in out

    def test_empty_df_does_not_print_memory_table(self):
        df = pd.DataFrame()
        _, out = _invoke(df)
        assert "Avg Memory Usage" not in out

    def test_exception_from_check_retrieve_exits_cleanly(self):
        result, _ = _invoke(RuntimeError("DB offline"))
        assert result.exit_code == 0

    def test_exception_prints_failed_to_load(self):
        _, out = _invoke(RuntimeError("connection refused"))
        assert "Failed to load data" in out

    def test_exception_message_included_in_output(self):
        _, out = _invoke(RuntimeError("connection refused"))
        assert "connection refused" in out

    def test_exception_does_not_show_records_table(self):
        _, out = _invoke(OSError("disk error"))
        assert "Total Records" not in out

    def test_exception_does_not_show_memory_table(self):
        _, out = _invoke(OSError("disk error"))
        assert "Avg Memory Usage" not in out


# ── TestSummaryWithData ────────────────────────────────────────────────────────

class TestSummaryWithData:
    """Covers rendering with function rows, context rows, mixed data, hotspot detection."""

    def test_function_rows_show_total_records(self):
        rows = [make_row(function_name=f"fn_{i}") for i in range(3)]
        df = pd.DataFrame(rows)
        _, out = _invoke(df)
        assert "Total Records" in out
        assert "3" in out

    def test_function_rows_show_unique_functions_count(self):
        rows = [make_row(function_name="fn_a"), make_row(function_name="fn_b")]
        df = pd.DataFrame(rows)
        _, out = _invoke(df)
        assert "Unique Functions" in out
        assert "2" in out

    def test_context_rows_show_unique_contexts_count(self):
        rows = [make_row(context_tag="ctx_a"), make_row(context_tag="ctx_b"),
                make_row(context_tag="ctx_c")]
        df = pd.DataFrame(rows)
        _, out = _invoke(df)
        assert "Unique Contexts" in out
        assert "3" in out

    def test_function_rows_show_execution_timing_section(self):
        df = pd.DataFrame([make_row(function_name="timed_fn", exec_time=0.05)])
        _, out = _invoke(df)
        assert "Execution Timing" in out

    def test_function_rows_show_avg_execution(self):
        df = pd.DataFrame([make_row(function_name="fn_avg", exec_time=0.1)])
        _, out = _invoke(df)
        assert "Avg Execution" in out

    def test_function_rows_show_slowest_entry(self):
        df = pd.DataFrame([make_row(function_name="slow_fn", exec_time=2.0)])
        _, out = _invoke(df)
        assert "Slowest" in out
        assert "slow_fn" in out

    def test_function_rows_show_fastest_entry(self):
        df = pd.DataFrame([make_row(function_name="fast_fn", exec_time=0.001)])
        _, out = _invoke(df)
        assert "Fastest" in out
        assert "fast_fn" in out

    def test_memory_section_shows_avg_memory_usage(self):
        df = pd.DataFrame([make_row(function_name="mem_fn", peak_mem=2_097_152)])
        _, out = _invoke(df)
        assert "Avg Memory Usage" in out

    def test_memory_section_shows_peak_memory(self):
        df = pd.DataFrame([make_row(function_name="peak_fn", peak_mem=4_194_304)])
        _, out = _invoke(df)
        assert "Peak Memory" in out

    def test_live_system_section_shows_cpu_usage(self):
        df = pd.DataFrame([make_row(function_name="sys_fn")])
        _, out = _invoke(df)
        assert "CPU Usage" in out

    def test_live_system_section_shows_memory_usage(self):
        df = pd.DataFrame([make_row(function_name="sys_fn")])
        _, out = _invoke(df)
        assert "Memory Usage" in out

    def test_mixed_rows_show_total_function_calls(self):
        rows = [
            make_row(function_name="fn_a"),
            make_row(function_name="fn_b"),
            make_row(context_tag="ctx_a"),
        ]
        df = pd.DataFrame(rows)
        _, out = _invoke(df)
        assert "Total Function Calls" in out
        assert "Total Context Calls" in out

    def test_most_called_function_shown_when_multiple_calls(self):
        rows = [make_row(function_name="hot_fn")] * 5 + [make_row(function_name="cold_fn")]
        df = pd.DataFrame(rows)
        _, out = _invoke(df)
        assert "Most Called Function" in out
        assert "hot_fn" in out

    def test_most_active_context_shown_when_context_rows_present(self):
        rows = [make_row(context_tag="busy_ctx")] * 3 + [make_row(context_tag="idle_ctx")]
        df = pd.DataFrame(rows)
        _, out = _invoke(df)
        assert "Most Active Context" in out
        assert "busy_ctx" in out

    def test_healthy_verdict_when_no_hotspot(self):
        # All rows have the same exec_time → max == mean, no hotspot
        rows = [make_row(function_name="uniform_fn", exec_time=0.01) for _ in range(5)]
        df = pd.DataFrame(rows)
        _, out = _invoke(df)
        assert "healthy" in out.lower()

    def test_hotspot_verdict_when_one_row_much_slower(self):
        # One row is 100x slower than the rest → max > mean * 3
        rows = [make_row(function_name=f"fn_{i}", exec_time=0.01) for i in range(9)]
        rows.append(make_row(function_name="monster_fn", exec_time=1.0))
        df = pd.DataFrame(rows)
        _, out = _invoke(df)
        assert "hotspot" in out.lower()

    def test_hotspot_verdict_not_shown_when_spread_is_small(self):
        rows = [make_row(function_name=f"fn_{i}", exec_time=0.01 * (i + 1)) for i in range(5)]
        df = pd.DataFrame(rows)
        _, out = _invoke(df)
        assert "healthy" in out.lower()

    def test_help_exits_cleanly(self):
        result = RUNNER.invoke(summary, ["--help"])
        assert result.exit_code == 0

    def test_help_shows_command_description(self):
        result = RUNNER.invoke(summary, ["--help"])
        assert "summary" in result.output.lower() or "performance" in result.output.lower()
