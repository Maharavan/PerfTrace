import datetime
import time
from collections import deque
import psutil
import click
from perftrace.core.collectors import SystemCollector
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich.rule import Rule

console = Console()

_CPU_HISTORY: deque = deque(maxlen=20)
_NET_PREV: dict = {}


def _fmt_bytes(b):
    if b is None:
        return "-"
    try:
        b = float(b)
    except (TypeError, ValueError):
        return str(b)
    if abs(b) < 1024:
        return f"{b:.0f} B"
    if abs(b) < 1024 ** 2:
        return f"{b / 1024:.1f} KB"
    if abs(b) < 1024 ** 3:
        return f"{b / 1024 ** 2:.1f} MB"
    return f"{b / 1024 ** 3:.2f} GB"


def _fmt_bytes_per_sec(b):
    s = _fmt_bytes(b)
    return f"{s}/s" if s != "-" else "-"


def _pct_color(pct):
    if pct >= 80:
        return "bold red"
    if pct >= 50:
        return "yellow"
    return "green"


def _progress_bar(pct, width=20):
    filled = int(pct / 100 * width)
    bar = "█" * filled + "░" * (width - filled)
    color = _pct_color(pct)
    return f"[{color}]{bar}[/{color}]"


def _sparkline(history):
    _BLOCKS = " ▁▂▃▄▅▆▇█"
    if not history:
        return "[dim]no data[/dim]"
    out = []
    for v in history:
        idx = min(int(v / 100 * (len(_BLOCKS) - 1)), len(_BLOCKS) - 1)
        color = _pct_color(v)
        out.append(f"[{color}]{_BLOCKS[idx]}[/{color}]")
    return "".join(out)


def _fmt_uptime(boot_timestamp):
    delta = datetime.datetime.now() - datetime.datetime.fromtimestamp(boot_timestamp)
    total = int(delta.total_seconds())
    days  = total // 86400
    hours = (total % 86400) // 3600
    mins  = (total % 3600) // 60
    secs  = total % 60
    if days:
        return f"{days}d {hours:02d}h {mins:02d}m"
    if hours:
        return f"{hours}h {mins:02d}m {secs:02d}s"
    return f"{mins}m {secs:02d}s"


def _get_net_delta(interval):
    global _NET_PREV
    net = psutil.net_io_counters()
    now = time.monotonic()
    if _NET_PREV:
        dt = max(now - _NET_PREV["ts"], 0.001)
        sent_ps = (net.bytes_sent - _NET_PREV["sent"]) / dt
        recv_ps = (net.bytes_recv - _NET_PREV["recv"]) / dt
    else:
        sent_ps = recv_ps = 0.0
    _NET_PREV = {"ts": now, "sent": net.bytes_sent, "recv": net.bytes_recv}
    return sent_ps, recv_ps, net.bytes_sent, net.bytes_recv


def _build_cpu_table(data, cpu_history):
    cpu_pct = data.get("cpu_percent", 0.0)
    per_core = psutil.cpu_percent(percpu=True)
    freq = psutil.cpu_freq()
    count_logical = psutil.cpu_count(logical=True)
    count_physical = psutil.cpu_count(logical=False)

    table = Table(
        title="[bold cyan]  CPU[/bold cyan]",
        show_header=True,
        header_style="bold cyan",
        show_lines=False,
        border_style="dim cyan",
        padding=(0, 1),
        expand=True,
    )
    table.add_column("Metric",  style="cyan",      no_wrap=True, min_width=18)
    table.add_column("Value",   justify="right",   min_width=10)
    table.add_column("",        no_wrap=True,       min_width=22)

    cpu_col = _pct_color(cpu_pct)
    table.add_row(
        "Overall Usage",
        f"[{cpu_col}]{cpu_pct:.1f}%[/{cpu_col}]",
        _progress_bar(cpu_pct),
    )
    table.add_row(
        "Trend (last 20)",
        "",
        _sparkline(cpu_history),
    )
    if freq:
        table.add_row(
            "Frequency",
            f"[white]{freq.current:.0f} MHz[/white]",
            f"[dim]max {freq.max:.0f} MHz[/dim]",
        )
    table.add_row(
        "Cores",
        f"[white]{count_logical}[/white]",
        f"[dim]{count_physical} physical[/dim]",
    )

    table.add_section()
    for i, c in enumerate(per_core):
        col = _pct_color(c)
        table.add_row(
            f"  Core {i}",
            f"[{col}]{c:.1f}%[/{col}]",
            _progress_bar(c, width=16),
        )

    return table


