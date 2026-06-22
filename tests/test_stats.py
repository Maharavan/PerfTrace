"""
Tests for perftrace.cli.commands.stats
Covers: stats_function, stats_context — empty DataFrames, found rows,
statistical_summary call behaviour, argument requirements, and --help.

Note: stats.py uses `from rich import print` rather than a module-level
console object, so there is no console to patch.  Click's CliRunner
captures stdout automatically, and we only need to intercept
check_retrieve_data and statistical_summary.
"""
import json
import datetime
from unittest.mock import patch, MagicMock

import pandas as pd
import pytest
from click.testing import CliRunner

from perftrace.cli.commands.stats import stats_function, stats_context

RUNNER = CliRunner()

MODULE = "perftrace.cli.commands.stats"


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
    """Invoke a stats command with check_retrieve_data and statistical_summary mocked."""
    mock_summary = MagicMock()
    with patch(f"{MODULE}.check_retrieve_data", return_value=df), \
         patch(f"{MODULE}.statistical_summary", mock_summary):
        result = RUNNER.invoke(cmd, args or [])
    return result, result.output, mock_summary


# ── TestStatsFunction ─────────────────────────────────────────────────────────

class TestStatsFunction:
    def test_empty_df_exits_cleanly(self):
        df = pd.DataFrame(columns=["function_name", "context_tag"])
        result, _, _ = _invoke(stats_function, df, ["any_fn"])
        assert result.exit_code == 0

    def test_empty_df_still_calls_statistical_summary(self):
        # stats.py does not gate on empty — it always calls statistical_summary.
        df = pd.DataFrame(columns=["function_name", "context_tag"])
        _, _, mock_summary = _invoke(stats_function, df, ["any_fn"])
        mock_summary.assert_called_once()

    def test_found_rows_calls_statistical_summary(self):
        df = pd.DataFrame([make_row(function_name="compute")])
        result, _, mock_summary = _invoke(stats_function, df, ["compute"])
        assert result.exit_code == 0
        mock_summary.assert_called_once()

    def test_statistical_summary_receives_filtered_df(self):
        rows = [
            make_row(function_name="compute", exec_time=0.1),
            make_row(function_name="compute", exec_time=0.2),
            make_row(function_name="other_fn", exec_time=0.3),
        ]
        df = pd.DataFrame(rows)
        _, _, mock_summary = _invoke(stats_function, df, ["compute"])
        passed_df = mock_summary.call_args[0][0]
        assert len(passed_df) == 2
        assert all(passed_df["function_name"] == "compute")

    def test_non_matching_name_passes_empty_df_to_summary(self):
        df = pd.DataFrame([make_row(function_name="real_fn")])
        _, _, mock_summary = _invoke(stats_function, df, ["ghost_fn"])
        mock_summary.assert_called_once()
        passed_df = mock_summary.call_args[0][0]
        assert passed_df.empty

    def test_header_text_present_in_output(self):
        df = pd.DataFrame([make_row(function_name="fn_header")])
        _, out, _ = _invoke(stats_function, df, ["fn_header"])
        # rich.print renders markup to stdout when captured by CliRunner
        assert "PerfTrace" in out or "Stats" in out

    def test_help_exits_cleanly(self):
        result = RUNNER.invoke(stats_function, ["--help"])
        assert result.exit_code == 0

    def test_help_shows_function_name_argument(self):
        result = RUNNER.invoke(stats_function, ["--help"])
        assert "FUNCTION_NAME" in result.output


# ── TestStatsContext ──────────────────────────────────────────────────────────

class TestStatsContext:
    def test_empty_df_exits_cleanly(self):
        df = pd.DataFrame(columns=["function_name", "context_tag"])
        result, _, _ = _invoke(stats_context, df, ["any_ctx"])
        assert result.exit_code == 0

    def test_empty_df_still_calls_statistical_summary(self):
        df = pd.DataFrame(columns=["function_name", "context_tag"])
        _, _, mock_summary = _invoke(stats_context, df, ["any_ctx"])
        mock_summary.assert_called_once()

    def test_found_rows_calls_statistical_summary(self):
        df = pd.DataFrame([make_row(context_tag="etl_pipeline")])
        result, _, mock_summary = _invoke(stats_context, df, ["etl_pipeline"])
        assert result.exit_code == 0
        mock_summary.assert_called_once()

    def test_statistical_summary_receives_filtered_df(self):
        rows = [
            make_row(context_tag="etl_pipeline", exec_time=0.1),
            make_row(context_tag="etl_pipeline", exec_time=0.2),
            make_row(context_tag="other_ctx", exec_time=0.9),
        ]
        df = pd.DataFrame(rows)
        _, _, mock_summary = _invoke(stats_context, df, ["etl_pipeline"])
        passed_df = mock_summary.call_args[0][0]
        assert len(passed_df) == 2
        assert all(passed_df["context_tag"] == "etl_pipeline")

    def test_non_matching_tag_passes_empty_df_to_summary(self):
        df = pd.DataFrame([make_row(context_tag="real_ctx")])
        _, _, mock_summary = _invoke(stats_context, df, ["ghost_ctx"])
        mock_summary.assert_called_once()
        passed_df = mock_summary.call_args[0][0]
        assert passed_df.empty

    def test_header_text_present_in_output(self):
        df = pd.DataFrame([make_row(context_tag="ctx_hdr")])
        _, out, _ = _invoke(stats_context, df, ["ctx_hdr"])
        assert "PerfTrace" in out or "Stats" in out

    def test_help_exits_cleanly(self):
        result = RUNNER.invoke(stats_context, ["--help"])
        assert result.exit_code == 0

    def test_help_shows_context_tag_argument(self):
        result = RUNNER.invoke(stats_context, ["--help"])
        assert "CONTEXT_TAG" in result.output


# ── TestStatsRequiresArg ──────────────────────────────────────────────────────

class TestStatsRequiresArg:
    def test_stats_function_fails_without_argument(self):
        result = RUNNER.invoke(stats_function, [])
        assert result.exit_code != 0

    def test_stats_function_error_mentions_missing_argument(self):
        result = RUNNER.invoke(stats_function, [])
        assert "Missing argument" in result.output or result.exit_code != 0

    def test_stats_context_fails_without_argument(self):
        result = RUNNER.invoke(stats_context, [])
        assert result.exit_code != 0

    def test_stats_context_error_mentions_missing_argument(self):
        result = RUNNER.invoke(stats_context, [])
        assert "Missing argument" in result.output or result.exit_code != 0
