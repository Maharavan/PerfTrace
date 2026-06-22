"""
Tests for perftrace.cli.commands.io_report
Covers: aggregation logic, sorting, --limit flag, edge cases, and CLI interface.
"""
import json
from io import StringIO
from unittest.mock import patch

import pandas as pd
import pytest
from click.testing import CliRunner
from rich.console import Console as RichConsole

from perftrace.cli.commands.io_report import io_report

RUNNER = CliRunner()


# ── Helpers ──────────────────────────────────────────────────────────────────

def _make_io(read_bytes=0, write_bytes=0, read_count=0, write_count=0, other_count=0):
    return json.dumps({
        "read_bytes": read_bytes,
        "write_bytes": write_bytes,
        "read_count": read_count,
        "write_count": write_count,
        "other_count": other_count,
    })


def _invoke(df, args=None):
    """Invoke io_report with Rich output captured to a plain string."""
    buf = StringIO()
    rich_con = RichConsole(file=buf, width=200, highlight=False, markup=False)
    with patch("perftrace.cli.commands.io_report.check_retrieve_data", return_value=df), \
         patch("perftrace.cli.commands.io_report.console", rich_con):
        result = RUNNER.invoke(io_report, args or [])
    return result, buf.getvalue()


# ── Empty / no-data cases ────────────────────────────────────────────────────

class TestIoReportNoData:
    def test_empty_dataframe_exits_cleanly(self):
        result, _ = _invoke(pd.DataFrame())
        assert result.exit_code == 0

    def test_empty_dataframe_prints_no_data_message(self):
        _, out = _invoke(pd.DataFrame())
        assert "No trace data" in out

    def test_all_zero_io_shows_collector_warning(self):
        df = pd.DataFrame([{
            "function_name": "fn_zero", "context_tag": None,
            "file_io_collector": _make_io(),
        }])
        result, out = _invoke(df)
        assert result.exit_code == 0
        assert "No file I/O data" in out

    def test_rows_with_empty_name_skipped(self):
        df = pd.DataFrame([
            {"function_name": None, "context_tag": None,
             "file_io_collector": _make_io(read_bytes=1000)},
            {"function_name": "-", "context_tag": None,
             "file_io_collector": _make_io(read_bytes=1000)},
        ])
        _, out = _invoke(df)
        assert "No file I/O data" in out


# ── Function rows ─────────────────────────────────────────────────────────────

class TestIoReportFunctions:
    def test_function_name_appears_in_output(self):
        df = pd.DataFrame([{
            "function_name": "load_data",
            "context_tag": None,
            "file_io_collector": _make_io(read_bytes=4096, read_count=8),
        }])
        _, out = _invoke(df)
        assert "load_data" in out

    def test_kind_column_shows_function(self):
        df = pd.DataFrame([{
            "function_name": "proc_fn",
            "context_tag": None,
            "file_io_collector": _make_io(read_bytes=2048, read_count=4),
        }])
        _, out = _invoke(df)
        assert "function" in out

    def test_multiple_calls_aggregated_into_one_row(self):
        df = pd.DataFrame([
            {"function_name": "agg_fn", "context_tag": None,
             "file_io_collector": _make_io(read_bytes=1000, read_count=2)},
            {"function_name": "agg_fn", "context_tag": None,
             "file_io_collector": _make_io(read_bytes=2000, read_count=3)},
        ])
        _, out = _invoke(df)
        lines_with_name = [l for l in out.splitlines() if "agg_fn" in l]
        assert len(lines_with_name) == 1

    def test_write_bytes_nonzero_appears(self):
        df = pd.DataFrame([{
            "function_name": "writer_fn",
            "context_tag": None,
            "file_io_collector": _make_io(write_bytes=8192, write_count=5),
        }])
        _, out = _invoke(df)
        assert "writer_fn" in out


# ── Context rows ──────────────────────────────────────────────────────────────

class TestIoReportContexts:
    def test_context_tag_appears_in_output(self):
        df = pd.DataFrame([{
            "function_name": None,
            "context_tag": "batch_job",
            "file_io_collector": _make_io(read_bytes=16384, read_count=20),
        }])
        _, out = _invoke(df)
        assert "batch_job" in out

    def test_kind_column_shows_context(self):
        df = pd.DataFrame([{
            "function_name": None,
            "context_tag": "ctx_pipeline",
            "file_io_collector": _make_io(read_bytes=5000, read_count=10),
        }])
        _, out = _invoke(df)
        assert "context" in out


# ── Mixed function + context ──────────────────────────────────────────────────

