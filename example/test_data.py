import asyncio
import os
import sys
from perftrace import perf_trace_metrics,perf_trace_metrics_cl
from perftrace import PerfTraceContextManager

@perf_trace_metrics_cl(profilers=["cpu"])
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

@perf_trace_metrics(profilers=["cpu"])
def normal_loop():
    data = []
    for i in range(100000):
        data.append(i)
    return data

@perf_trace_metrics(profilers=["cpu","memory"])
def trigger_memory_error():
    big_list = [0] * (10**10)

@perf_trace_metrics()
def os_error():
    with open("/nonexistent/path/file.txt", "r") as f:
        f.read()

if __name__=='__main__':
    track_cl  = MyProcessor()
    track_cl.step1(1)
    lc = list_comprehensive()
    nl = normal_loop()
    #trigger_memory_error()
    with PerfTraceContextManager(context_tag="work") as collectors:
        work = [x ** 2 for x in range(100000)]

    # print(collectors.get_metrics())
