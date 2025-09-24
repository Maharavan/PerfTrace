from collections import defaultdict
from functools import wraps
import os
import time
import tracemalloc
import asyncio
import psutil
import metrics

def auto_metrics(debug=True):
    def code_tracker(func):
        @wraps(func)
        def wrapper(*args,**kwargs):
            if not debug:
                return func (*args,**kwargs)
            print(f"Executing {func.__name__}")
            start_time = time.perf_counter()
            current_process = psutil.Process(os.getpid())
            cpu_memory_current = current_process.memory_info().rss / (1024 ** 2)
            tracemalloc.start()
            try:
                if asyncio.iscoroutinefunction(func):
                    coroutine =  func(*args,**kwargs)   
                    if asyncio.get_running_loop():
                        return coroutine
                    else:
                        return asyncio.run(coroutine)
                else:
                    return func(*args,**kwargs) 
            except BaseException as e:
                print(f'[AutoMetric] {func.__name__} failed')
                metrics.error_count[func.__name__]+=1
                raise
            finally:
                current,peak = tracemalloc.get_traced_memory()
                cpu_memory_end = current_process.memory_info().rss/ (1024*1024)
                process_ram_delta = round(cpu_memory_end-cpu_memory_current,2)
                tracemalloc.stop()
                end_time = time.perf_counter()
                metrics.call_count[func.__name__]+=1
                metrics.memory_count[func.__name__].append((current,peak))
                metrics.ram_count[func.__name__].append(process_ram_delta)
                execution_time = end_time-start_time
                metrics.exec_count[func.__name__].append(execution_time)

                print(f"[AutoMetric] Executed time {func.__name__}: {execution_time:.2f}")
                print(f"[AutoMetric] Call Count: {metrics.call_count[func.__name__]}")
                print(f"[AutoMetric] Error Count : {metrics.error_count[func.__name__]}")
                print(f"[Autometric] Function Memory Current & Peak Memory Size : {current/1024**2:.2f} Mb {peak/1024**2:.2f}Mb ")
                print(f"[Autometric] CPU Memory {process_ram_delta}")

        return wrapper
    return code_tracker


def auto_metrics_cl(cls,debug=True):
    for name,method in cls.__dict__.items():
        if isinstance(method,staticmethod):
            get_func = method.__func__
            setattr(cls,name,staticmethod(auto_metrics(debug)(get_func)))
        elif isinstance(method,classmethod):
            get_func = method.__func__
            setattr(cls,name,classmethod(auto_metrics(debug)(get_func)))
        elif callable(method) and not name.startswith('__'):
            setattr(cls,name,auto_metrics(debug)(method))
    return cls