class TestIoReportMixed:
    def test_both_function_and_context_shown(self):
        df = pd.DataFrame([
            {"function_name": "fn_mix", "context_tag": None,
             "file_io_collector": _make_io(read_bytes=3000, read_count=6)},
            {"function_name": None, "context_tag": "ctx_mix",
             "file_io_collector": _make_io(write_bytes=1500, write_count=3)},
        ])
        _, out = _invoke(df)
        assert "fn_mix" in out
        assert "ctx_mix" in out

    def test_sorted_by_total_bytes_descending(self):
        df = pd.DataFrame([
            {"function_name": "small_fn", "context_tag": None,
             "file_io_collector": _make_io(read_bytes=100)},
            {"function_name": "big_fn", "context_tag": None,
             "file_io_collector": _make_io(read_bytes=100_000)},
        ])
        _, out = _invoke(df)
        idx_big = out.find("big_fn")
        idx_small = out.find("small_fn")
        assert 0 <= idx_big < idx_small

    def test_function_preferred_when_both_fields_set(self):
        df = pd.DataFrame([{
            "function_name": "fn_both",
            "context_tag": "ctx_both",
            "file_io_collector": _make_io(read_bytes=1024, read_count=2),
        }])
        _, out = _invoke(df)
        # function_name wins — row is keyed by function_name
        assert "fn_both" in out


# ── --limit flag ───────────────────────────────────────────────────────────────

class TestIoReportLimit:
    def test_limit_applies_to_rows_shown(self):
        rows = [
            {"function_name": f"fn_{i:02d}", "context_tag": None,
             "file_io_collector": _make_io(read_bytes=(100 - i) * 1000)}
            for i in range(10)
        ]
        df = pd.DataFrame(rows)
        _, out = _invoke(df, ["--limit", "3"])
        assert "Top 3" in out

    def test_limit_short_flag_works(self):
        rows = [
            {"function_name": f"fn_{i}", "context_tag": None,
             "file_io_collector": _make_io(read_bytes=(10 - i) * 500)}
            for i in range(5)
        ]
        df = pd.DataFrame(rows)
        _, out = _invoke(df, ["-n", "2"])
        assert "Top 2" in out

    def test_default_limit_is_20(self):
        result = RUNNER.invoke(io_report, ["--help"])
        assert "20" in result.output

    def test_limit_title_reflects_value(self):
        df = pd.DataFrame([
            {"function_name": f"fn_{i}", "context_tag": None,
             "file_io_collector": _make_io(read_bytes=(5 - i) * 200)}
            for i in range(5)
        ])
        _, out = _invoke(df, ["--limit", "5"])
        assert "Top 5" in out


# ── Edge cases ────────────────────────────────────────────────────────────────

class TestIoReportEdgeCases:
    def test_none_io_collector_treated_as_zero(self):
        df = pd.DataFrame([
            {"function_name": "fn_null", "context_tag": None,
             "file_io_collector": None},
            {"function_name": "fn_good", "context_tag": None,
             "file_io_collector": _make_io(read_bytes=1024, read_count=1)},
        ])
        result, _ = _invoke(df)
        assert result.exit_code == 0

    def test_invalid_numeric_value_skipped_gracefully(self):
        df = pd.DataFrame([
            {"function_name": "fn_bad", "context_tag": None,
             "file_io_collector": json.dumps({"read_bytes": "oops"})},
            {"function_name": "fn_ok", "context_tag": None,
             "file_io_collector": _make_io(read_bytes=2048, read_count=3)},
        ])
        result, out = _invoke(df)
        assert result.exit_code == 0
        assert "fn_ok" in out

    def test_malformed_json_collector_skipped(self):
        df = pd.DataFrame([
            {"function_name": "fn_corrupt", "context_tag": None,
             "file_io_collector": "not-json-at-all"},
            {"function_name": "fn_valid", "context_tag": None,
             "file_io_collector": _make_io(read_bytes=512, read_count=1)},
        ])
        result, _ = _invoke(df)
        assert result.exit_code == 0

    def test_single_entry_shows_rank_1(self):
        df = pd.DataFrame([{
            "function_name": "only_fn",
            "context_tag": None,
            "file_io_collector": _make_io(read_bytes=4096, read_count=5),
        }])
        _, out = _invoke(df)
        assert "only_fn" in out
        assert "1" in out


# ── CLI interface ─────────────────────────────────────────────────────────────

class TestIoReportCli:
    def test_help_exits_cleanly(self):
        result = RUNNER.invoke(io_report, ["--help"])
        assert result.exit_code == 0

    def test_help_shows_command_description(self):
        result = RUNNER.invoke(io_report, ["--help"])
        assert "I/O" in result.output or "io" in result.output.lower()

    def test_help_shows_limit_option(self):
        result = RUNNER.invoke(io_report, ["--help"])
        assert "--limit" in result.output or "-n" in result.output

    def test_invalid_limit_type_fails(self):
        result = RUNNER.invoke(io_report, ["--limit", "abc"])
        assert result.exit_code != 0