def _build_memory_table(data):
    total_mem = data.get("total_system_memory", 0)
    used_mem  = data.get("used_memory", 0)
    avail_mem = data.get("available_system_memory", 0)
    free_mem  = data.get("free_memory", 0)
    mem_pct   = data.get("memory_percentage", 0.0)
    mem_col   = _pct_color(mem_pct)

    swap = psutil.swap_memory()

    table = Table(
        title="[bold blue]  Memory[/bold blue]",
        show_header=True,
        header_style="bold blue",
        show_lines=False,
        border_style="dim blue",
        padding=(0, 1),
        expand=True,
    )
    table.add_column("Metric",  style="cyan",    no_wrap=True, min_width=18)
    table.add_column("Value",   justify="right", min_width=10)
    table.add_column("",        no_wrap=True,     min_width=22)

    table.add_row(
        "RAM Used",
        f"[{mem_col}]{_fmt_bytes(used_mem)}[/{mem_col}]",
        _progress_bar(mem_pct),
    )
    table.add_row("RAM Total",     f"[white]{_fmt_bytes(total_mem)}[/white]", "")
    table.add_row("RAM Available", f"[green]{_fmt_bytes(avail_mem)}[/green]",
                  f"[dim]{mem_pct:.1f}% in use[/dim]")
    table.add_row("RAM Free",      f"[green]{_fmt_bytes(free_mem)}[/green]", "")

    table.add_section()
    swap_col = _pct_color(swap.percent)
    table.add_row(
        "Swap Used",
        f"[{swap_col}]{_fmt_bytes(swap.used)}[/{swap_col}]",
        _progress_bar(swap.percent),
    )
    table.add_row("Swap Total", f"[white]{_fmt_bytes(swap.total)}[/white]",
                  f"[dim]{swap.percent:.1f}% in use[/dim]")

    return table


def _build_disk_net_table(data, sent_ps, recv_ps, total_sent, total_recv):
    total_disk = data.get("total_disk_space", 1)
    used_disk  = data.get("used_disk_space", 0)
    free_disk  = data.get("free_disk_space", 0)
    disk_pct   = used_disk / total_disk * 100 if total_disk else 0
    disk_col   = _pct_color(disk_pct)

    table = Table(
        title="[bold yellow]  Disk & Network[/bold yellow]",
        show_header=True,
        header_style="bold yellow",
        show_lines=False,
        border_style="dim yellow",
        padding=(0, 1),
        expand=True,
    )
    table.add_column("Metric",  style="cyan",    no_wrap=True, min_width=18)
    table.add_column("Value",   justify="right", min_width=10)
    table.add_column("",        no_wrap=True,     min_width=22)

    table.add_row(
        "Disk Used",
        f"[{disk_col}]{_fmt_bytes(used_disk)}[/{disk_col}]",
        _progress_bar(disk_pct),
    )
    table.add_row("Disk Total", f"[white]{_fmt_bytes(total_disk)}[/white]",
                  f"[dim]{disk_pct:.1f}% in use[/dim]")
    table.add_row("Disk Free",  f"[green]{_fmt_bytes(free_disk)}[/green]", "")

    table.add_section()
    table.add_row(
        "Net ↑ Speed",
        f"[cyan]{_fmt_bytes_per_sec(sent_ps)}[/cyan]",
        f"[dim]total {_fmt_bytes(total_sent)}[/dim]",
    )
    table.add_row(
        "Net ↓ Speed",
        f"[magenta]{_fmt_bytes_per_sec(recv_ps)}[/magenta]",
        f"[dim]total {_fmt_bytes(total_recv)}[/dim]",
    )

    return table


def _build_system_table(data, refresh_count, interval, proc_count):
    boot = data.get("uptime")
    uptime_str = _fmt_uptime(boot) if boot else "-"
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    table = Table(
        title="[bold green]  System[/bold green]",
        show_header=True,
        header_style="bold green",
        show_lines=False,
        border_style="dim green",
        padding=(0, 1),
        expand=True,
    )
    table.add_column("Metric",  style="cyan",    no_wrap=True, min_width=18)
    table.add_column("Value",   justify="right", min_width=10)
    table.add_column("",        style="dim",     no_wrap=True, min_width=22)

    table.add_row("Uptime",     f"[white]{uptime_str}[/white]",  "")
    table.add_row("Processes",  f"[white]{proc_count}[/white]",  "running")
    table.add_row("Timestamp",  f"[white]{ts}[/white]",          "")
    table.add_row("Refresh #",  f"[white]{refresh_count}[/white]",
                  f"every {interval}s")

    return table


def _build_layout(data, refresh_count, interval):
    _CPU_HISTORY.append(data.get("cpu_percent", 0.0))
    sent_ps, recv_ps, total_sent, total_recv = _get_net_delta(interval)
    proc_count = len(psutil.pids())

    cpu_table    = _build_cpu_table(data, list(_CPU_HISTORY))
    mem_table    = _build_memory_table(data)
    disk_table   = _build_disk_net_table(data, sent_ps, recv_ps, total_sent, total_recv)
    sys_table    = _build_system_table(data, refresh_count, interval, proc_count)

    header = Rule(
        title="[bold cyan]PerfTrace — Live System Monitor[/bold cyan]  "
              "[dim]Ctrl+C to stop[/dim]",
        style="cyan",
    )
    top_row    = Columns([cpu_table, mem_table],    equal=True, expand=True)
    bottom_row = Columns([disk_table, sys_table],   equal=True, expand=True)

    from rich.console import Group
    return Group(header, top_row, bottom_row)


@click.command()
@click.option(
    "--interval", "-i",
    default=3,
    type=int,
    show_default=True,
    help="Refresh interval in seconds.",
)
def system_monitor(interval):
    """Live system resource monitor with CPU, RAM, disk, network, and per-core stats."""
    refresh_count = 0
    with Live(console=console, refresh_per_second=4, screen=True) as live:
        try:
            while True:
                refresh_count += 1
                data = SystemCollector().report()
                live.update(_build_layout(data, refresh_count, interval))
                time.sleep(interval)
        except KeyboardInterrupt:
            pass

    console.print(Panel.fit(
        "[yellow]Monitoring stopped.[/yellow]",
        border_style="yellow",
    ))
