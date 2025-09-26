import asyncio
from collections import defaultdict
from functools import wraps
from .collectors import ExecutionCollector
from .collectors import MemoryCollector
from .collectors import CPUCollector
from .collectors import FileIOCollector
from .collectors import GarbageCollector
from .collectors import NetworkActivityCollector
def auto_metrics(debug=True):
    def code_tracker(func):
        @wraps(func)
        def wrapper(*args,**kwargs):
            report = {}
            collector = [
                ExecutionCollector(),
                MemoryCollector(),
                CPUCollector(),
                FileIOCollector(),
                GarbageCollector(),
                NetworkActivityCollector()
            ]
            for stats in collector:
                stats.start()
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
                print(f'[AutoMetric] {func.__name__} failed')
                raise
            finally:
                for stats in collector:
                    stats.stop()
                    report[stats.__class__.__name__] = stats.report()
                    print(f"[Autometrics] {stats.__class__.__name__} {report[stats.__class__.__name__]}")
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