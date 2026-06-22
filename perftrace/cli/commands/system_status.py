import click
import psutil
import datetime
from perftrace.core.collectors import SystemCollector
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.rule import Rule

console = Console()


def _fmt_bytes(b):
    if b is None:
        return "-"
    try:
        b = float(b)
    except (TypeError, ValueError):
        return str(b)
    if abs(b) < 1024 ** 2:
        return f"{b / 1024:.1f} KB"
    if abs(b) < 1024 ** 3:
        return f"{b / 1024 ** 2:.1f} MB"
    return f"{b / 1024 ** 3:.2f} GB"


def _pct_color(pct):
    if pct >= 80:
        return "bold red"
    if pct >= 50:
        return "yellow"
    return "green"


def _bar(pct, width=18):
    filled = int(pct / 100 * width)
    color = _pct_color(pct)
    return f"[{color}]{'█' * filled}{'░' * (width - filled)}[/{color}]"


def _fmt_uptime(boot_ts):
    delta = datetime.datetime.now() - datetime.datetime.fromtimestamp(boot_ts)
    total = int(delta.total_seconds())
    d = total // 86400
    h = (total % 86400) // 3600
    m = (total % 3600) // 60
    s = total % 60
    if d:
        return f"{d}d {h:02d}h {m:02d}m {s:02d}s"
    if h:
        return f"{h}h {m:02d}m {s:02d}s"
    return f"{m}m {s:02d}s"


def _section_table(title, color="cyan"):
    t = Table(
        title=f"[bold {color}]{title}[/bold {color}]",
        show_header=True,
        header_style=f"bold {color}",
        show_lines=False,
        border_style=f"dim {color}",
        padding=(0, 1),
        expand=True,
    )
    t.add_column("Metric",  style="cyan",    no_wrap=True, min_width=22)
    t.add_column("Value",   justify="right", min_width=14)
    t.add_column("Visual",  no_wrap=True,    min_width=20)
    return t


@click.command()
def system_data():
    """Show a formatted snapshot of live system resource usage."""
    console.print(Panel.fit(
        "[bold cyan]PerfTrace[/bold cyan]  [dim]System Status Snapshot[/dim]",
        border_style="cyan",
        padding=(0, 2),
    ))

    data = SystemCollector().report()

    # ── CPU ──────────────────────────────────────────────────────────────────
    cpu_pct     = data.get("cpu_percent", 0.0)
    cpu_count_l = psutil.cpu_count(logical=True)
    cpu_count_p = psutil.cpu_count(logical=False)
    freq        = psutil.cpu_freq()
    freq_str    = f"{freq.current:.0f} MHz  [dim](max {freq.max:.0f} MHz)[/dim]" if freq else "-"
    cpu_col     = _pct_color(cpu_pct)

    t_cpu = _section_table("CPU", "cyan")
    t_cpu.add_row("Usage",
                  f"[{cpu_col}]{cpu_pct:.1f}%[/{cpu_col}]",
                  _bar(cpu_pct))
    t_cpu.add_row("Logical Cores",  f"[white]{cpu_count_l}[/white]", "")
    t_cpu.add_row("Physical Cores", f"[white]{cpu_count_p}[/white]", "")
    t_cpu.add_row("Frequency", freq_str, "")
    console.print(t_cpu)

    # ── Memory ───────────────────────────────────────────────────────────────
    mem_pct   = data.get("memory_percentage", 0.0)
    used_mem  = data.get("used_memory", 0)
    total_mem = data.get("total_system_memory", 0)
    avail_mem = data.get("available_system_memory", 0)
    free_mem  = data.get("free_memory", 0)
    swap      = psutil.swap_memory()
    mem_col   = _pct_color(mem_pct)
    swap_col  = _pct_color(swap.percent)

    t_mem = _section_table("Memory", "blue")
    t_mem.add_row("RAM Used",
                  f"[{mem_col}]{_fmt_bytes(used_mem)}[/{mem_col}]",
                  _bar(mem_pct))
    t_mem.add_row("RAM Total",     f"[white]{_fmt_bytes(total_mem)}[/white]",
                  f"[dim]{mem_pct:.1f}% in use[/dim]")
    t_mem.add_row("RAM Available", f"[green]{_fmt_bytes(avail_mem)}[/green]", "")
    t_mem.add_row("RAM Free",      f"[green]{_fmt_bytes(free_mem)}[/green]", "")
    t_mem.add_section()
    t_mem.add_row("Swap Used",
                  f"[{swap_col}]{_fmt_bytes(swap.used)}[/{swap_col}]",
                  _bar(swap.percent))
    t_mem.add_row("Swap Total",    f"[white]{_fmt_bytes(swap.total)}[/white]",
                  f"[dim]{swap.percent:.1f}% in use[/dim]")
    console.print(t_mem)

    # ── Disk ─────────────────────────────────────────────────────────────────
    total_disk = data.get("total_disk_space", 1)
    used_disk  = data.get("used_disk_space", 0)
    free_disk  = data.get("free_disk_space", 0)
    disk_pct   = used_disk / total_disk * 100 if total_disk else 0
    disk_col   = _pct_color(disk_pct)

    t_disk = _section_table("Disk", "yellow")
    t_disk.add_row("Used",
                   f"[{disk_col}]{_fmt_bytes(used_disk)}[/{disk_col}]",
                   _bar(disk_pct))
    t_disk.add_row("Total", f"[white]{_fmt_bytes(total_disk)}[/white]",
                   f"[dim]{disk_pct:.1f}% in use[/dim]")
    t_disk.add_row("Free",  f"[green]{_fmt_bytes(free_disk)}[/green]", "")
    console.print(t_disk)

    # ── System ───────────────────────────────────────────────────────────────
    boot        = data.get("uptime")
    uptime_str  = _fmt_uptime(boot) if boot else "-"
    proc_count  = len(psutil.pids())
    net         = psutil.net_io_counters()

    t_sys = _section_table("System", "green")
    t_sys.add_row("Uptime",          f"[white]{uptime_str}[/white]",    "")
    t_sys.add_row("Processes",        f"[white]{proc_count}[/white]",   "running")
    t_sys.add_section()
    t_sys.add_row("Net Bytes Sent",   f"[cyan]{_fmt_bytes(net.bytes_sent)}[/cyan]",   "")
    t_sys.add_row("Net Bytes Recv",   f"[magenta]{_fmt_bytes(net.bytes_recv)}[/magenta]", "")
    t_sys.add_row("Net Packets Sent", f"[cyan]{net.packets_sent:,}[/cyan]",            "")
    t_sys.add_row("Net Packets Recv", f"[magenta]{net.packets_recv:,}[/magenta]",      "")
    console.print(t_sys)
