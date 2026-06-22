import click
from perftrace.cli.commands.help import render_help
from perftrace.cli.registry import cli_commands


def _help_callback(ctx, _param, value):
    if not value or ctx.resilient_parsing:
        return
    ctx.invoke(render_help)
    ctx.exit()


class PerfTraceGroup(click.Group):
    """Custom group that shows our Rich help instead of Click's plain text."""
    def get_help(self, ctx):
        ctx.invoke(render_help)
        return ""


@click.group(
    invoke_without_command=True,
    cls=PerfTraceGroup,
    add_help_option=False,
)
@click.option(
    "--help", "-h",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=_help_callback,
    help="Show this help message and exit.",
)
@click.pass_context
def cli(ctx):
    """PerfTrace CLI — Unified Performance Tracing"""
    if ctx.invoked_subcommand is None:
        ctx.invoke(render_help)


for name, cmd in cli_commands.items():
    cli.add_command(cmd["function"], name)


def main():
    cli()
