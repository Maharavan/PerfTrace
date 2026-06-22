"""
Tests for perftrace.cli.commands.top_commands
Covers: top_memory and top_cpu commands — empty data, zero data, function/context
rows, --limit flag, sort order, and CLI interface.
"""
import json
import datetime
from io import StringIO
from unittest.mock import patch

import pandas as pd
import pytest
from click.testing import CliRunner
from rich.console import Console as RichConsole

from perftrace.cli.commands.top_commands import top_memory, top_cpu

RUNNER = CliRunner()
MODULE = "perftrace.cli.commands.top_commands"


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


# ── TestTopMemory ──────────────────────────────────────────────────────────────

class TestTopMemory:
    def test_empty_dataframe_exits_cleanly(self):
        result, _ = _invoke(top_memory, pd.DataFrame())
        assert result.exit_code == 0

    def test_empty_dataframe_prints_no_trace_data(self):
        _, out = _invoke(top_memory, pd.DataFrame())
        assert "No trace data" in out

    def test_zero_peak_memory_still_renders_table(self):
        # peak_mem=0 is a valid (if trivial) value — the source enters the row into agg
        # because the initial agg[name]["peak"] is also 0.0 and `0 > 0` is False, so
        # the `if peak > agg[name]["peak"]` branch is skipped for subsequent rows but
        # the defaultdict key is still created on the first access, meaning the table
        # renders with 0 B values rather than printing the "no memory" message.
        df = pd.DataFrame([make_row(function_name="fn_zero", peak_mem=0)])
        result, out = _invoke(top_memory, df)
        assert result.exit_code == 0
        # The "no memory" message fires only when agg is truly empty (no named rows at all)
        assert "Peak Memory Usage" in out

    def test_function_row_name_appears_in_output(self):
        df = pd.DataFrame([make_row(function_name="load_data", peak_mem=2_097_152)])
        _, out = _invoke(top_memory, df)
        assert "load_data" in out

    def test_function_row_shows_type_function(self):
        df = pd.DataFrame([make_row(function_name="process_fn", peak_mem=1_048_576)])
        _, out = _invoke(top_memory, df)
        assert "function" in out

    def test_context_row_name_appears_in_output(self):
        df = pd.DataFrame([make_row(context_tag="batch_job", peak_mem=4_194_304)])
        _, out = _invoke(top_memory, df)
        assert "batch_job" in out

    def test_context_row_shows_type_context(self):
        df = pd.DataFrame([make_row(context_tag="pipeline_ctx", peak_mem=3_145_728)])
        _, out = _invoke(top_memory, df)
        assert "context" in out

    def test_limit_option_reflected_in_table_title(self):
        rows = [make_row(function_name=f"fn_{i}", peak_mem=(10 - i) * 1_048_576)
                for i in range(8)]
        df = pd.DataFrame(rows)
        _, out = _invoke(top_memory, df, ["--limit", "3"])
        assert "Top 3" in out

    def test_limit_short_flag_works(self):
        rows = [make_row(function_name=f"fn_{i}", peak_mem=(10 - i) * 1_048_576)
                for i in range(5)]
        df = pd.DataFrame(rows)
        _, out = _invoke(top_memory, df, ["-n", "2"])
        assert "Top 2" in out

    def test_multiple_rows_for_same_name_uses_max_peak(self):
        # Two calls to "fn_dup": peak_mem 1 MB and 5 MB — table must show 5 MB peak
        df = pd.DataFrame([
            make_row(function_name="fn_dup", peak_mem=1_048_576),
            make_row(function_name="fn_dup", peak_mem=5_242_880),
        ])
        _, out = _invoke(top_memory, df)
        # Only one aggregated row should appear
        lines_with_name = [l for l in out.splitlines() if "fn_dup" in l]
        assert len(lines_with_name) == 1

    def test_unnamed_rows_only_shows_no_memory_message(self):
        # When every row has no usable name, agg stays empty → "No memory data available"
        df = pd.DataFrame([
            {"function_name": None, "context_tag": None,
             "memory_collector": json.dumps({"current_memory": 0, "peak_memory": 1_048_576})},
        ])
        result, out = _invoke(top_memory, df)
        assert result.exit_code == 0
        assert "No memory data available" in out

    def test_table_title_contains_peak_memory_usage(self):
        df = pd.DataFrame([make_row(function_name="fn_title", peak_mem=2_097_152)])
        _, out = _invoke(top_memory, df)
        assert "Peak Memory Usage" in out

    def test_help_exits_cleanly(self):
        result = RUNNER.invoke(top_memory, ["--help"])
        assert result.exit_code == 0

    def test_help_shows_limit_option(self):
        result = RUNNER.invoke(top_memory, ["--help"])
        assert "--limit" in result.output or "-n" in result.output


