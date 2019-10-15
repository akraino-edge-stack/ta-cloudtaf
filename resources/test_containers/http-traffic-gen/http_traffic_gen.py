#!/usr/bin/python

import requests
import thread
import time
import traceback


URL = "http://podinfo.kube-system.svc.nokia.net:9898"
location = "nokia"
PARAMS = {'address': location}
delta = 0.01


def worker(threadName):
    for x in range(0, 1000):
        time.sleep(delta)
        requests.get(url=URL, params=PARAMS)

try:
    for x in range(0, 3):
        thread.start_new_thread(worker, ("Thread-" + str(x), ))
except Exception as e:
    traceback.print_exc()

time.sleep(40)
