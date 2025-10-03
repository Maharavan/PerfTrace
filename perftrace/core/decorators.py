from perftrace.core.collectors import ExecutionCollector
from perftrace.core.collectors import MemoryCollector
from perftrace.core.collectors import CPUCollector
from perftrace.core.collectors import FileIOCollector
from perftrace.core.collectors import GarbageCollector
from perftrace.core.collectors import NetworkActivityCollector
from perftrace.core.collectors import ThreadContextCollector
# from perftrace.core.collectors import ExceptionCollector
from perftrace.storage import get_storage
import asyncio
import datetime
from functools import wraps
def perf_trace_metrics(profilers=None):
    def code_tracker(func):
        @wraps(func)
        def wrapper(*args,**kwargs):
            report = {}
            active_collectors = None
            profile_collectors = {
                "memory":MemoryCollector(),
                "cpu":CPUCollector(),
                "execution":ExecutionCollector(),
                "file":FileIOCollector(),
                "garbagecollector":GarbageCollector(),
                "ThreadContext": ThreadContextCollector(),
                "network":NetworkActivityCollector(),
                # "error":ExceptionCollector()
            }
            

            if profilers is None or (isinstance(profilers,str) and profilers=="all"):
                active_collectors = profile_collectors   
            elif isinstance(profilers,list):
                try:
                    active_collectors = {cls:profile_collectors[cls] for cls in profilers}
                except KeyError as e:
                    available = list(profile_collectors.keys())
                    raise ValueError(f"Unknown collector. Available: {','.join(available)}") from e
            else:
                if not isinstance(profilers, str):
                    raise TypeError(f"Expected string, list, or None. Got {type(active_collectors)}")
                
                if profilers not in profile_collectors:
                    available = list(profile_collectors.keys())
                    raise ValueError(f"Unknown collector '{profilers}'. Available: {available}")
                
                active_collectors = {profilers:profilers[profilers]}
            active_collectors["execution"] = ExecutionCollector()

            for _,collector in active_collectors.items():
                collector.start()

            try:
                if asyncio.iscoroutinefunction(func):
                    coroutine =  func(*args,**kwargs)   
                    if asyncio.get_running_loop():
                        return  coroutine
                    else:
                        return asyncio.run(coroutine)
                else:
                    return func(*args,**kwargs) 
            except BaseException as e:
                # ExceptionCollector.capture()
                print(f'[PerfTrace] {func.__name__} {e} failed')
                raise
            finally:
                report["Timestamp"] = datetime.datetime.now()
                report["Function_name"] = func.__name__
                report["Context_tag"] = None
                for name,collector in active_collectors.items():
                    collector.stop()
                    report[collector.__class__.__name__] = collector.report()
                    
                    #print(f"[PerfTrace] {collector.__class__.__name__} {report[collector.__class__.__name__]}")
                get_storage(backend='duckdb',report=report)
        return wrapper
    return code_tracker


def perf_trace_metrics_cl(profilers=None):
    def decorator(cls):
        for name,method in cls.__dict__.items():
            if isinstance(method,staticmethod):
                get_func = method.__func__
                setattr(cls,name,staticmethod(perf_trace_metrics(profilers)(get_func)))
            elif isinstance(method,classmethod):
                get_func = method.__func__
                setattr(cls,name,classmethod(perf_trace_metrics(profilers)(get_func)))
            elif callable(method) and not name.startswith('__'):
                setattr(cls,name,perf_trace_metrics(profilers)(method))
        return cls
    return decorator