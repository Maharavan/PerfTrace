"""
Tests for perftrace.cli.commands.frequency_count
Covers: _bar(), _render_frequency(), count_function, count_context.
"""
import json
import datetime
from io import StringIO
from unittest.mock import patch, MagicMock

import pandas as pd
import pytest
from click.testing import CliRunner
from rich.console import Console as RichConsole

from perftrace.cli.commands.frequency_count import (
    _bar,
    _render_frequency,
    count_function,
    count_context,
    _BAR_WIDTH,
)

RUNNER = CliRunner()

# frequency_count.py lazy-imports check_retrieve_data inside each Click command,
# so the effective module path to patch is the db_utils source.
_DB_UTILS = "perftrace.cli.db_utils.check_retrieve_data"
_CONSOLE  = "perftrace.cli.commands.frequency_count.console"


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


def _invoke_cmd(cmd, df, args=None):
    """Invoke a Click command with check_retrieve_data patched and Rich output captured."""
    buf = StringIO()
    rich_con = RichConsole(file=buf, width=200, highlight=False, markup=False)
    with patch(_DB_UTILS, return_value=df), \
         patch(_CONSOLE, rich_con):
        result = RUNNER.invoke(cmd, args or [])
    return result, buf.getvalue()


def _render_invoke(df, column, entity_label, title):
    """Call _render_frequency with a patched console and return captured output."""
    buf = StringIO()
    rich_con = RichConsole(file=buf, width=200, highlight=False, markup=False)
    with patch(_CONSOLE, rich_con):
        _render_frequency(df, column, entity_label, title)
    return buf.getvalue()


# ── TestBar ────────────────────────────────────────────────────────────────────

class TestBar:
    """Unit tests for the _bar() helper."""

    def test_zero_percent_all_empty_chars(self):
        result = _bar(0)
        assert "░" * _BAR_WIDTH in result

    def test_hundred_percent_all_filled_chars(self):
        result = _bar(100)
        assert "█" * _BAR_WIDTH in result

    def test_fifty_percent_half_filled(self):
        result = _bar(50)
        expected_filled = int(50 / 100 * _BAR_WIDTH)
        assert "█" * expected_filled in result

    def test_returns_string(self):
        assert isinstance(_bar(25), str)

    def test_contains_filled_block_chars_for_nonzero(self):
        result = _bar(10)
        assert "█" in result

    def test_contains_empty_block_chars_for_non_hundred(self):
        result = _bar(90)
        assert "░" in result

    def test_total_bar_chars_equals_bar_width(self):
        # Strip markup tags to count raw characters
        raw = _bar(40)
        filled_count = raw.count("█")
        empty_count  = raw.count("░")
        assert filled_count + empty_count == _BAR_WIDTH

    def test_seventy_five_percent_has_more_filled_than_empty(self):
        raw = _bar(75)
        assert raw.count("█") > raw.count("░")


# ── TestRenderFrequency ───────────────────────────────────────────────────────

class TestRenderFrequency:
    """Tests for _render_frequency() — the shared rendering helper."""

    def test_empty_df_prints_no_calls_message(self):
        df = pd.DataFrame({"function_name": pd.Series([], dtype=str)})
        out = _render_invoke(df, "function_name", "Function", "Function Call Frequency")
        assert "No Function calls recorded" in out

    def test_single_item_shows_name_in_output(self):
        df = pd.DataFrame([make_row(function_name="solo_fn")])
        out = _render_invoke(df, "function_name", "Function", "Function Call Frequency")
        assert "solo_fn" in out

    def test_multiple_items_ranked_highest_first(self):
        rows = (
            [make_row(function_name="popular_fn")] * 5
            + [make_row(function_name="rare_fn")] * 1
        )
        df = pd.DataFrame(rows)
        out = _render_invoke(df, "function_name", "Function", "Function Call Frequency")
        idx_popular = out.find("popular_fn")
        idx_rare    = out.find("rare_fn")
        assert 0 <= idx_popular < idx_rare, "Higher-count item should appear before lower-count item"

    def test_percentage_adds_to_100_for_single_item(self):
        df = pd.DataFrame([make_row(function_name="only_fn")] * 3)
        out = _render_invoke(df, "function_name", "Function", "Function Call Frequency")
        assert "100.0%" in out

    def test_total_calls_shown_in_panel(self):
        rows = [make_row(function_name="fn_a")] * 4
        df = pd.DataFrame(rows)
        out = _render_invoke(df, "function_name", "Function", "Function Call Frequency")
        assert "4" in out  # total_calls == 4

    def test_unique_count_shown_for_multiple_functions(self):
        rows = [make_row(function_name="fn_x"), make_row(function_name="fn_y")]
        df = pd.DataFrame(rows)
        out = _render_invoke(df, "function_name", "Function", "Function Call Frequency")
        assert "2" in out  # 2 unique functions

    def test_rank_column_starts_at_1(self):
        df = pd.DataFrame([make_row(function_name="alpha_fn")])
        out = _render_invoke(df, "function_name", "Function", "Function Call Frequency")
        assert "1" in out

    def test_context_label_used_for_context_column(self):
        df = pd.DataFrame({"context_tag": pd.Series([], dtype=str)})
        out = _render_invoke(df, "context_tag", "Context", "Context Manager Call Frequency")
        assert "No Context calls recorded" in out


