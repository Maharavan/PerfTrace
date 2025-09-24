from collections import defaultdict
import os
import time
import tracemalloc
import asyncio
import psutil
call_count = defaultdict(int)
error_count = defaultdict(int)
exec_count  = defaultdict(list)
memory_count = defaultdict(list)
ram_count = defaultdict(list)


def avg_cpu_exec_function(func):
    avg_cpu = sum(ram_count[func])/len(ram_count[func])
    return avg_cpu

def retrieve_statistics(func):
    if func:
        return {
            "function_call":call_count[func],
            "error_count":error_count[func],
            "ram_delta": ram_count[func],
            "functional_memory": memory_count[func],
            "execution_time":exec_count[func]
        }
    else:
        print("No data passed")


def get_all_max_peak():
    overall_max_peak = 0
    for function,mem in memory_count.items():
        _,peak = mem
        overall_max_peak = max(overall_max_peak,peak)
    return overall_max_peak

def get_all_min_peak():
    overall_min_peak = 0
    for function,mem in memory_count.items():
        _,peak = mem
        overall_min_peak = max(overall_min_peak,peak)
    return overall_min_peak

