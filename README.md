# PerfTrace

**PerfTrace** is a unified performance tracing and profiling CLI for Python applications.

It provides detailed insights into **function execution**, **context/module performance**, **CPU and memory usage**, and **system metrics**, with rich statistical summaries and export support — all through a clean, production-ready command-line interface.

PerfTrace is designed to be lightweight, explicit, and developer-controlled.
It focuses on **performance measurement**, not error monitoring or exception tracking.

---

## ✨ Features

- 🔍 **Function & Context Profiling**
- 📊 **Statistical Metrics**
  - min / max / average
  - p90 / p95 / p99 percentiles
  - standard deviation
- 🕒 **Recent & Historical Analysis**
- 🐢 **Slowest / Fastest Function Detection**
- 🧠 **System & Memory Monitoring**
- 📁 **Export Data**
  - CSV
  - JSON
- 🩺 **Health Diagnostics (`doctor`)**
- ⚙️ **Configurable Storage Backends**
  - DuckDB (default)
  - PostgreSQL

> ⚠️ PerfTrace **does not capture exceptions or stack traces**.
> If a function raises an error, execution stops as usual and only completed executions are recorded.

---

## 📦 Installation

```bash
pip install perftrace
```

**Requirements**
- Python **3.11+**

---

## 🚀 Quick Start

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

## 🧠 How PerfTrace Is Used

PerfTrace works in two phases:

1. **Instrumentation phase** – decorators or context managers record performance metrics
2. **Analysis phase** – the CLI queries stored data and produces reports

By default, PerfTrace uses **DuckDB**, so no database setup is required.

---

## 🧩 Instrumenting Your Code

### 1️⃣ Function-Level Profiling

```python
from perftrace import perf_trace_metrics

@perf_trace_metrics(profilers=["cpu"])
def normal_loop():
    data = []
    for i in range(100_000):
        data.append(i)
    return data
```

---

### Capture All Metrics

```python
@perf_trace_metrics(profilers="all")
def list_comprehensive():
    return [i for i in range(100_000)]
```

---

### 2️⃣ Class-Level Profiling

```python
from perftrace import perf_trace_metrics_cl

@perf_trace_metrics_cl(profilers=["cpu"])
class MyProcessor:
    @staticmethod
    def step1(x):
        return x + 1

    def step2(self, y):
        return y * 2
```

---

### 3️⃣ Context-Based Profiling

```python
from perftrace import PerfTraceContextManager

with PerfTraceContextManager(context_tag="work"):
    work = [x ** 2 for x in range(100_000)]
```

---

## 🧪 Full Example Script

```python
from perftrace import perf_trace_metrics, perf_trace_metrics_cl
from perftrace import PerfTraceContextManager

@perf_trace_metrics_cl(profilers=["cpu"])
class MyProcessor:
    @staticmethod
    def step1(x):
        return x + 1

@perf_trace_metrics(profilers="all")
def list_comprehensive():
    return [i for i in range(100_000)]

@perf_trace_metrics(profilers=["cpu"])
def normal_loop():
    return [i for i in range(100_000)]

if __name__ == "__main__":
    processor = MyProcessor()
    processor.step1(1)

    list_comprehensive()
    normal_loop()

    with PerfTraceContextManager(context_tag="work"):
        work = [x ** 2 for x in range(100_000)]
```

---

## 📊 Analyze with CLI

```bash
perftrace summary
perftrace slowest
perftrace fastest
perftrace stats-function normal_loop
perftrace stats-context work
```

---

## ⚙ Configuration

```bash
perftrace set-config
```

---

## 🩺 Diagnostics

```bash
perftrace doctor
```

---

## 📁 Exporting Data

```bash
perftrace export-csv
perftrace export-json
perftrace export-function-csv
perftrace export-context-json
```

---

## 📄 License

[MIT License](LICENSE)

---

## ⭐ Positioning

PerfTrace is a **developer-centric performance profiler**.
It complements APM tools and is not an error-tracking system.