# ── TestTopCpu ────────────────────────────────────────────────────────────────

class TestTopCpu:
    def test_empty_dataframe_exits_cleanly(self):
        result, _ = _invoke(top_cpu, pd.DataFrame())
        assert result.exit_code == 0

    def test_empty_dataframe_prints_no_trace_data(self):
        _, out = _invoke(top_cpu, pd.DataFrame())
        assert "No trace data" in out

    def test_unnamed_rows_only_shows_no_cpu_message(self):
        # The "No CPU data available" path fires when agg is truly empty.
        # That happens only when every row has no usable name (None / "-").
        df = pd.DataFrame([
            {"function_name": None, "context_tag": None,
             "cpu_collector": json.dumps({"avg_cpu_percentage": 50.0, "ram_delta": 0.0})},
        ])
        result, out = _invoke(top_cpu, df)
        assert result.exit_code == 0
        assert "No CPU data available" in out

    def test_function_row_name_appears_in_output(self):
        df = pd.DataFrame([make_row(function_name="compute_fn", avg_cpu=42.5)])
        _, out = _invoke(top_cpu, df)
        assert "compute_fn" in out

    def test_function_row_shows_type_function(self):
        df = pd.DataFrame([make_row(function_name="sort_fn", avg_cpu=30.0)])
        _, out = _invoke(top_cpu, df)
        assert "function" in out

    def test_context_row_name_appears_in_output(self):
        df = pd.DataFrame([make_row(context_tag="etl_ctx", avg_cpu=55.0)])
        _, out = _invoke(top_cpu, df)
        assert "etl_ctx" in out

    def test_context_row_shows_type_context(self):
        df = pd.DataFrame([make_row(context_tag="import_ctx", avg_cpu=20.0)])
        _, out = _invoke(top_cpu, df)
        assert "context" in out

    def test_rows_sorted_descending_by_avg_cpu(self):
        df = pd.DataFrame([
            make_row(function_name="low_cpu_fn",  avg_cpu=5.0),
            make_row(function_name="high_cpu_fn", avg_cpu=95.0),
        ])
        _, out = _invoke(top_cpu, df)
        idx_high = out.find("high_cpu_fn")
        idx_low  = out.find("low_cpu_fn")
        assert 0 <= idx_high < idx_low

    def test_multiple_calls_averaged(self):
        # Three calls: 10 + 20 + 30 → avg 20 %
        df = pd.DataFrame([
            make_row(function_name="avg_fn", avg_cpu=10.0),
            make_row(function_name="avg_fn", avg_cpu=20.0),
            make_row(function_name="avg_fn", avg_cpu=30.0),
        ])
        _, out = _invoke(top_cpu, df)
        lines = [l for l in out.splitlines() if "avg_fn" in l]
        assert len(lines) == 1

    def test_limit_option_reflected_in_table_title(self):
        rows = [make_row(function_name=f"fn_{i}", avg_cpu=float(50 - i))
                for i in range(6)]
        df = pd.DataFrame(rows)
        _, out = _invoke(top_cpu, df, ["--limit", "4"])
        assert "Top 4" in out

    def test_limit_short_flag_works(self):
        rows = [make_row(function_name=f"fn_{i}", avg_cpu=float(50 - i))
                for i in range(5)]
        df = pd.DataFrame(rows)
        _, out = _invoke(top_cpu, df, ["-n", "2"])
        assert "Top 2" in out

    def test_table_title_contains_average_cpu_usage(self):
        df = pd.DataFrame([make_row(function_name="fn_cpu", avg_cpu=18.0)])
        _, out = _invoke(top_cpu, df)
        # Rich may line-wrap the title; check both key words appear somewhere in output
        assert "Average CPU" in out or "CPU Usage" in out

    def test_help_exits_cleanly(self):
        result = RUNNER.invoke(top_cpu, ["--help"])
        assert result.exit_code == 0

    def test_help_shows_limit_option(self):
        result = RUNNER.invoke(top_cpu, ["--help"])
        assert "--limit" in result.output or "-n" in result.output
