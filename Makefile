CFLAGS += -Wall -O2 -g -I/usr/include/python2.7

all: pycode_instrumentation.so

pycode_instrumentation.so: pycode_instrumentation.c
	gcc $(CFLAGS) -g -fPIC -shared -o pycode_instrumentation.so pycode_instrumentation.c

install: pycode_instrumentation.so
	install -m 644 pycode_instrumentation.so /tmp/pycode_instrumentation.so

clean:
	rm -f pycode_instrumentation.so
	rm -f *.pyc

.PHONY: all clean install
