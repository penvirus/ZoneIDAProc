import time
from collections import namedtuple

Endpoint = namedtuple('Endpoint', ['host', 'port'])
end_1 = Endpoint('1.1.1.1', 1111)

end_2 = Endpoint(host='2.2.2.2', port=2222)
end_3 = Endpoint(port=3333, host='3.3.3.3')
Pair = namedtuple('Pair', ['src', 'dst'])
pair = Pair(src=end_2, dst=end_3)

data = 'default'

while True:
    current = time.ctime()
    print '[%s]        data = %s' % (current, data)
    time.sleep(1)
