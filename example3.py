import subprocess
import atexit
import threading
import inspect
import __main__
from collections import namedtuple
from ida_proc import IDAProc

app = IDAProc()

Endpoint = namedtuple('Endpoint', ['host', 'port'])
end_1 = Endpoint('1.1.1.1', 1111)

end_2 = Endpoint(host='2.2.2.2', port=2222)
end_3 = Endpoint(port=3333, host='3.3.3.3')
Pair = namedtuple('Pair', ['src', 'dst'])
pair = Pair(src=end_2, dst=end_3)

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

if __name__ == '__main__':
    expand_object('/', __main__)
    app.run()
