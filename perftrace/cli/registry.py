from perftrace.cli.commands.version import version
from perftrace.cli.commands.list import list as list_cmd
from perftrace.cli.commands.show_data import show_function
from perftrace.cli.commands.show_data import show_context
from perftrace.cli.commands.recent_data import recent_function
from perftrace.cli.commands.recent_data import recent_context
from perftrace.cli.commands.stats import stats_function
from perftrace.cli.commands.stats import stats_context
from perftrace.cli.commands.fastest_execution import fastest as fastest_execution
from perftrace.cli.commands.slowest_execution import slowest as slowest_execution
from perftrace.cli.commands.help import help as help_cmd
from perftrace.cli.commands.today_function_call import today

from perftrace import __version__


cli_commands = {
    "version": {
        "function": version,
        "description": "Shows the current version of PerfTrace."
    },
    "help": {
        "function": help_cmd,
        "description": "Displays help and lists all available commands."
    },
    "list": {
        "function": list_cmd,
        "description": "Lists all performance traces, functions, or available profiling data."
    },
    "show-function": {
        "function": show_function,
        "description": "Shows detailed data for a specific function."
    },
    "show-context": {
        "function": show_context,
        "description": "Shows profiling data for a specific context (module or file)."
    },
    "recent-function": {
        "function": recent_function,
        "description": "Shows recently executed functions."
    },
    "recent-context": {
        "function": recent_context,
        "description": "Shows recently executed contexts."
    },
    "stats-function": {
        "function": stats_function,
        "description": "Shows statistical metrics (min/max/avg execution time) for a function."
    },
    "stats-context": {
        "function": stats_context,
        "description": "Shows statistical metrics for a context/module."
    },
    "slowest": {
        "function": slowest_execution,
        "description": "Shows the function or context with the slowest execution time."
    },
    "fastest": {
        "function": fastest_execution,
        "description": "Shows the function or context with the fastest execution time."
    },
    "today":{
        "function":today,
        "description":"Shows Today Function call"
    }
}

