#!/usr/bin/python

import thread
import time
import traceback
import requests


URL = "http://podinfo.kube-system.svc.nokia.net:9898"
LOCATION = "nokia"
PARAMS = {'address': LOCATION}
DELTA = 0.01


def worker(threadName):
    for x in range(0, 1000):
        time.sleep(DELTA)
        requests.get(url=URL, params=PARAMS)

try:
    for x in range(0, 3):
        thread.start_new_thread(worker, ("Thread-" + str(x), ))
except Exception as e:
    traceback.print_exc()

time.sleep(40)
