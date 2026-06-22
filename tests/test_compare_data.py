"""
Tests for perftrace.cli.commands.compare_data
Covers: compare_function, compare_context commands, and the _avg_metrics helper.
Verifies empty data, missing A/B, both found, delta computation, and CLI interface.
"""
import json
import datetime
from io import StringIO
from unittest.mock import patch

import pandas as pd
import pytest
from click.testing import CliRunner
from rich.console import Console as RichConsole

from perftrace.cli.commands.compare_data import (
    compare_function,
    compare_context,
    _avg_metrics,
)

RUNNER = CliRunner()
MODULE = "perftrace.cli.commands.compare_data"


# ── Shared helpers ─────────────────────────────────────────────────────────────

def make_row(function_name=None, context_tag=None, exec_time=0.01, peak_mem=1_048_576,
             avg_cpu=15.0, ram_delta=0.5, exc_occurred=False, exc_type=None, exc_msg=None):
    return {
        "timestamp": datetime.datetime(2026, 6, 22, 10, 0, 0),
        "function_name": function_name,
        "context_tag": context_tag,
        "execution_collector": json.dumps({
            "execution_time": exec_time, "start_time": 0.0, "end_time": exec_time,
        }),
        "memory_collector": json.dumps({
            "current_memory": int(peak_mem * 0.8), "peak_memory": peak_mem,
        }),
        "cpu_collector": json.dumps({
            "avg_cpu_percentage": avg_cpu, "ram_delta": ram_delta,
            "start_ram": 100.0, "end_ram": 100.5,
        }),
        "file_io_collector": json.dumps({
            "read_bytes": 0, "write_bytes": 0, "read_count": 0, "write_count": 0,
        }),
        "garbage_collector": json.dumps({
            "initial_gc_count": 10, "final_gc_count": 10, "delta_gc_count": 0,
        }),
        "thread_context_collector": json.dumps({
            "threads_delta": 0, "ctx_switches_voluntary_delta": 5,
            "ctx_switches_involuntary_delta": 1, "initial_threads": 4, "final_threads": 4,
        }),
        "network_activity_collector": json.dumps({
            "tcp_connection_delta": 0, "udp_connection_delta": 0,
            "bytes_sent": 0, "bytes_received": 0,
        }),
        "exception_collector": json.dumps({
            "occurred": exc_occurred, "exception_type": exc_type,
            "exception_message": exc_msg, "traceback": None,
        }),
    }


def _invoke(cmd, df, args=None):
    buf = StringIO()
    rich_con = RichConsole(file=buf, width=200, highlight=False, markup=False)
    with patch(f"{MODULE}.check_retrieve_data", return_value=df), \
         patch(f"{MODULE}.console", rich_con):
        result = RUNNER.invoke(cmd, args or [])
    return result, buf.getvalue()


# ── TestCompareFunction ───────────────────────────────────────────────────────

class TestCompareFunction:
    def test_empty_dataframe_exits_cleanly(self):
        result, _ = _invoke(compare_function, pd.DataFrame(), ["fn_a", "fn_b"])
        assert result.exit_code == 0

    def test_empty_dataframe_prints_no_trace_data(self):
        _, out = _invoke(compare_function, pd.DataFrame(), ["fn_a", "fn_b"])
        assert "No trace data" in out

    def test_missing_function_a_prints_error(self):
        df = pd.DataFrame([make_row(function_name="fn_b", exec_time=0.05)])
        _, out = _invoke(compare_function, df, ["fn_missing", "fn_b"])
        assert "fn_missing" in out
        assert "No records found" in out

    def test_missing_function_b_prints_error(self):
        df = pd.DataFrame([make_row(function_name="fn_a", exec_time=0.05)])
        _, out = _invoke(compare_function, df, ["fn_a", "fn_missing"])
        assert "fn_missing" in out
        assert "No records found" in out

    def test_missing_message_mentions_function(self):
        df = pd.DataFrame([make_row(function_name="fn_a", exec_time=0.05)])
        _, out = _invoke(compare_function, df, ["fn_a", "absent_fn"])
        assert "function" in out.lower()

    def test_both_found_shows_comparison_table(self):
        df = pd.DataFrame([
            make_row(function_name="fn_alpha", exec_time=0.02, peak_mem=2_097_152),
            make_row(function_name="fn_beta",  exec_time=0.04, peak_mem=4_194_304),
        ])
        _, out = _invoke(compare_function, df, ["fn_alpha", "fn_beta"])
        assert "Function Comparison" in out
        assert "Average Metrics" in out

    def test_both_function_names_appear_as_table_headers(self):
        df = pd.DataFrame([
            make_row(function_name="load_data",    exec_time=0.01),
            make_row(function_name="process_data", exec_time=0.03),
        ])
        _, out = _invoke(compare_function, df, ["load_data", "process_data"])
        assert "load_data" in out
        assert "process_data" in out

    def test_run_count_shown_for_each_function(self):
        df = pd.DataFrame([
            make_row(function_name="fn_x", exec_time=0.01),
            make_row(function_name="fn_x", exec_time=0.02),
            make_row(function_name="fn_y", exec_time=0.05),
        ])
        _, out = _invoke(compare_function, df, ["fn_x", "fn_y"])
        # fn_x has 2 runs, fn_y has 1 run
        assert "2 run" in out
        assert "1 run" in out

    def test_delta_column_present_in_output(self):
        df = pd.DataFrame([
            make_row(function_name="slow_fn", exec_time=0.1),
            make_row(function_name="fast_fn", exec_time=0.01),
        ])
        _, out = _invoke(compare_function, df, ["slow_fn", "fast_fn"])
        # Delta column header uses the minus sign (A − B)
        assert "A" in out and "B" in out

    def test_help_exits_cleanly(self):
        result = RUNNER.invoke(compare_function, ["--help"])
        assert result.exit_code == 0

    def test_help_shows_two_arguments(self):
        result = RUNNER.invoke(compare_function, ["--help"])
        assert "FUNCTION_A" in result.output
        assert "FUNCTION_B" in result.output


