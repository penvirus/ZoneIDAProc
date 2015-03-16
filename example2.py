import subprocess
import sys
import os

def instrument_code(pid, filename):
    """given a list"""
    cmd = list()
    cmd.append('gdb')
    cmd.append('--nw')
    cmd.append('--nh')
    cmd.append('--nx')
    cmd.append('--batch')
    cmd.append('--pid')
    cmd.append('%s' % pid)
    cmd.append('\'--eval-command=call dlopen("/home/tbshr/pycode_instrumentation.so", 2)\'')
    cmd.append('\'--eval-command=call instrument_file("%s")\'' % filename)
    with open(os.devnull, 'w') as null:
        #p = subprocess.Popen(' '.join(cmd), shell=True, close_fds=True, stdout=null, stderr=null)
        p = subprocess.Popen(' '.join(cmd), shell=True, close_fds=True)
    p.communicate()

if __name__ == '__main__':
    pid = int(sys.argv[1])

    filename = '/tmp/zone_ida_instrumentation.py'

    code = '''from ida_proc import IDAProc
app = IDAProc()
import __main__
for k,v in __main__.__dict__.items():
    @app.route('__main__/%s' % k)
    def x():
        return str(v)
app.run(foreground=True)
'''

    with open(filename, 'w') as f:
        f.write(code)
    instrument_code(pid, filename)
