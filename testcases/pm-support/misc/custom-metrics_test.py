from prometheus_client import start_http_server, Histogram
import random
import time

function_exec = Histogram('function_exec_time',
                          'Time spent processing a function',
                          ['func_name'])

def func():
    if (random.random() < 0.02):
        time.sleep(2)
        return
time.sleep(0.2)
start_http_server(9100)

while True:
    start_time = time.time()
    func()
    function_exec.labels(func_name="func").observe(time.time() - start_time)
