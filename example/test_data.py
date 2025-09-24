import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from autometrics.core import auto_metrics,auto_metrics_cl

@auto_metrics_cl()
class MyProcessor:
    @staticmethod
    def step1(x):
        print(f"Step1 processing {x}")
        return x + 1
    def step2(self, y):
        print(f"Step2 processing {y}")
        return y * 2

@auto_metrics()
def list_comprehensive():
    data = [i for i in range(100000)]
    return data

@auto_metrics(debug=False)
def normal_loop():
    data = []
    for i in range(100000):
        data.append(i)
    return data

@auto_metrics()
def trigger_memory_error():
    big_list = [0] * (10**10)

@auto_metrics()
def os_error():
    with open("/nonexistent/path/file.txt", "r") as f:
        f.read()

if __name__=='__main__':
    track_cl  = MyProcessor()
    track_cl.step1(1)
    lc = list_comprehensive()
    nl = normal_loop()
    # trigger_memory_error()