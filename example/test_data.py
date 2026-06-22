import os
import sys
from perftrace import perf_trace_metrics, perf_trace_metrics_cl
from perftrace import PerfTraceContextManager

_SAMPLE_FILE = os.path.join(os.path.dirname(__file__), "sample_io.txt")


@perf_trace_metrics_cl(profilers=["cpu", "memory"])
class MyProcessor:
    @staticmethod
    def step1(x):
        print(f"Step1 processing {x}")
        return x + 1

    def step2(self, y):
        print(f"Step2 processing {y}")
        return y * 2


@perf_trace_metrics(profilers="all")
def list_comprehensive():
    data = [i for i in range(100000)]
    return data


# "file" collector enabled — captures read_bytes / write_bytes / op counts
@perf_trace_metrics(profilers=["cpu", "file"])
def normal_loop():
    data = []
    for i in range(100000):
        data.append(i)
    with open(_SAMPLE_FILE, "w") as f:
        f.write("File created by normal_loop\n" * 100)
    return data


# Reads the file written above — captured by the "file" collector
@perf_trace_metrics(profilers=["cpu", "memory", "file"])
def read_sample_file():
    if not os.path.exists(_SAMPLE_FILE):
        return []
    with open(_SAMPLE_FILE, "r") as f:
        lines = f.readlines()
    return lines


@perf_trace_metrics(profilers=["cpu", "memory"])
def trigger_memory_error():
    big_list = [0] * (10**10)


if __name__ == "__main__":
    track_cl = MyProcessor()
    track_cl.step1(1)

    lc = list_comprehensive()
    nl = normal_loop()
    rf = read_sample_file()

    # trigger_memory_error()

    # Context manager with file I/O tracking enabled
    with PerfTraceContextManager(
        context_tag="work", cls_collectors=["cpu", "memory", "file"]
    ) as collectors:
        with open(_SAMPLE_FILE, "a") as f:
            f.write("appended by context manager\n")
        work = [x ** 2 for x in range(100000)]

    print(collectors.get_metrics())
