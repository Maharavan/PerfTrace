import click
from collections import Counter
from rich import print
from rich.table import Table
from perftrace.cli.db_utils import check_retrieve_data


@click.command(name="count-function")
@click.option(
    "--limit",
    type=int,
    default=10,
    help="Show top N functions by call count"
)
def count_function(limit):
    """Shows function call frequency"""

    print("[bold cyan]PerfTrace CLI[/bold cyan] - Unified Performance Tracing")

    df = check_retrieve_data()

    if df.empty or "function_name" not in df.columns:
        print("[yellow]No function data found[/yellow]")
        return

    functions = df["function_name"].dropna().tolist()

    if not functions:
        print("[yellow]No function calls recorded[/yellow]")
        return

    counter = Counter(functions)

    total_calls = sum(counter.values())
    unique_funcs = len(counter)

    print("\n[bold blue]Function Call Summary[/bold blue]")
    print(f"[yellow]Total Function Calls:[/yellow] {total_calls}")
    print(f"[yellow]Unique Functions:[/yellow] {unique_funcs}")

    table = Table(
        title="Top Functions by Call Count",
        show_lines=False,
        header_style="bold magenta"
    )

    table.add_column("Rank", justify="right")
    table.add_column("Function Name", justify="left", style="cyan")
    table.add_column("Calls", justify="right", style="green")
    table.add_column("Percentage", justify="right", style="yellow")

    for idx, (func, count) in enumerate(counter.most_common(limit), start=1):
        percent = (count / total_calls) * 100
        table.add_row(
            str(idx),
            func,
            str(count),
            f"{percent:.1f}%"
        )

    print(table)


@click.command(name="count-context")
@click.option(
    "--limit",
    type=int,
    default=10,
    help="Show top N functions by call count"
)
def count_context(limit):
    """Shows function call frequency"""

    print("[bold cyan]PerfTrace CLI[/bold cyan] - Unified Performance Tracing")

    df = check_retrieve_data()

    if df.empty or "context_tag" not in df.columns:
        print("[yellow]No function data found[/yellow]")
        return

    context = df["context_tag"].dropna().tolist()

    if not context:
        print("[yellow]No Context Manager calls recorded[/yellow]")
        return

    counter = Counter(context)

    total_calls = sum(counter.values())
    unique_ct = len(counter)

    print("\n[bold blue]Context Manager Call Summary[/bold blue]")
    print(f"[yellow]Total Context Calls:[/yellow] {total_calls}")
    print(f"[yellow]Unique Context Managers:[/yellow] {unique_ct}")

    table = Table(
        title="Top Functions by Call Count",
        show_lines=False,
        header_style="bold magenta"
    )

    table.add_column("Rank", justify="right")
    table.add_column("Context Manager", justify="left", style="cyan")
    table.add_column("Calls", justify="right", style="green")
    table.add_column("Percentage", justify="right", style="yellow")

    for idx, (func, count) in enumerate(counter.most_common(limit), start=1):
        percent = (count / total_calls) * 100
        table.add_row(
            str(idx),
            func,
            str(count),
            f"{percent:.1f}%"
        )

    print(table)
