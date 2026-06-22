"""
Tests for three small commands combined in one file:
  - perftrace.cli.commands.version       (version)
  - perftrace.cli.commands.fastest_execution (fastest)
  - perftrace.cli.commands.slowest_execution (slowest)
"""
import json
import datetime
from io import StringIO
from unittest.mock import patch, MagicMock, call

import pandas as pd
import pytest
from click.testing import CliRunner
from rich.console import Console as RichConsole

from perftrace.cli.commands.version            import version
from perftrace.cli.commands.fastest_execution  import fastest
from perftrace.cli.commands.slowest_execution  import slowest
from perftrace                                 import __version__

RUNNER = CliRunner()


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


def _invoke_fastest(df, args=None):
    buf = StringIO()
    rich_con = RichConsole(file=buf, width=200, highlight=False, markup=False)
    mock_fn = MagicMock()
    with patch("perftrace.cli.commands.fastest_execution.check_retrieve_data", return_value=df), \
         patch("perftrace.cli.commands.fastest_execution.console", rich_con), \
         patch("perftrace.cli.commands.fastest_execution.find_slowest_fastest_executed", mock_fn):
        result = RUNNER.invoke(fastest, args or [])
    return result, buf.getvalue(), mock_fn


def _invoke_slowest(df, args=None):
    buf = StringIO()
    rich_con = RichConsole(file=buf, width=200, highlight=False, markup=False)
    mock_fn = MagicMock()
    with patch("perftrace.cli.commands.slowest_execution.check_retrieve_data", return_value=df), \
         patch("perftrace.cli.commands.slowest_execution.console", rich_con), \
         patch("perftrace.cli.commands.slowest_execution.find_slowest_fastest_executed", mock_fn):
        result = RUNNER.invoke(slowest, args or [])
    return result, buf.getvalue(), mock_fn


# ── TestVersion ────────────────────────────────────────────────────────────────

class TestVersion:
    """Tests for the `version` command."""

    def test_exits_zero(self):
        buf = StringIO()
        rich_con = RichConsole(file=buf, width=200, highlight=False, markup=False)
        with patch("perftrace.cli.commands.version.console", rich_con):
            result = RUNNER.invoke(version)
        assert result.exit_code == 0

    def test_output_contains_version_string(self):
        buf = StringIO()
        rich_con = RichConsole(file=buf, width=200, highlight=False, markup=False)
        with patch("perftrace.cli.commands.version.console", rich_con):
            RUNNER.invoke(version)
        out = buf.getvalue()
        assert __version__ in out

    def test_output_contains_perftrace_name(self):
        buf = StringIO()
        rich_con = RichConsole(file=buf, width=200, highlight=False, markup=False)
        with patch("perftrace.cli.commands.version.console", rich_con):
            RUNNER.invoke(version)
        out = buf.getvalue()
        assert "PerfTrace" in out

    def test_output_contains_python_version(self):
        import platform
        buf = StringIO()
        rich_con = RichConsole(file=buf, width=200, highlight=False, markup=False)
        with patch("perftrace.cli.commands.version.console", rich_con):
            RUNNER.invoke(version)
        out = buf.getvalue()
        assert platform.python_version() in out

    def test_output_contains_platform_system(self):
        import platform
        buf = StringIO()
        rich_con = RichConsole(file=buf, width=200, highlight=False, markup=False)
        with patch("perftrace.cli.commands.version.console", rich_con):
            RUNNER.invoke(version)
        out = buf.getvalue()
        assert platform.system() in out

    def test_help_exits_cleanly(self):
        result = RUNNER.invoke(version, ["--help"])
        assert result.exit_code == 0

    def test_help_shows_command_description(self):
        result = RUNNER.invoke(version, ["--help"])
        assert "version" in result.output.lower() or "PerfTrace" in result.output


# ── TestFastest ────────────────────────────────────────────────────────────────