# ── TestCompareContext ────────────────────────────────────────────────────────

class TestCompareContext:
    def test_empty_dataframe_exits_cleanly(self):
        result, _ = _invoke(compare_context, pd.DataFrame(), ["ctx_a", "ctx_b"])
        assert result.exit_code == 0

    def test_empty_dataframe_prints_no_trace_data(self):
        _, out = _invoke(compare_context, pd.DataFrame(), ["ctx_a", "ctx_b"])
        assert "No trace data" in out

    def test_missing_context_a_prints_error(self):
        df = pd.DataFrame([make_row(context_tag="ctx_b", exec_time=0.05)])
        _, out = _invoke(compare_context, df, ["ctx_missing", "ctx_b"])
        assert "ctx_missing" in out
        assert "No records found" in out

    def test_missing_context_b_prints_error(self):
        df = pd.DataFrame([make_row(context_tag="ctx_a", exec_time=0.05)])
        _, out = _invoke(compare_context, df, ["ctx_a", "ctx_missing"])
        assert "ctx_missing" in out
        assert "No records found" in out

    def test_missing_message_mentions_context(self):
        df = pd.DataFrame([make_row(context_tag="ctx_a", exec_time=0.05)])
        _, out = _invoke(compare_context, df, ["ctx_a", "absent_ctx"])
        assert "context" in out.lower()

    def test_both_found_shows_comparison_table(self):
        df = pd.DataFrame([
            make_row(context_tag="batch_job",   exec_time=0.10, peak_mem=8_388_608),
            make_row(context_tag="import_flow", exec_time=0.25, peak_mem=16_777_216),
        ])
        _, out = _invoke(compare_context, df, ["batch_job", "import_flow"])
        assert "Context Comparison" in out
        assert "Average Metrics" in out

    def test_both_context_tags_appear_as_table_headers(self):
        df = pd.DataFrame([
            make_row(context_tag="ctx_alpha", exec_time=0.05),
            make_row(context_tag="ctx_beta",  exec_time=0.15),
        ])
        _, out = _invoke(compare_context, df, ["ctx_alpha", "ctx_beta"])
        assert "ctx_alpha" in out
        assert "ctx_beta" in out

    def test_uses_context_tag_column_not_function_name(self):
        # Row has function_name set but no context_tag matching "ctx_x" — must report missing
        df = pd.DataFrame([make_row(function_name="fn_decoy", exec_time=0.01)])
        _, out = _invoke(compare_context, df, ["ctx_x", "ctx_y"])
        assert "No records found" in out

    def test_run_count_shown_for_each_context(self):
        df = pd.DataFrame([
            make_row(context_tag="heavy_ctx", exec_time=0.5),
            make_row(context_tag="heavy_ctx", exec_time=0.6),
            make_row(context_tag="light_ctx", exec_time=0.1),
        ])
        _, out = _invoke(compare_context, df, ["heavy_ctx", "light_ctx"])
        assert "2 run" in out
        assert "1 run" in out

    def test_help_exits_cleanly(self):
        result = RUNNER.invoke(compare_context, ["--help"])
        assert result.exit_code == 0

    def test_help_shows_two_arguments(self):
        result = RUNNER.invoke(compare_context, ["--help"])
        assert "CONTEXT_A" in result.output
        assert "CONTEXT_B" in result.output


