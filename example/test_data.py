import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from autometrics.core.decorators import auto_metrics,auto_metrics_cl
from autometrics.core.context_manager import AutometricContextManager
@auto_metrics_cl
class MyProcessor:
    @staticmethod
    def step1(x):
        print(f"Step1 processing {x}")
        return x + 1
    def step2(self, y):
        print(f"Step2 processing {y}")
        return y * 2

@auto_metrics(profilers="all")
def list_comprehensive():
    data = [i for i in range(100000)]
    return data

@auto_metrics(profilers="all")
def normal_loop():
    data = []
    for i in range(100000):
        data.append(i)
    return data

@auto_metrics(profilers=["cpu","memory"])
def trigger_memory_error():
    big_list = [0] * (10**10)

@auto_metrics()
def os_error():
    with open("/nonexistent/path/file.txt", "r") as f:
        f.read()

if __name__=='__main__':
    # track_cl  = MyProcessor()
    # track_cl.step1(1)
    lc = list_comprehensive()
    nl = normal_loop()
    #trigger_memory_error()
    # with AutometricContextManager() as collectors:
    #     work = [x ** 2 for x in range(100000)]

    # print(collectors.get_metrics())
