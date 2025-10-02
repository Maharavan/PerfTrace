import click
from rich import print
from perftrace.cli.commands import version
from perftrace.cli.commands import help as help_cmd
from perftrace.cli.commands import list as list_cmd
from perftrace.cli.commands import show_function
from perftrace.cli.commands import show_context
from perftrace.cli.commands import recent_function
from perftrace.cli.commands import recent_context
from perftrace.cli.commands import stats_function
from perftrace.cli.commands import stats_context
from perftrace.cli.commands import slowest
from perftrace.cli.commands import fastest

from perftrace import __version__

cli_commands = {
    "version": version,
    "help": help_cmd,
    "list": list_cmd,
    "show-function": show_function,
    "show-context": show_context,
    "recent-function": recent_function,
    "recent-context": recent_context,
    "stats-function": stats_function,
    "stats-context": stats_context,
    "slowest": slowest,
    "fastest": fastest,
}



class PerfTraceGroup(click.Group):
    def get_help(self, ctx):
        ctx.invoke(help_cmd)
        for name,help in cli_commands.items():
            print(f"[blue] {name} [/blue] : [green]{help}[/green]")
        ctx.exit(0)


@click.group(invoke_without_command=True,cls=PerfTraceGroup)
@click.pass_context
def cli(ctx):
    """PerfTrace CLI - Unified Performance Tracing"""
    if ctx.invoked_subcommand is None:
        ctx.invoke(help)

for name, cmd in cli_commands.items():
    cli.add_command(cmd, name)

def main():
    cli()
    