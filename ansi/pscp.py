#!/usr/bin/env python
# -*- Mode: python -*-
#
import fcntl
import os
import pwd
import re
import subprocess
import threading
import datetime
from basethread import BaseThread

_DEFAULT_PARALLELISM = 32
_DEFAULT_TIMEOUT     = None # "infinity" by default
log_str = str(datetime.datetime.now().strftime('%Y%m%d%H%M'))

#flags = {'par': 32, 'verbose': None, 'hosts': 'a', 'user': 'root', 'timeout': 10, 'recursive': None, 'errdir': None, 'options': None, 'outdir': None}
flags = {'par': 32, 'verbose': None, 'timeout': 30, 'recursive': None, 'errdir': 'logs/pscp/' + log_str, 'options': None, 'outdir': 'logs/pscp/' + log_str}

def do_pscp(hosts, ports, user, local, remote):
    if flags["outdir"] and not os.path.exists(flags["outdir"]):
        os.makedirs(flags["outdir"])
    if flags["errdir"] and not os.path.exists(flags["errdir"]):
        os.makedirs(flags["errdir"])
    sem = threading.Semaphore(flags["par"])
    threads = []
    for i in range(len(hosts)):
        sem.acquire()
        cmd = "scp -qC -P %d %s %s@%s:%s" %(ports[i], local, user, hosts[i], remote)
        t = BaseThread(hosts[i], ports[i], cmd, flags, sem)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

if __name__ == "__main__":
    subprocess._cleanup = lambda : None
    pass
