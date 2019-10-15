import random
import string
import os
import time

# Configure script based on environment variables
PS = int(os.environ.get("STRPS", 10))
LEN = int(os.environ.get("STRLEN", 200))
SPREAD = int(os.environ.get("SPREAD", 10))

i = 0
T = time.time()
RATE = PS
TPS = PS

while True:
    GENLEN = int((LEN-13)*(1-((random.randint(0, SPREAD*2)-SPREAD)/200)))
    print ("Rate=", RATE, ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits + " " +
                                                " " + " ") for _ in range(GENLEN)))
    time.sleep(1 / TPS)
    i = i+1
    if i >= PS / 2:
        i = 0
        t2 = time.time()
        RATE = round(((PS / 2) / (t2 - T)), 2)
        T = t2
        TPS = TPS*(PS/RATE)
