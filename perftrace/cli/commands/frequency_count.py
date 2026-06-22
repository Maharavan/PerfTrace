import click
from collections import Counter
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

_BAR_WIDTH = 20


def _bar(pct):
    filled = int(pct / 100 * _BAR_WIDTH)
    return f"[cyan]{'█' * filled}[/cyan][dim]{'░' * (_BAR_WIDTH - filled)}[/dim]"


def _render_frequency(df, column, entity_label, title):
    items = df[column].dropna().tolist()
    if not items:
        console.print(f"[yellow]No {entity_label} calls recorded.[/yellow]")
        return

    counter     = Counter(items)
    total_calls = sum(counter.values())
    unique_n    = len(counter)

    console.print(Panel.fit(
        f"[bold cyan]{title}[/bold cyan]\n"
        f"[dim]Total calls: [white]{total_calls:,}[/white]   "
        f"Unique {entity_label}s: [white]{unique_n:,}[/white][/dim]",
        border_style="cyan",
        padding=(0, 2),
    ))

    t = Table(
        show_header=True,
        header_style="bold cyan",
        show_lines=False,
        border_style="dim cyan",
        padding=(0, 1),
        expand=True,
    )
    t.add_column("#",           justify="right", style="dim",    width=4,  no_wrap=True)
    t.add_column(entity_label,  style="green",   no_wrap=True,   min_width=24)
    t.add_column("Calls",       justify="right", style="white",  width=8,  no_wrap=True)
    t.add_column("%",           justify="right", style="yellow", width=7,  no_wrap=True)
    t.add_column("Distribution",                 no_wrap=True,   min_width=24)

    for rank, (name, count) in enumerate(counter.most_common(), start=1):
        pct = count / total_calls * 100
        t.add_row(
            str(rank),
            name,
            f"{count:,}",
            f"{pct:.1f}%",
            _bar(pct),
        )

    console.print(t)


@click.command(name="count-function")
@click.option("--limit", type=int, default=10, show_default=True,
              help="Show top N functions by call count.")
def count_function(limit):
    """Show function call frequency with distribution bars."""
    from perftrace.cli.db_utils import check_retrieve_data
    df = check_retrieve_data()

    if df.empty or "function_name" not in df.columns:
        console.print("[yellow]No function data found.[/yellow]")
        return

    df = df.dropna(subset=["function_name"])
    if len(df) > limit:
        top = df["function_name"].value_counts().nlargest(limit).index
        df  = df[df["function_name"].isin(top)]

    _render_frequency(df, "function_name", "Function", "Function Call Frequency")


@click.command(name="count-context")
@click.option("--limit", type=int, default=10, show_default=True,
              help="Show top N context managers by call count.")
def count_context(limit):
    """Show context manager call frequency with distribution bars."""
    from perftrace.cli.db_utils import check_retrieve_data
    df = check_retrieve_data()

    if df.empty or "context_tag" not in df.columns:
        console.print("[yellow]No context data found.[/yellow]")
        return

    df = df.dropna(subset=["context_tag"])
    if len(df) > limit:
        top = df["context_tag"].value_counts().nlargest(limit).index
        df  = df[df["context_tag"].isin(top)]

    _render_frequency(df, "context_tag", "Context", "Context Manager Call Frequency")
