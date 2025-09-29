import asyncio
from functools import wraps
from .collectors import ExecutionCollector
from .collectors import MemoryCollector
from .collectors import CPUCollector
from .collectors import FileIOCollector
from .collectors import GarbageCollector
from .collectors import NetworkActivityCollector
from .collectors import ThreadContextCollector
from ..storage import get_storage
def auto_metrics(profilers=None):
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
            }
            

            if profilers is None or (isinstance(profilers,str) and profilers=="all"):
                active_collectors = profile_collectors   
            elif isinstance(profilers,list):
                try:
                    active_collectors = {cls:profile_collectors[cls] for cls in profilers}
                except KeyError as e:
                    available = list(profile_collectors.keys())
                    raise ValueError(f"Unknown collector. Available: {','.join(available)}")
            else:
                if not isinstance(profilers, str):
                    raise TypeError(f"Expected string, list, or None. Got {type(active_collectors)}")
                
                if profilers not in profile_collectors:
                    available = list(profile_collectors.keys())
                    raise ValueError(f"Unknown collector '{profilers}'. Available: {available}")
                
                active_collectors = {profilers:profilers[profilers]}
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
                print(f'[AutoMetric] {func.__name__} failed')
                raise
            finally:
                for name,collector in active_collectors.items():
                    collector.stop()
                    report[collector.__class__.__name__] = collector.report()
                    
                    #print(f"[Autometrics] {collector.__class__.__name__} {report[collector.__class__.__name__]}")
                get_storage(backend='sqlite',report=report)
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