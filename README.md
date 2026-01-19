# PerfTrace 🔍

[![PyPI version](https://img.shields.io/pypi/v/perftrace.svg)](https://pypi.org/project/perftrace/)
[![Python versions](https://img.shields.io/pypi/pyversions/perftrace.svg)](https://pypi.org/project/perftrace/)
[![License](https://img.shields.io/pypi/l/perftrace.svg)](https://pypi.org/project/perftrace/)
![Stars](https://img.shields.io/github/stars/Maharavan/PerfTrace?style=social)

**PerfTrace** is a unified performance tracing and profiling CLI for Python applications.

It provides detailed insights into **function execution**, **context/module performance**, **CPU and memory usage**, and **system metrics**, with rich statistical summaries and export support — all through a clean, production-ready command-line interface.

PerfTrace is **developer-centric, explicit, and lightweight**.  
It focuses on **performance analysis**, not error or exception tracking.

---

## ✨ Key Features

- 🔍 Function & context-level profiling
- 📊 Statistical metrics (min / max / avg / p90 / p95 / p99 / std dev)
- 🕒 Recent, daily, and historical analysis
- 🐢 Slowest / fastest execution detection
- 🧠 System & memory monitoring
- 📁 Export to CSV & JSON
- 🩺 Health diagnostics (`doctor`)
- ⚙️ Configurable storage backends (DuckDB & PostgreSQL)
- 🧩 Function, class, and context-manager based instrumentation

---

## 📦 Installation

```bash
pip install perftrace
```

**Requirements**
- Python **3.11+**

---

## 🚀 Getting Started

```bash
perftrace help
```

Recommended first commands:

```bash
perftrace summary
perftrace doctor
perftrace stats-function <FUNCTION_NAME>
```

---

## 🧠 How PerfTrace Works

PerfTrace works in **two clear phases**:

1. **Instrumentation**  
   Developers explicitly mark functions, classes, or code blocks using decorators or context managers.

2. **Analysis**  
   The CLI queries stored metrics and generates summaries, statistics, and exports.

PerfTrace runs **only when your code runs** — there are no background agents, daemons, or always-on processes.

---

## 🧩 Instrumenting Your Code

### 🎛 Selecting Metrics to Collect

PerfTrace allows you to **explicitly control which performance metrics are collected**.

You can either:
- provide a **list of specific metrics**, or
- use `"all"` to collect every supported metric

#### Supported Metrics

| Metric | Description |
|------|------------|
| `cpu` | CPU usage and CPU time |
| `memory` | Memory usage and deltas |
| `execution` | Execution time |
| `file` | File I/O activity |
| `garbagecollector` | Garbage collection activity |
| `ThreadContext` | Thread and execution context |
| `network` | Network activity |

#### Using Specific Metrics

```python
from perftrace import perf_trace_metrics

@perf_trace_metrics(profilers=["cpu", "memory", "execution"])
def compute():
    return [i for i in range(100_000)]
```

#### Using All Metrics

```python
@perf_trace_metrics(profilers="all")
def full_trace():
    return [i for i in range(100_000)]
```

### Class-Level Profiling

```python
from perftrace import perf_trace_metrics_cl

@perf_trace_metrics_cl(profilers=["cpu", "execution"])
class MyProcessor:
    @staticmethod
    def step1(x):
        return x + 1

    def step2(self, y):
        return y * 2
```

### Context-Based Profiling

```python
from perftrace import PerfTraceContextManager

with PerfTraceContextManager(
    context_tag="work",
    cls_collectors=["cpu", "memory"]
):
    work = [x ** 2 for x in range(100_000)]
```

---

## 📖 Complete CLI Reference

### General Commands

| Command | Description |
|------|------------|
| `version` | Show PerfTrace version |
| `help` | Display help |
| `doctor` | Run health checks |
| `summary` | Overall performance summary |
| `list` | List available functions and contexts |

### Function Commands

| Command | Description |
|------|------------|
| `show-function <name>` | Detailed trace data |
| `stats-function <name>` | Statistical metrics |
| `recent-function` | Recently executed functions |
| `search-function <name>` | Search execution history |
| `count-function` | Execution frequency |
| `slowest` | Slowest execution |
| `fastest` | Fastest execution |

### Context Commands

| Command | Description |
|------|------------|
| `show-context <name>` | Context trace data |
| `stats-context <name>` | Statistical metrics |
| `recent-context` | Recently executed contexts |
| `search-context <name>` | Search history |
| `count-context` | Execution frequency |

### Time-Based

| Command | Description |
|------|------------|
| `today` | Executions today |
| `history` | Historical data |

### System & Memory

| Command | Description |
|------|------------|
| `system-status` | System status |
| `system-info` | System information |
| `system-monitor` | Real-time monitoring |
| `memory` | Memory usage |

### Export

| Command | Description |
|------|------------|
| `export-csv` | Export database to CSV |
| `export-json` | Export database to JSON |
| `export-function-csv` | Export function CSV |
| `export-context-csv` | Export context CSV |
| `export-function-json` | Export function JSON |
| `export-context-json` | Export context JSON |

---

## ⚙️ Configuration (YAML)

Config file locations:

- Linux / macOS: `~/.perftrace/config.yaml`
- Windows: `%USERPROFILE%\.perftrace\config.yaml`

### DuckDB (Default)

```yaml
database:
  engine: duckdb
  duckdb:
    path: ./data/default.duckdb
```

### PostgreSQL (Optional)

```yaml
database:
  engine: postgresql
  postgresql:
    host: localhost
    port: 5432
    user: postgres
    password: your_password
```

Interactive setup:

```bash
perftrace set-config
```

Verify:

```bash
perftrace doctor
```

---

## 🔍 Positioning (PerfTrace vs APM Tools)

PerfTrace **complements APM tools** by providing:
- precise function-level metrics
- lightweight, on-demand profiling
- local and CI-friendly analysis

PerfTrace is not a distributed tracing or error-tracking system.

---

## 📄 License

[MIT License](LICENSE)