class TestFastest:
    """Tests for the `fastest` command."""

    def test_empty_df_exits_cleanly(self):
        result, _, _ = _invoke_fastest(pd.DataFrame())
        assert result.exit_code == 0

    def test_empty_df_prints_no_trace_data(self):
        _, out, _ = _invoke_fastest(pd.DataFrame())
        assert "No trace data found" in out

    def test_empty_df_does_not_call_find_slowest_fastest(self):
        _, _, mock_fn = _invoke_fastest(pd.DataFrame())
        mock_fn.assert_not_called()

    def test_none_df_exits_cleanly(self):
        result, _, _ = _invoke_fastest(None)
        assert result.exit_code == 0

    def test_none_df_prints_no_trace_data(self):
        _, out, _ = _invoke_fastest(None)
        assert "No trace data found" in out

    def test_data_present_calls_find_fn_twice(self):
        df = pd.DataFrame([make_row(function_name="quick_fn")])
        _, _, mock_fn = _invoke_fastest(df)
        assert mock_fn.call_count == 2

    def test_data_present_calls_with_function_name_first(self):
        df = pd.DataFrame([make_row(function_name="fn_a")])
        _, _, mock_fn = _invoke_fastest(df)
        first_call_args = mock_fn.call_args_list[0]
        assert first_call_args[0][1] == "function_name"

    def test_data_present_calls_with_context_tag_second(self):
        df = pd.DataFrame([make_row(function_name="fn_a")])
        _, _, mock_fn = _invoke_fastest(df)
        second_call_args = mock_fn.call_args_list[1]
        assert second_call_args[0][1] == "context_tag"

    def test_data_present_passes_sort_by_true(self):
        df = pd.DataFrame([make_row(function_name="fn_a")])
        _, _, mock_fn = _invoke_fastest(df)
        for c in mock_fn.call_args_list:
            assert c[1].get("sort_by") is True or c[0][2] is True

    def test_data_present_exits_cleanly(self):
        df = pd.DataFrame([make_row(function_name="fn_a")])
        result, _, _ = _invoke_fastest(df)
        assert result.exit_code == 0

    def test_help_exits_cleanly(self):
        result = RUNNER.invoke(fastest, ["--help"])
        assert result.exit_code == 0

    def test_help_shows_fastest_description(self):
        result = RUNNER.invoke(fastest, ["--help"])
        assert "fastest" in result.output.lower() or "fastest" in result.output


# ── TestSlowest ────────────────────────────────────────────────────────────────

class TestSlowest:
    """Tests for the `slowest` command."""

    def test_empty_df_exits_cleanly(self):
        result, _, _ = _invoke_slowest(pd.DataFrame())
        assert result.exit_code == 0

    def test_empty_df_prints_no_trace_data(self):
        _, out, _ = _invoke_slowest(pd.DataFrame())
        assert "No trace data found" in out

    def test_empty_df_does_not_call_find_slowest_fastest(self):
        _, _, mock_fn = _invoke_slowest(pd.DataFrame())
        mock_fn.assert_not_called()

    def test_none_df_exits_cleanly(self):
        result, _, _ = _invoke_slowest(None)
        assert result.exit_code == 0

    def test_none_df_prints_no_trace_data(self):
        _, out, _ = _invoke_slowest(None)
        assert "No trace data found" in out

    def test_data_present_calls_find_fn_twice(self):
        df = pd.DataFrame([make_row(function_name="slow_fn")])
        _, _, mock_fn = _invoke_slowest(df)
        assert mock_fn.call_count == 2

    def test_data_present_calls_with_function_name_first(self):
        df = pd.DataFrame([make_row(function_name="fn_b")])
        _, _, mock_fn = _invoke_slowest(df)
        first_call_args = mock_fn.call_args_list[0]
        assert first_call_args[0][1] == "function_name"

    def test_data_present_calls_with_context_tag_second(self):
        df = pd.DataFrame([make_row(function_name="fn_b")])
        _, _, mock_fn = _invoke_slowest(df)
        second_call_args = mock_fn.call_args_list[1]
        assert second_call_args[0][1] == "context_tag"

    def test_data_present_passes_sort_by_false(self):
        df = pd.DataFrame([make_row(function_name="fn_b")])
        _, _, mock_fn = _invoke_slowest(df)
        for c in mock_fn.call_args_list:
            # sort_by=False may be positional or keyword
            sort_by_val = c[1].get("sort_by") if "sort_by" in c[1] else c[0][2]
            assert sort_by_val is False

    def test_data_present_exits_cleanly(self):
        df = pd.DataFrame([make_row(function_name="fn_b")])
        result, _, _ = _invoke_slowest(df)
        assert result.exit_code == 0

    def test_help_exits_cleanly(self):
        result = RUNNER.invoke(slowest, ["--help"])
        assert result.exit_code == 0

    def test_help_shows_slowest_description(self):
        result = RUNNER.invoke(slowest, ["--help"])
        assert "slowest" in result.output.lower() or "slowest" in result.output
