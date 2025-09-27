from .collectors import ExecutionCollector
from .collectors import MemoryCollector
from .collectors import CPUCollector
from .collectors import FileIOCollector
from .collectors import GarbageCollector
from .collectors import NetworkActivityCollector
from .collectors import ThreadContextCollector

class AutometricContextManager:
    """
    Context manager for collecting metrics on code blocks.
    
    Args:
        cls_collectors: None (all collectors), 'all', list of collector names, or single collector name
    
    Examples:
        with AutometricContextManager() as metrics:
            expensive_operation()
        
        with AutometricContextManager(['memory', 'cpu']) as metrics:
            targeted_monitoring()
        
        reports = metrics.get_metrics()
    """
    def __init__(self,cls_collectors=None):
        self.collectors = {
            "memory":MemoryCollector(),
            "cpu":CPUCollector(),
            "execution":ExecutionCollector(),
            "file":FileIOCollector(),
            "garbage":GarbageCollector(),
            "ThreadContext": ThreadContextCollector(),
            "network":NetworkActivityCollector(),
        }
        self.report = {}
        if cls_collectors is None or (isinstance(cls_collectors,str) and cls_collectors=="all"):
            self.active_collectors = self.collectors    
        elif isinstance(cls_collectors,list):
            try:
                self.active_collectors = {cls:self.collectors[cls] for cls in cls_collectors}
            except KeyError as e:
                available = list(self.collectors.keys())
                raise ValueError(f"Unknown collector. Available: {','.join(available)}")
        else:
            if not isinstance(cls_collectors, str):
                raise TypeError(f"Expected string, list, or None. Got {type(cls_collectors)}")
            
            if cls_collectors not in self.collectors:
                available = list(self.collectors.keys())
                raise ValueError(f"Unknown collector '{cls_collectors}'. Available: {available}")
            
            self.active_collectors = {cls_collectors:self.collectors[cls_collectors]}
    def __enter__(self):
        failed_collectors = []
        for name,collector in self.active_collectors.items():
            try:
                collector.start()
            except Exception as e:
                failed_collectors.append(f"{name}: {e}")
        if failed_collectors:
            print(f"Warning: Some collectors failed to start: {', '.join(failed_collectors)}")
        return self
    
    def __exit__(self,exc_type,exc_value,exc_traceback):
        for _,collector in self.active_collectors.items():
            collector.stop()
            self.report[collector.__class__.__name__] = collector.report()
        return False
    
    def get_metrics(self):
        return self.report


