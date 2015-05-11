#!/usr/bin/python

import subprocess
import sys
import os

def instrument_code(pid, filename):
    """given a list"""
    cmd = list()
    cmd.append('./gdb')
    cmd.append('--nw')
    cmd.append('--nh')
    cmd.append('--nx')
    cmd.append('--batch')
    cmd.append('--pid')
    cmd.append('%s' % pid)
    cmd.append('\'--eval-command=set scheduler-locking off\'')
    cmd.append('\'--eval-command=call dlopen("/tmp/pycode_instrumentation.so", 2)\'')
    cmd.append('\'--eval-command=call instrument_file("%s")\'' % filename)
    with open(os.devnull, 'w') as null:
        p = subprocess.Popen(' '.join(cmd), shell=True, close_fds=True, stdout=null, stderr=null)
        p.communicate()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: %s [pid]' % sys.argv[0]
        sys.exit(1)

    pid = int(sys.argv[1])

    filename = '/tmp/zone_ida_instrumentation.py'

    code = '''
import subprocess
import atexit
import threading
import inspect
import __main__
from ida_proc import IDAProc

app = IDAProc()

def make_kv(path, m, k):
    @app.route(path)
    def getter():
        return m[k]

__expand_type__ = (Endpoint, Pair)
def expand_object(prefix, obj):
    for k,v in obj.__dict__.items():
        if k.startswith('__'):
            continue
        if inspect.ismodule(v) or inspect.isroutine(v) or inspect.isclass(v):
            continue

        path = '%s/%s' % (prefix, k)
        if type(v) in __expand_type__:
            expand_object(path, v)
        else:
            make_kv(path, obj.__dict__, k)

def fusermount():
    p = subprocess.Popen(['/bin/fusermount', '-u', app.get_mount_point()], close_fds=True, shell=False)
    p.communicate()
atexit.register(fusermount)

expand_object('/', __main__)

import threading
t = threading.Thread(target=app.run)
t.daemon = True
t.start()
'''

    with open(filename, 'w') as f:
        f.write(code)
    instrument_code(pid, filename)

    os.remove(filename)
