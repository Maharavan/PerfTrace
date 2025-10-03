from perftrace.core.collectors import ExecutionCollector
from perftrace.core.collectors import MemoryCollector
from perftrace.core.collectors import CPUCollector
from perftrace.core.collectors import FileIOCollector
from perftrace.core.collectors import GarbageCollector
from perftrace.core.collectors import NetworkActivityCollector
from perftrace.core.collectors import ThreadContextCollector
from perftrace.storage import get_storage
import datetime
class PerfTraceContextManager:
    """
    Context manager for collecting metrics on code blocks.
    
    Args:
        cls_collectors: None (all collectors), 'all', list of collector names, or single collector name
    
    Examples:
        with PerfTraceContextManager() as metrics:
            expensive_operation()
        
        with PerfTraceContextManager(['memory', 'cpu']) as metrics:
            targeted_monitoring()
        
        reports = metrics.get_metrics()
    """
    def __init__(self,context_tag,cls_collectors=None):
        self.collectors = {
            "memory":MemoryCollector(),
            "cpu":CPUCollector(),
            "execution":ExecutionCollector(),
            "file":FileIOCollector(),
            "garbagecollector":GarbageCollector(),
            "ThreadContext": ThreadContextCollector(),
            "network":NetworkActivityCollector(),
        }
        self.context_tag = context_tag
        self.report = {}
        if cls_collectors is None or (isinstance(cls_collectors,str) and cls_collectors=="all"):
            self.active_collectors = self.collectors    
        elif isinstance(cls_collectors,list):
            try:
                self.active_collectors = {cls:self.collectors[cls] for cls in cls_collectors}
            except KeyError as e:
                available = list(self.collectors.keys())
                raise ValueError(f"Unknown collector. Available: {','.join(available)}") from e
        else:
            if not isinstance(cls_collectors, str):
                raise TypeError(f"Expected string, list, or None. Got {type(cls_collectors)}")          
            if cls_collectors not in self.collectors:
                available = list(self.collectors.keys())
                raise ValueError(f"Unknown collector '{cls_collectors}'. Available: {available}")    
            self.active_collectors = {cls_collectors:self.collectors[cls_collectors]}
        self.active_collectors["execution"] = ExecutionCollector()
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
        self.report["Timestamp"] = datetime.datetime.now()
        self.report["Function_name"] = None
        self.report["Context_tag"] = self.context_tag
        for _,collector in self.active_collectors.items():
            collector.stop()
            self.report[collector.__class__.__name__] = collector.report()
        get_storage(backend='duckdb',report=self.report)
        return False
    
    def get_metrics(self):
        return self.report