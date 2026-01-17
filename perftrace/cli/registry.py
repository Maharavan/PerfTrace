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
from perftrace.cli.commands.help import render_help as help_cmd
from perftrace.cli.commands.today_function_call import today
from perftrace.cli.commands.history_command import history
from perftrace.cli.commands.history_command import search_function
from perftrace.cli.commands.history_command import search_context
from perftrace.cli.commands.system_status import system_data
from perftrace.cli.commands.get_memory import memory
from perftrace.cli.commands.config import create_config
from perftrace.cli.commands.system_monitor import system_monitor
from perftrace.cli.commands.system_info import system_info
from perftrace.cli.commands.export_csv import export_context_csv, export_result_csv
from perftrace.cli.commands.export_csv import export_function_csv
from perftrace.cli.commands.export_json import export_result_json
from perftrace.cli.commands.database_info import database_info

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
    },
    "history":{
        "function": history,
        "description": "Shows history data for specific days"
    },
    "search-function":{
        "function":search_function,
        "description": "Shows history of specific function"
    },
    "search-context":{
        "function":search_context,
        "description": "Shows history of Context manager"
    },
    "system-status":{
        "function":system_data,
        "description":"Retrieves System Status"
    },
    "memory":{
        "function":memory,
        "description": "Get Memory stats of function & Context manager"
    },
    "set-config":{
        "function":create_config,
        "description": "Create Config"
    },
    "system-monitor":{
        "function": system_monitor,
        "description": "Real time monitor system"
    },
    "system-info":{
        "function": system_info,
        "description": "Gives information about the system"
    },
    "export-csv":{
        "function": export_result_csv,
        "description": "Export the Database data in CSV format"
    },
    "export-function-csv":{
        "function": export_function_csv,
        "description": "Export the Function data in CSV format"
    },
    "export-context-csv":{
        "function": export_context_csv,
        "description": "Export the Context data in CSV format"
    },
    "export-json":{
        "function": export_result_json,
        "description": "Export the Database data in JSON format"
    },
    "database-info":{
        "function": database_info,
        "description": "Get details of Database"
    }

}

