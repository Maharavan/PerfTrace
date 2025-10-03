import click
from rich import print
from perftrace.cli.commands import help as help_cmd
from perftrace import __version__
from perftrace.cli.registry import cli_commands


class PerfTraceGroup(click.Group):
    def get_help(self, ctx):
        ctx.invoke(help_cmd)
        ctx.exit(0)
        return super().get_help(ctx)


@click.group(invoke_without_command=True,cls=PerfTraceGroup)
@click.pass_context
def cli(ctx):
    """PerfTrace CLI - Unified Performance Tracing"""
    if ctx.invoked_subcommand is None:
        ctx.invoke(help)

for name, cmd in cli_commands.items():
    cli.add_command(cmd['function'], name)

def main():
    cli()
    