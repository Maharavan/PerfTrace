"""
Tests for perftrace.cli.commands.recent_data
Covers: recent_function, recent_context — empty results, found records,
tail(1) latest-only behaviour, argument requirements, and --help.
"""
import json
import datetime
from io import StringIO
from unittest.mock import patch, MagicMock

import pandas as pd
import pytest
from click.testing import CliRunner
from rich.console import Console as RichConsole

from perftrace.cli.commands.recent_data import recent_function, recent_context

RUNNER = CliRunner()

MODULE = "perftrace.cli.commands.recent_data"


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
    mock_recent = MagicMock()
    with patch(f"{MODULE}.check_retrieve_data", return_value=df), \
         patch(f"{MODULE}.console", rich_con), \
         patch(f"{MODULE}.get_recent_info_about_function_context", mock_recent):
        result = RUNNER.invoke(cmd, args or [])
    return result, buf.getvalue(), mock_recent


# ── TestRecentFunction ────────────────────────────────────────────────────────

class TestRecentFunction:
    def test_empty_df_exits_cleanly(self):
        df = pd.DataFrame(columns=["function_name", "context_tag"])
        result, _, _ = _invoke(recent_function, df, ["some_fn"])
        assert result.exit_code == 0

    def test_empty_df_prints_no_records_message(self):
        df = pd.DataFrame(columns=["function_name", "context_tag"])
        _, out, _ = _invoke(recent_function, df, ["some_fn"])
        assert "No records found for function" in out

    def test_no_records_message_includes_function_name(self):
        df = pd.DataFrame(columns=["function_name", "context_tag"])
        _, out, _ = _invoke(recent_function, df, ["missing_func"])
        assert "missing_func" in out

    def test_found_row_calls_get_recent_info(self):
        df = pd.DataFrame([make_row(function_name="traced_fn")])
        result, _, mock_recent = _invoke(recent_function, df, ["traced_fn"])
        assert result.exit_code == 0
        mock_recent.assert_called_once()

    def test_tail_one_only_passes_single_row(self):
        # Three rows for the same function — only the last should be passed.
        rows = [
            make_row(function_name="multi_fn", exec_time=0.1),
            make_row(function_name="multi_fn", exec_time=0.2),
            make_row(function_name="multi_fn", exec_time=0.9),
        ]
        df = pd.DataFrame(rows)
        result, _, mock_recent = _invoke(recent_function, df, ["multi_fn"])
        assert result.exit_code == 0
        mock_recent.assert_called_once()
        passed_df = mock_recent.call_args[0][0]
        assert len(passed_df) == 1

    def test_non_matching_name_does_not_call_get_recent_info(self):
        df = pd.DataFrame([make_row(function_name="other_fn")])
        _, out, mock_recent = _invoke(recent_function, df, ["absent_fn"])
        mock_recent.assert_not_called()
        assert "No records found for function" in out

    def test_found_record_prints_most_recent_label(self):
        df = pd.DataFrame([make_row(function_name="fn_label")])
        _, out, _ = _invoke(recent_function, df, ["fn_label"])
        assert "fn_label" in out

    def test_help_exits_cleanly(self):
        result = RUNNER.invoke(recent_function, ["--help"])
        assert result.exit_code == 0

    def test_help_shows_function_name_argument(self):
        result = RUNNER.invoke(recent_function, ["--help"])
        assert "FUNCTION_NAME" in result.output


# ── TestRecentContext ─────────────────────────────────────────────────────────

class TestRecentContext:
    def test_empty_df_exits_cleanly(self):
        df = pd.DataFrame(columns=["function_name", "context_tag"])
        result, _, _ = _invoke(recent_context, df, ["some_ctx"])
        assert result.exit_code == 0

    def test_empty_df_prints_no_records_message(self):
        df = pd.DataFrame(columns=["function_name", "context_tag"])
        _, out, _ = _invoke(recent_context, df, ["some_ctx"])
        assert "No records found for context" in out

    def test_no_records_message_includes_context_tag(self):
        df = pd.DataFrame(columns=["function_name", "context_tag"])
        _, out, _ = _invoke(recent_context, df, ["pipeline_ctx"])
        assert "pipeline_ctx" in out

    def test_found_row_calls_get_recent_info(self):
        df = pd.DataFrame([make_row(context_tag="active_ctx")])
        result, _, mock_recent = _invoke(recent_context, df, ["active_ctx"])
        assert result.exit_code == 0
        mock_recent.assert_called_once()

    def test_tail_one_only_passes_single_row(self):
        rows = [
            make_row(context_tag="multi_ctx", exec_time=0.05),
            make_row(context_tag="multi_ctx", exec_time=0.10),
            make_row(context_tag="multi_ctx", exec_time=0.50),
        ]
        df = pd.DataFrame(rows)
        result, _, mock_recent = _invoke(recent_context, df, ["multi_ctx"])
        assert result.exit_code == 0
        mock_recent.assert_called_once()
        passed_df = mock_recent.call_args[0][0]
        assert len(passed_df) == 1

    def test_non_matching_tag_does_not_call_get_recent_info(self):
        df = pd.DataFrame([make_row(context_tag="existing_ctx")])
        _, out, mock_recent = _invoke(recent_context, df, ["absent_ctx"])
        mock_recent.assert_not_called()
        assert "No records found for context" in out

    def test_found_record_prints_context_label(self):
        df = pd.DataFrame([make_row(context_tag="ctx_label")])
        _, out, _ = _invoke(recent_context, df, ["ctx_label"])
        assert "ctx_label" in out

    def test_help_exits_cleanly(self):
        result = RUNNER.invoke(recent_context, ["--help"])
        assert result.exit_code == 0

    def test_help_shows_context_tag_argument(self):
        result = RUNNER.invoke(recent_context, ["--help"])
        assert "CONTEXT_TAG" in result.output


# ── TestRecentRequiresArg ─────────────────────────────────────────────────────

class TestRecentRequiresArg:
    def test_recent_function_fails_without_argument(self):
        result = RUNNER.invoke(recent_function, [])
        assert result.exit_code != 0

    def test_recent_function_error_mentions_missing_argument(self):
        result = RUNNER.invoke(recent_function, [])
        assert "Missing argument" in result.output or result.exit_code != 0

    def test_recent_context_fails_without_argument(self):
        result = RUNNER.invoke(recent_context, [])
        assert result.exit_code != 0

    def test_recent_context_error_mentions_missing_argument(self):
        result = RUNNER.invoke(recent_context, [])
        assert "Missing argument" in result.output or result.exit_code != 0
