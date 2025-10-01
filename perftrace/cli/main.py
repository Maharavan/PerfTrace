import click
from rich import print
from .commands import version,help
from perftrace import __version__

class PerfTraceGroup(click.Group):
    def get_help(self, ctx):
        ctx.invoke(help)
        ctx.exit(0)


@click.group(invoke_without_command=True,cls=PerfTraceGroup)
@click.pass_context
def cli(ctx):
    """PerfTrace CLI - Unified Performance Tracing"""
    if ctx.invoked_subcommand is None:
        ctx.invoke(help)

cli.add_command(version)
cli.add_command(help)


def main():
    cli()
