CFLAGS += -Wall -O2 -g -I/usr/include/python2.7

all: pycode_instrumentation.so

pycode_instrumentation.so: pycode_instrumentation.c
	gcc $(CFLAGS) -g -fPIC -shared -o pycode_instrumentation.so pycode_instrumentation.c

clean:
	rm -f pycode_instrumentation.so
