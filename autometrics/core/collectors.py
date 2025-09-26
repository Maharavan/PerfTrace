from collections import defaultdict
import os
import time
import tracemalloc
import psutil
import gc
from abc import ABC,abstractmethod

class BaseCollector(ABC):
    @abstractmethod
    def start(self):
        """Start collecting metrics"""
        pass
    @abstractmethod
    def stop(self):
        """Stop collecting metrics"""
        pass
    @abstractmethod
    def report(self):
        """Return collected metrics"""
        pass


class ExecutionCollector(BaseCollector):
    def __init__(self):
        self.start_time = None
        self.stop_time = None
        self.exec_time = None
    def start(self):
        self.start_time =  time.perf_counter()
    
    def stop(self):
        self.stop_time =  time.perf_counter()
    
    def report(self):
        if self.start_time is not None and self.stop_time is not None:
            self.exec_time = self.stop_time-self.start_time
        return {
            "execution_time":self.exec_time,
            "start_time":self.start_time,
            "end_time":self.stop_time
        }

    

class CPUCollector(BaseCollector):
    def __init__(self):
        self.current_process = psutil.Process(os.getpid())
        self.cpu_usage_start = None
        self.cpu_usage_end = None
        self.ram_delta = None
        self.avg_cpu_percentage = None

    def start(self):
        self.cpu_mem_start =  self.current_process.memory_info().rss /(1024**2)
        self.cpu_usage_start = self.current_process.cpu_percent(interval=0.1)

    def stop(self):
        self.cpu_mem_end =  self.current_process.memory_info().rss /(1024**2)
        self.cpu_usage_end = self.current_process.cpu_percent(interval=0.1)
        
    def report(self):
        if self.cpu_mem_start is not None and self.cpu_mem_end is not None:
            self.ram_delta = self.cpu_mem_end-self.cpu_mem_start
            

        if self.cpu_usage_end is not None and self.cpu_usage_start is not None:
            self.avg_cpu_percentage = (self.cpu_usage_end+self.cpu_usage_start)/2
        
        return {
            "ram_delta":self.ram_delta,
            "start_ram":self.cpu_mem_start,
            "end_ram":self.cpu_mem_end,
            "avg_cpu_percentage":self.avg_cpu_percentage,
            "cpu_usage_start":self.cpu_usage_start,
            "cpu_usage_end":self.cpu_usage_end
        }

class MemoryCollector(BaseCollector):
    def __init__(self):
        self.current_mem = None
        self.peak_mem = None
    def start(self):
        if tracemalloc.is_tracing():
            tracemalloc.stop()
        tracemalloc.start()
    def stop(self):
        self.current_mem,self.peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
    
    def report(self):
        return {
            "current_memory":self.current_mem,
            "peak_memory": self.peak_mem
        }

class FileIOCollector(BaseCollector):
    def __init__(self):
        self.current_process = psutil.Process(os.getpid())
        self.start_io = None
        self.stop_io = None
        self.read_bytes_delta = None
        self.write_bytes_delta = None
        self.read_count_delta = None
        self.write_count_delta = None
        self.other_count_delta = None
        self.other_bytes_delta = None

    def start(self):
        self.start_io = self.current_process.io_counters()
    
    def stop(self):
        self.stop_io = self.current_process.io_counters()

    def report(self):
        if self.start_io is not None and self.stop_io is not None:
            self.read_bytes_delta = self.stop_io.read_bytes - self.start_io.read_bytes
            self.write_bytes_delta = self.stop_io.write_bytes - self.start_io.write_bytes
            self.read_count_delta = self.stop_io.read_count - self.start_io.read_count
            self.write_count_delta = self.stop_io.write_count - self.start_io.write_count
            self.other_count_delta = getattr(self.stop_io, "other_count", 0) - getattr(self.start_io, "other_count", 0)
            self.other_bytes_delta = getattr(self.stop_io, "other_bytes", 0) - getattr(self.start_io, "other_bytes", 0)

        return {
            "read_bytes": self.read_bytes_delta,
            "write_bytes": self.write_bytes_delta,
            "read_count": self.read_count_delta,
            "write_count": self.write_count_delta,
            "other_count": self.other_count_delta,
            "other_bytes": self.other_bytes_delta
        }

