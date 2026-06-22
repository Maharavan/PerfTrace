"""
Tests for perftrace.cli.commands.show_data
Covers: show_function, show_context — no-data messages, matching rows,
non-matching filters, argument requirements, and --help.
"""
import json
import datetime
from io import StringIO
from unittest.mock import patch, MagicMock

import pandas as pd
import pytest
from click.testing import CliRunner
from rich.console import Console as RichConsole

from perftrace.cli.commands.show_data import show_function, show_context

RUNNER = CliRunner()

MODULE = "perftrace.cli.commands.show_data"


# ── Shared helpers ────────────────────────────────────────────────────────────

def make_row(function_name=None, context_tag=None, exec_time=0.01, peak_mem=1_048_576,
             avg_cpu=15.0, ram_delta=0.5, exc_occurred=False, exc_type=None, exc_msg=None):
    return {
        "timestamp": datetime.datetime(2026, 6, 22, 10, 0, 0),
        "function_name": function_name,
        "context_tag": context_tag,
        "execution_collector": json.dumps({"execution_time": exec_time, "start_time": 0.0, "end_time": exec_time}),
        "memory_collector": json.dumps({"current_memory": int(peak_mem * 0.8), "peak_memory": peak_mem}),
        "cpu_collector": json.dumps({"avg_cpu_percentage": avg_cpu, "ram_delta": ram_delta,
                                      "start_ram": 100.0, "end_ram": 100.5,
                                      "cpu_usage_start": 10.0, "cpu_usage_end": 20.0}),
        "file_io_collector": json.dumps({"read_bytes": 0, "write_bytes": 0,
                                          "read_count": 0, "write_count": 0, "other_count": 0}),
        "garbage_collector": json.dumps({"initial_gc_count": 10, "final_gc_count": 10, "delta_gc_count": 0}),
        "thread_context_collector": json.dumps({"threads_delta": 0, "ctx_switches_voluntary_delta": 5,
                                                 "ctx_switches_involuntary_delta": 1,
                                                 "initial_threads": 4, "final_threads": 4}),
        "network_activity_collector": json.dumps({"tcp_connection_delta": 0, "udp_connection_delta": 0,
                                                   "bytes_sent": 0, "bytes_received": 0,
                                                   "bytes_sent_delta": 0, "bytes_received_delta": 0}),
        "exception_collector": json.dumps({"occurred": exc_occurred, "exception_type": exc_type,
                                           "exception_message": exc_msg, "traceback": None}),
    }


def _invoke(cmd, df, args=None):
    buf = StringIO()
    rich_con = RichConsole(file=buf, width=200, highlight=False, markup=False)
    mock_table = MagicMock()
    with patch(f"{MODULE}.check_retrieve_data", return_value=df), \
         patch(f"{MODULE}.console", rich_con), \
         patch(f"{MODULE}.get_compact_trace_table", mock_table):
        result = RUNNER.invoke(cmd, args or [])
    return result, buf.getvalue(), mock_table


# ── TestShowFunction ──────────────────────────────────────────────────────────

class TestShowFunction:
    def test_no_data_prints_no_records_message(self):
        df = pd.DataFrame(columns=["function_name", "context_tag"])
        result, out, _ = _invoke(show_function, df, ["my_func"])
        assert result.exit_code == 0
        assert "No records found for function" in out

    def test_no_data_message_includes_function_name(self):
        df = pd.DataFrame(columns=["function_name", "context_tag"])
        _, out, _ = _invoke(show_function, df, ["target_fn"])
        assert "target_fn" in out

    def test_matching_row_calls_get_compact_trace_table(self):
        df = pd.DataFrame([make_row(function_name="my_func")])
        result, _, mock_table = _invoke(show_function, df, ["my_func"])
        assert result.exit_code == 0
        mock_table.assert_called_once()

    def test_non_matching_name_prints_no_records(self):
        df = pd.DataFrame([make_row(function_name="other_func")])
        _, out, mock_table = _invoke(show_function, df, ["missing_func"])
        assert "No records found for function" in out
        mock_table.assert_not_called()

    def test_multiple_rows_same_function_all_passed_to_table(self):
        rows = [make_row(function_name="batch_fn", exec_time=t) for t in [0.1, 0.2, 0.3]]
        df = pd.DataFrame(rows)
        result, _, mock_table = _invoke(show_function, df, ["batch_fn"])
        assert result.exit_code == 0
        mock_table.assert_called_once()
        passed_df = mock_table.call_args[0][0]
        assert len(passed_df) == 3

    def test_help_exits_cleanly(self):
        result = RUNNER.invoke(show_function, ["--help"])
        assert result.exit_code == 0

    def test_help_shows_function_name_argument(self):
        result = RUNNER.invoke(show_function, ["--help"])
        assert "FUNCTION_NAME" in result.output


# ── TestShowContext ───────────────────────────────────────────────────────────

class TestShowContext:
    def test_no_data_prints_no_records_message(self):
        df = pd.DataFrame(columns=["function_name", "context_tag"])
        result, out, _ = _invoke(show_context, df, ["my_ctx"])
        assert result.exit_code == 0
        assert "No records found for context" in out

    def test_no_data_message_includes_context_tag(self):
        df = pd.DataFrame(columns=["function_name", "context_tag"])
        _, out, _ = _invoke(show_context, df, ["pipeline_ctx"])
        assert "pipeline_ctx" in out

    def test_matching_row_calls_get_compact_trace_table(self):
        df = pd.DataFrame([make_row(context_tag="my_ctx")])
        result, _, mock_table = _invoke(show_context, df, ["my_ctx"])
        assert result.exit_code == 0
        mock_table.assert_called_once()

    def test_non_matching_tag_prints_no_records(self):
        df = pd.DataFrame([make_row(context_tag="other_ctx")])
        _, out, mock_table = _invoke(show_context, df, ["missing_ctx"])
        assert "No records found for context" in out
        mock_table.assert_not_called()

    def test_multiple_rows_same_context_all_passed_to_table(self):
        rows = [make_row(context_tag="batch_ctx", exec_time=t) for t in [0.05, 0.10, 0.15]]
        df = pd.DataFrame(rows)
        result, _, mock_table = _invoke(show_context, df, ["batch_ctx"])
        assert result.exit_code == 0
        mock_table.assert_called_once()
        passed_df = mock_table.call_args[0][0]
        assert len(passed_df) == 3

    def test_context_row_not_returned_for_function_query(self):
        df = pd.DataFrame([make_row(context_tag="ctx_only")])
        _, out, mock_table = _invoke(show_context, df, ["other_ctx"])
        mock_table.assert_not_called()

    def test_help_exits_cleanly(self):
        result = RUNNER.invoke(show_context, ["--help"])
        assert result.exit_code == 0

    def test_help_shows_context_tag_argument(self):
        result = RUNNER.invoke(show_context, ["--help"])
        assert "CONTEXT_TAG" in result.output


# ── TestShowDataRequiresArg ───────────────────────────────────────────────────

class TestShowDataRequiresArg:
    def test_show_function_fails_without_argument(self):
        result = RUNNER.invoke(show_function, [])
        assert result.exit_code != 0

    def test_show_function_error_mentions_missing_argument(self):
        result = RUNNER.invoke(show_function, [])
        assert "Missing argument" in result.output or result.exit_code != 0

    def test_show_context_fails_without_argument(self):
        result = RUNNER.invoke(show_context, [])
        assert result.exit_code != 0

    def test_show_context_error_mentions_missing_argument(self):
        result = RUNNER.invoke(show_context, [])
        assert "Missing argument" in result.output or result.exit_code != 0
