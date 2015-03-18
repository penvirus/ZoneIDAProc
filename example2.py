import time
import threading
import subprocess
import atexit
from gevent import spawn, sleep
from ida_proc import IDAProc

data = dict()
data['data'] = 'default'

def main():
    while True:
        print "[%s]        data['data'] = %s" % (time.ctime(), data['data'])
        sleep(1)

def proc():
    app = IDAProc()

    @app.route('data')
    def getter():
        return data['data']

    @app.route('data', method='SET')
    def setter(d):
        data['data'] = d
        return data['data']

    def fusermount():
        p = subprocess.Popen(['/bin/fusermount', '-u', app.get_mount_point()], close_fds=True, shell=False)
        p.communicate()
    atexit.register(fusermount)

    app.run()

if __name__ == '__main__':
    t = threading.Thread(target=proc)
    t.daemon = True
    t.start()
    spawn(main).join()