class GarbageCollector(BaseCollector):
    def __init__(self):
        self.initial_gc_count = None
        self.final_gc_count = None
        self.delta_gc_count = None
        self.gc_events = []
    def _callback(self,phase,info):
        self.gc_events.append({
            "phase":phase,
            "info": info
        })

    def start(self):
        self.initial_gc_count = gc.get_count()
        gc.callbacks.append(self._callback)
    
    def stop(self):
        self.final_gc_count = gc.get_count()
        self.delta_gc_count = tuple (v2-v1 for v1,v2 in zip(self.initial_gc_count,self.final_gc_count))
        if self._callback in gc.callbacks:
            gc.callbacks.remove(self._callback)
    
    def report(self):
        return {
            "initial_gc_count":self.initial_gc_count,
            "final_gc_count": self.final_gc_count,
            "delta_gc_count": self.delta_gc_count,
            "gc_events":self.gc_events,
        }
        
class NetworkActivityCollector(BaseCollector):
    def __init__(self):
        super().__init__()
        self.initial_tcp_connection = 0
        self.initial_udp_connection = 0
        self.final_tcp_connection = 0
        self.final_udp_connection = 0
        self.initial_bytes_sent = 0
        self.final_bytes_sent = 0
        self.bytes_sent_delta = 0
        self.initial_bytes_recv = 0
        self.final_bytes_recv = 0
        self.bytes_recv_delta = 0
        self.tcp_connection_delta = 0
        self.udp_connection_delta = 0
        self.socket_states = defaultdict(int)
    def start(self):  
        self.initial_tcp_connection = len(psutil.net_connections(kind='tcp'))
        self.initial_udp_connection = len(psutil.net_connections(kind='udp'))
        self.initial_bytes_sent = psutil.net_io_counters().bytes_sent
        self.initial_bytes_recv = psutil.net_io_counters().bytes_recv

    def stop(self):
        tcp_conns = psutil.net_connections(kind="tcp")
        udp_conns = psutil.net_connections(kind="udp")
        
        self.final_tcp_connection = len(tcp_conns)
        self.final_udp_connection = len(udp_conns)

        final_soc = tcp_conns+udp_conns

        for conn in final_soc:
            self.socket_states[conn.status]+=1
        self.final_bytes_sent = psutil.net_io_counters().bytes_sent
        self.final_bytes_recv = psutil.net_io_counters().bytes_recv

    def report(self):
        self.tcp_connection_delta = self.final_tcp_connection - self.initial_tcp_connection
        self.udp_connection_delta = self.final_udp_connection - self.initial_udp_connection
        self.bytes_sent_delta = self.final_bytes_sent - self.initial_bytes_sent
        self.bytes_recv_delta = self.final_bytes_recv-self.initial_bytes_recv
        return {
            "tcp_connection_delta": self.tcp_connection_delta,
            "udp_connection_delta": self.udp_connection_delta,
            "tcp_connection": self.final_tcp_connection,
            "udp_connection": self.final_udp_connection,
            "bytes_sent":self.final_bytes_sent,
            "bytes_received":self.final_bytes_recv,
            "bytes_sent_delta":self.bytes_sent_delta,
            "bytes_received_delta":self.bytes_recv_delta,
            "connection_type": dict(self.socket_states)
        }
    
class SystemCollector(BaseCollector):
    def start(self):
        pass
    def stop(self):
        pass
    def report(self):
        system_memory = psutil.virtual_memory()

        return {
            "total_system_memory": system_memory.total,
            "available_system_memory":system_memory.available,
            "used_memory":system_memory.used,
            "free_memory":system_memory.free,
            "memory_percentage":system_memory.percent
        }
    
class ThreadContextCollector(BaseCollector):
    def __init__(self):
        super().__init__()
        self.current_process = psutil.Process(os.getpid())
        self.initial_thread = 0
        self.final_thread = 0
        self.initial_ctx_switches = None
        self.final_ctx_switches = None

    def start(self):
        self.initial_thread = self.current_process.num_threads()
        self.initial_ctx_switches = self.current_process.num_ctx_switches()
    
    def stop(self):
        self.final_thread = self.current_process.num_threads()
        self.final_ctx_switches = self.current_process.num_ctx_switches()
    def report(self):
        return {
            "threads_delta": self.final_thread - self.initial_thread,
            "ctx_switches_voluntary_delta": self.final_ctx_switches.voluntary - self.initial_ctx_switches.voluntary,
            "ctx_switches_involuntary_delta": self.final_ctx_switches.involuntary - self.initial_ctx_switches.involuntary,
        }
    
