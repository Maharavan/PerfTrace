"""
Tests for perftrace.cli.commands.exceptions
(Named test_exceptions_cmd to avoid shadowing Python's built-in exceptions module.)
Covers: empty DataFrame, no exceptions in data, single/multiple exception rows,
function vs. context kind labels, message truncation, --limit flag, and CLI interface.
"""
import json
import datetime
from io import StringIO
from unittest.mock import patch

import pandas as pd
import pytest
from click.testing import CliRunner
from rich.console import Console as RichConsole

from perftrace.cli.commands.exceptions import exceptions

RUNNER = CliRunner()
MODULE = "perftrace.cli.commands.exceptions"


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


def _invoke(df, args=None):
    buf = StringIO()
    rich_con = RichConsole(file=buf, width=200, highlight=False, markup=False)
    with patch(f"{MODULE}.check_retrieve_data", return_value=df), \
         patch(f"{MODULE}.console", rich_con):
        result = RUNNER.invoke(exceptions, args or [])
    return result, buf.getvalue()


# ── TestExceptionsNoData ──────────────────────────────────────────────────────

class TestExceptionsNoData:
    def test_empty_dataframe_exits_cleanly(self):
        result, _ = _invoke(pd.DataFrame())
        assert result.exit_code == 0

    def test_empty_dataframe_prints_no_trace_data(self):
        _, out = _invoke(pd.DataFrame())
        assert "No trace data" in out

    def test_all_occurred_false_prints_success_message(self):
        df = pd.DataFrame([
            make_row(function_name="fn_ok", exc_occurred=False),
            make_row(function_name="fn_also_ok", exc_occurred=False),
        ])
        _, out = _invoke(df)
        assert "No exceptions found" in out

    def test_all_occurred_false_does_not_show_table(self):
        df = pd.DataFrame([make_row(function_name="clean_fn", exc_occurred=False)])
        _, out = _invoke(df)
        assert "Exception Traces" not in out

    def test_success_message_contains_all_traces_completed(self):
        df = pd.DataFrame([make_row(function_name="success_fn", exc_occurred=False)])
        _, out = _invoke(df)
        assert "all traces completed successfully" in out

    def test_none_exc_collector_treated_as_no_exception(self):
        # When exception_collector is None, _parse_json returns {} and occurred defaults False
        row = make_row(function_name="fn_null_exc")
        row["exception_collector"] = None
        df = pd.DataFrame([row])
        result, out = _invoke(df)
        assert result.exit_code == 0
        assert "No exceptions found" in out


# ── TestExceptionsWithData ────────────────────────────────────────────────────

class TestExceptionsWithData:
    def test_single_exception_function_row_shows_table(self):
        df = pd.DataFrame([
            make_row(function_name="failing_fn", exc_occurred=True,
                     exc_type="ValueError", exc_msg="bad input"),
        ])
        _, out = _invoke(df)
        assert "Exception Traces" in out

    def test_exception_function_name_appears_in_output(self):
        df = pd.DataFrame([
            make_row(function_name="exploding_fn", exc_occurred=True,
                     exc_type="RuntimeError", exc_msg="boom"),
        ])
        _, out = _invoke(df)
        assert "exploding_fn" in out

    def test_exception_context_tag_appears_in_output(self):
        df = pd.DataFrame([
            make_row(context_tag="risky_ctx", exc_occurred=True,
                     exc_type="KeyError", exc_msg="missing key"),
        ])
        _, out = _invoke(df)
        assert "risky_ctx" in out

    def test_function_row_shows_kind_function(self):
        df = pd.DataFrame([
            make_row(function_name="fn_kind", exc_occurred=True,
                     exc_type="TypeError", exc_msg="wrong type"),
        ])
        _, out = _invoke(df)
        assert "function" in out

    def test_context_row_shows_kind_context(self):
        df = pd.DataFrame([
            make_row(context_tag="ctx_kind", exc_occurred=True,
                     exc_type="IOError", exc_msg="file not found"),
        ])
        _, out = _invoke(df)
        assert "context" in out

    def test_exception_type_appears_in_output(self):
        df = pd.DataFrame([
            make_row(function_name="typed_fn", exc_occurred=True,
                     exc_type="ZeroDivisionError", exc_msg="division by zero"),
        ])
        _, out = _invoke(df)
        assert "ZeroDivisionError" in out

    def test_multiple_exception_rows_all_appear(self):
        df = pd.DataFrame([
            make_row(function_name="fn_one", exc_occurred=True,
                     exc_type="ValueError", exc_msg="err one"),
            make_row(function_name="fn_two", exc_occurred=True,
                     exc_type="KeyError", exc_msg="err two"),
            make_row(function_name="fn_three", exc_occurred=False),
        ])
        _, out = _invoke(df)
        assert "fn_one" in out
        assert "fn_two" in out
        assert "fn_three" not in out

    def test_record_count_shown_in_table_title(self):
        df = pd.DataFrame([
            make_row(function_name="fn_a", exc_occurred=True,
                     exc_type="ValueError", exc_msg="err a"),
            make_row(function_name="fn_b", exc_occurred=True,
                     exc_type="TypeError", exc_msg="err b"),
        ])
        _, out = _invoke(df)
        # Title format: "Exception Traces (2 record(s))"
        assert "2 record" in out

    def test_message_truncated_to_80_chars(self):
        long_msg = "A" * 100
        df = pd.DataFrame([
            make_row(function_name="long_msg_fn", exc_occurred=True,
                     exc_type="RuntimeError", exc_msg=long_msg),
        ])
        _, out = _invoke(df)
        # The 80-char truncated message must appear; the 100-char original must not appear intact
        assert "A" * 80 in out
        assert "A" * 81 not in out

    def test_short_message_not_padded(self):
        short_msg = "short error"
        df = pd.DataFrame([
            make_row(function_name="short_fn", exc_occurred=True,
                     exc_type="Exception", exc_msg=short_msg),
        ])
        _, out = _invoke(df)
        assert short_msg in out

    def test_limit_restricts_rows_shown(self):
        rows = [
            make_row(function_name=f"fn_{i}", exc_occurred=True,
                     exc_type="Error", exc_msg=f"msg {i}")
            for i in range(10)
        ]
        df = pd.DataFrame(rows)
        _, out = _invoke(df, ["--limit", "3"])
        # Title must report 3 records, not 10
        assert "3 record" in out

    def test_limit_short_flag_works(self):
        rows = [
            make_row(function_name=f"fn_{i}", exc_occurred=True,
                     exc_type="Error", exc_msg=f"msg {i}")
            for i in range(6)
        ]
        df = pd.DataFrame(rows)
        _, out = _invoke(df, ["-n", "2"])
        assert "2 record" in out

    def test_help_exits_cleanly(self):
        result = RUNNER.invoke(exceptions, ["--help"])
        assert result.exit_code == 0

    def test_help_shows_limit_option(self):
        result = RUNNER.invoke(exceptions, ["--help"])
        assert "--limit" in result.output or "-n" in result.output

    def test_help_shows_default_limit_of_50(self):
        result = RUNNER.invoke(exceptions, ["--help"])
        assert "50" in result.output