# ── TestAvgMetrics ────────────────────────────────────────────────────────────

class TestAvgMetrics:
    def test_empty_dataframe_returns_none_and_zero(self):
        df = pd.DataFrame(columns=["function_name", "execution_collector",
                                   "memory_collector", "cpu_collector"])
        avgs, count = _avg_metrics(df, "nonexistent")
        assert avgs is None
        assert count == 0

    def test_name_not_in_column_returns_none_and_zero(self):
        df = pd.DataFrame([make_row(function_name="fn_other")])
        avgs, count = _avg_metrics(df, "fn_absent")
        assert avgs is None
        assert count == 0

    def test_single_row_returns_correct_averages(self):
        df = pd.DataFrame([
            make_row(function_name="fn_single", exec_time=0.05, peak_mem=2_097_152,
                     avg_cpu=25.0, ram_delta=1.0),
        ])
        avgs, count = _avg_metrics(df, "fn_single")
        assert count == 1
        assert avgs is not None
        assert abs(avgs["exec_time"] - 0.05) < 1e-9
        assert abs(avgs["peak_mem"] - 2_097_152) < 1e-3
        assert abs(avgs["avg_cpu"] - 25.0) < 1e-9
        assert abs(avgs["ram_delta"] - 1.0) < 1e-9

    def test_multiple_rows_averaged_correctly(self):
        df = pd.DataFrame([
            make_row(function_name="fn_multi", exec_time=0.10, peak_mem=1_048_576,
                     avg_cpu=10.0, ram_delta=0.2),
            make_row(function_name="fn_multi", exec_time=0.20, peak_mem=2_097_152,
                     avg_cpu=20.0, ram_delta=0.4),
            make_row(function_name="fn_multi", exec_time=0.30, peak_mem=3_145_728,
                     avg_cpu=30.0, ram_delta=0.6),
        ])
        avgs, count = _avg_metrics(df, "fn_multi")
        assert count == 3
        assert abs(avgs["exec_time"] - 0.20) < 1e-9
        assert abs(avgs["peak_mem"] - 2_097_152) < 1e-3
        assert abs(avgs["avg_cpu"] - 20.0) < 1e-9
        assert abs(avgs["ram_delta"] - 0.4) < 1e-9

    def test_none_values_in_collectors_are_skipped(self):
        # Row with null JSON values — those keys should not contribute to average
        row = make_row(function_name="fn_null_vals", exec_time=0.08)
        # Overwrite collectors so exec_time is present but peak_memory is None
        row["memory_collector"] = json.dumps({"current_memory": None, "peak_memory": None})
        row["cpu_collector"]    = json.dumps({"avg_cpu_percentage": None, "ram_delta": None})
        df = pd.DataFrame([row])
        avgs, count = _avg_metrics(df, "fn_null_vals")
        assert count == 1
        assert avgs is not None
        assert abs(avgs["exec_time"] - 0.08) < 1e-9
        # Metrics with only None values should be returned as None (no valid samples)
        assert avgs["peak_mem"] is None
        assert avgs["avg_cpu"]  is None
        assert avgs["ram_delta"] is None

    def test_context_column_kwarg_filters_by_context_tag(self):
        df = pd.DataFrame([
            make_row(context_tag="my_ctx", exec_time=0.07, peak_mem=1_572_864,
                     avg_cpu=12.0, ram_delta=0.3),
        ])
        avgs, count = _avg_metrics(df, "my_ctx", column="context_tag")
        assert count == 1
        assert avgs is not None
        assert abs(avgs["exec_time"] - 0.07) < 1e-9

    def test_function_name_column_does_not_match_context_tag(self):
        # Default column="function_name" must not accidentally match a context_tag value
        df = pd.DataFrame([make_row(context_tag="fn_lookalike", exec_time=0.03)])
        avgs, count = _avg_metrics(df, "fn_lookalike")  # default column="function_name"
        assert avgs is None
        assert count == 0

    def test_malformed_json_collector_skipped_gracefully(self):
        row = make_row(function_name="fn_bad_json", exec_time=0.04)
        row["execution_collector"] = "not-json"
        df = pd.DataFrame([row])
        # Should not raise; exec_time will be None (skipped), others still parsed
        avgs, count = _avg_metrics(df, "fn_bad_json")
        assert count == 1
        assert avgs is not None
        assert avgs["exec_time"] is None
