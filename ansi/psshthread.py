# coding=utf8
import paramiko,os,threading
import time
import Queue
from models import logs


completed = Queue.Queue()
completed.put(0)


class sshthread(threading.Thread):

    def __init__(self, host, username, port, cmd, flags, sem):
        threading.Thread.__init__(self)
        self.host = host
        self.username = username
        self.port = int(port)
        self.cmd = cmd
        self.flags = flags
        self.sem = sem
        self.thread_stop = False

    def run(self):
        try:
            prikey = os.path.expanduser(self.flags["keyfile"])
            pkey = paramiko.RSAKey.from_private_key_file(prikey)
            ssh=paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=self.host, port=self.port, username=self.username, pkey=pkey, timeout=30)
            try:
                stdin,stdout,stderr = ssh.exec_command(self.cmd)
                self.flags["sta"] = "ok"
                log_completion(self.host, self.port, self.flags, stdout.read())
            except Exception,e:
                self.flags["sta"] = "fail"
                log_completion(self.host, self.port, self.flags, stdout.read())
                print e
            ssh.close()
        except Exception,e:
            log_completion(self.host, self.port, self.flags, e)
            print e
        self.sem.release()

    def stop(self):
        self.thread_stop=True


class uploadthread(threading.Thread):

    def __init__(self, host, username, port, local_file, remote_file, flags, sem):
        threading.Thread.__init__(self)
        self.host = host
        self.username = username
        self.port = int(port)
        self.local_file = local_file
        self.remote_file = remote_file
        self.flags = flags
        self.sem = sem
        self.thread_stop = False

    def run(self):
        try:
            prikey = os.path.expanduser(self.flags["keyfile"])
            pkey = paramiko.RSAKey.from_private_key_file(prikey)
            t=paramiko.Transport((self.host,self.port))
            t.connect(username=self.username, pkey=pkey)
            sftp=paramiko.SFTPClient.from_transport(t)
            try:
                sftp.put(self.local_file,self.remote_file)
                self.flags["sta"] = "ok"
                log_completion(self.host, self.port, self.flags, "SUCCESS")
            except Exception,e:
                self.flags["sta"] = "fail"
                log_completion(self.host, self.port, self.flags, e)
                print e
            t.close()
        except Exception,e:
            log_completion(self.host, self.port, self.flags, e)
            print e
        self.sem.release()

    def stop(self):
        self.thread_stop=True


def do_pscp(hosts, ports, username, local_file, remote_file, flags):
    if flags["logdir"] and not os.path.exists(flags["logdir"]):
        os.makedirs(flags["logdir"])
    sem = threading.Semaphore(flags["par"])
    paramiko.util.log_to_file(flags["logdir"] + "/parmiko.log")
    threads = []
    for i in range(len(hosts)):
        sem.acquire()
        t = uploadthread(hosts[i], username, ports[i], local_file, remote_file, flags, sem)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    return "job started..."


def do_pssh(hosts, ports, username, cmd, flags):
    if flags["logdir"] and not os.path.exists(flags["logdir"]):
        os.makedirs(flags["logdir"])
    sem = threading.Semaphore(flags["par"])
    paramiko.util.log_to_file(flags["logdir"] + "/parmiko.log")
    threads = []
    for i in range(len(hosts)):
        sem.acquire()
        t = sshthread(hosts[i], username, ports[i], cmd, flags, sem)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    return "job started..."


def log_completion(host, port, flags, exception=None):
    # Increment the count of complete ops. This will
    # drain the queue, causing subsequent calls of this
    # method to block.
    n = completed.get() + 1
    try:
        tstamp = time.asctime().split()[3] # Current time
        progress = "[%s]" % n
        success = "[SUCCESS]"
        failure = "[FAILURE]"
        exc = str(exception)
        if exception is not None and flags["sta"] == "fail":
            pathname = "%s/%s" % (flags["logdir"], host)
            msg = "%s %s %s %s:%s\n%s" % (progress, tstamp, failure, host, port, exc)
            f = open(pathname, "w")
            f.write(msg)
            f.close()
            db, sta = logs.objects.get_or_create(hostip=host,stime=os.path.basename(flags["logdir"]))
            db.progress = progress
            db.tstamp = tstamp
            db.status = failure
            db.logtype = flags["type"]
            db.exc = exc
            db.save()
        else:
            pathname = "%s/%s" % (flags["logdir"], host)
            msg = "%s %s %s %s:%s" % (progress, tstamp, success, host, port)
            f = open(pathname, "w")
            f.write(msg)
            f.close()
            db, sta = logs.objects.get_or_create(hostip=host,stime=os.path.basename(flags["logdir"]))
            db.progress = progress
            db.tstamp = tstamp
            db.status = success
            db.logtype = flags["type"]
            db.exc = exc
            db.save()
    finally:
        # Update the count of complete ops. This will re-fill
        # the queue, allowing other threads to continue with
        # output.
        completed.put(n)

if __name__ == "__main__":
    log_str = "1"
    flags = {'par': 32, 'timeout': 30, 'logdir': 'logs/pscp/' + log_str }
    do_pscp(["116.9.94.50"], [22], "root", "/etc/hosts", "/tmp/hos", flags)

