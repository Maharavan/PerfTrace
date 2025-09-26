from collections import defaultdict
import os
import time
import tracemalloc
import asyncio
import psutil
import statistics

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
    for _ ,memlist in memory_count.items():
        for cur,peak in memlist:
            overall_max_peak = max(overall_max_peak,peak)
    return overall_max_peak

def get_all_min_peak():
    overall_min_peak = 0
    for _ ,memlist in memory_count.items():
        for cur,peak in memlist:
            overall_min_peak = min(overall_min_peak,peak)
    return overall_min_peak

def get_function_memory_stats(func):
    if func not in memory_count:
        return None

    current_memory = [cur for cur,_ in memory_count[func]]
    peak_memory = [peak for _,peak in memory_count[func]]

    return {
        "current_memory":{
            "avg_current_memory":sum(current_memory)/len(current_memory),
            "min_current_memory": min(current_memory),
            "max_current_memory": max(current_memory),
            "latest":current_memory[-1]
            
        },
        "peak_memory":{
            "avg_peak_memory":sum(peak_memory)/len(peak_memory),
            "min_peak_memory": min(peak_memory),
            "max_peak_memory": max(peak_memory),
            "latest":peak_memory[-1]
            
        }
    }

def get_execution_time(func):
    if func not in exec_count:
        return None

    execution_time_function = [cur for cur,_ in exec_count[func]]

    return {
        "execution_time_function":{
            "avg_current_memory":sum(execution_time_function)/len(execution_time_function),
            "min_current_memory": min(execution_time_function),
            "max_current_memory": max(execution_time_function),
            "mean": statistics.mean(execution_time_function),
            "median": statistics.median(execution_time_function),
            "mode": statistics.mode(execution_time_function),
            "standard_deviation":statistics.stdev(execution_time_function),
            "latest":execution_time_function[-1]
            
        }
    }