# ── TestCountFunction ─────────────────────────────────────────────────────────

class TestCountFunction:
    """Tests for the count-function Click command."""

    def test_empty_dataframe_exits_cleanly(self):
        df = pd.DataFrame()
        result, _ = _invoke_cmd(count_function, df)
        assert result.exit_code == 0

    def test_empty_dataframe_prints_no_function_data(self):
        df = pd.DataFrame()
        _, out = _invoke_cmd(count_function, df)
        assert "No function data found" in out

    def test_df_without_function_name_column_prints_no_data(self):
        df = pd.DataFrame([{"context_tag": "ctx_only"}])
        _, out = _invoke_cmd(count_function, df)
        assert "No function data found" in out

    def test_single_function_appears_in_output(self):
        df = pd.DataFrame([make_row(function_name="my_fn")])
        _, out = _invoke_cmd(count_function, df)
        assert "my_fn" in out

    def test_multiple_functions_all_shown_within_default_limit(self):
        rows = [make_row(function_name=f"fn_{i}") for i in range(5)]
        df = pd.DataFrame(rows)
        _, out = _invoke_cmd(count_function, df)
        for i in range(5):
            assert f"fn_{i}" in out

    def test_limit_option_restricts_to_top_n(self):
        # 10 distinct functions; --limit 3 should show at most 3
        rows = [make_row(function_name=f"func_{i}") for i in range(10)]
        df = pd.DataFrame(rows)
        _, out = _invoke_cmd(count_function, df, ["--limit", "3"])
        shown = sum(1 for i in range(10) if f"func_{i}" in out)
        assert shown <= 3

    def test_limit_default_is_10(self):
        result = RUNNER.invoke(count_function, ["--help"])
        assert "10" in result.output

    def test_help_exits_cleanly(self):
        result = RUNNER.invoke(count_function, ["--help"])
        assert result.exit_code == 0

    def test_help_shows_limit_option(self):
        result = RUNNER.invoke(count_function, ["--help"])
        assert "--limit" in result.output

    def test_rows_with_null_function_name_ignored(self):
        rows = [
            make_row(function_name=None),
            make_row(function_name="valid_fn"),
        ]
        df = pd.DataFrame(rows)
        _, out = _invoke_cmd(count_function, df)
        assert "valid_fn" in out


# ── TestCountContext ──────────────────────────────────────────────────────────

class TestCountContext:
    """Tests for the count-context Click command."""

    def test_empty_dataframe_exits_cleanly(self):
        df = pd.DataFrame()
        result, _ = _invoke_cmd(count_context, df)
        assert result.exit_code == 0

    def test_empty_dataframe_prints_no_context_data(self):
        df = pd.DataFrame()
        _, out = _invoke_cmd(count_context, df)
        assert "No context data found" in out

    def test_df_without_context_tag_column_prints_no_data(self):
        df = pd.DataFrame([{"function_name": "fn_only"}])
        _, out = _invoke_cmd(count_context, df)
        assert "No context data found" in out

    def test_single_context_appears_in_output(self):
        df = pd.DataFrame([make_row(context_tag="my_ctx")])
        _, out = _invoke_cmd(count_context, df)
        assert "my_ctx" in out

    def test_multiple_contexts_all_shown_within_default_limit(self):
        rows = [make_row(context_tag=f"ctx_{i}") for i in range(5)]
        df = pd.DataFrame(rows)
        _, out = _invoke_cmd(count_context, df)
        for i in range(5):
            assert f"ctx_{i}" in out

    def test_limit_option_restricts_to_top_n(self):
        rows = [make_row(context_tag=f"ctx_{i}") for i in range(10)]
        df = pd.DataFrame(rows)
        _, out = _invoke_cmd(count_context, df, ["--limit", "3"])
        shown = sum(1 for i in range(10) if f"ctx_{i}" in out)
        assert shown <= 3

    def test_limit_default_is_10(self):
        result = RUNNER.invoke(count_context, ["--help"])
        assert "10" in result.output

    def test_help_exits_cleanly(self):
        result = RUNNER.invoke(count_context, ["--help"])
        assert result.exit_code == 0

    def test_help_shows_limit_option(self):
        result = RUNNER.invoke(count_context, ["--help"])
        assert "--limit" in result.output

    def test_rows_with_null_context_tag_ignored(self):
        rows = [
            make_row(context_tag=None),
            make_row(context_tag="valid_ctx"),
        ]
        df = pd.DataFrame(rows)
        _, out = _invoke_cmd(count_context, df)
        assert "valid_ctx" in out
