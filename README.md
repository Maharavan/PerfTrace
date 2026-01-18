# PerfTrace

**PerfTrace** is a unified performance tracing and profiling CLI for Python applications.

It provides detailed insights into **function execution**, **context/module performance**, **CPU and memory usage**, and **system metrics**, with rich statistical summaries and export support — all through a clean, production-ready command-line interface.

PerfTrace is designed to be lightweight, easy to adopt, and suitable for both local development and production analysis.

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
  - DuckDB
  - PostgreSQL

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

## 🧠 Usage (How PerfTrace Works)

PerfTrace instruments your application to collect performance traces at runtime.
These traces are stored in a configured backend (DuckDB or PostgreSQL).

The CLI is then used to **query, analyze, and export** this data for performance tuning,
regression detection, and system diagnostics.

### Typical Workflow

1. Run your application with PerfTrace enabled
2. Collect function and context-level performance traces
3. Analyze collected data using the CLI
4. Export results for reporting or CI/CD checks

---

## 📖 CLI Usage Examples

### 🔍 Performance Analysis

```bash
perftrace summary
perftrace slowest
perftrace fastest
perftrace stats-function process_order
perftrace stats-context database_layer
```

---

### 🕒 Time-Based Analysis

```bash
perftrace today
perftrace recent-function
perftrace recent-context
perftrace history
```

---

### 🔎 Search & Frequency Analysis

```bash
perftrace search-function process_order
perftrace count-function
perftrace count-context
```

---

### 🖥 System & Memory Metrics

```bash
perftrace system-status
perftrace system-info
perftrace system-monitor
perftrace memory
```

---

### 📁 Exporting Data

```bash
perftrace export-csv
perftrace export-json
perftrace export-function-csv
perftrace export-context-json
```

---

## ⚙ Configuration

```bash
perftrace set-config
```

Configure storage backend, database connection details, and profiling options.

---

## 🩺 Diagnostics

```bash
perftrace doctor
```

Validates configuration, database connectivity, and profiling data integrity.

---

## 🧪 Development Installation

```bash
pip install -e .
```

---

## 📄 License

MIT License © Maharavan

---

## ⭐ Why PerfTrace?

PerfTrace is built for developers who want actionable performance insights without
heavyweight APM tooling.

It fits naturally into development, debugging, CI/CD pipelines, and production
performance investigations.
