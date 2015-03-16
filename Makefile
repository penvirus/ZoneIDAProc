CFLAGS += -Wall -O2 -g -I/usr/include/python2.7

all:
	gcc $(CFLAGS) -g -Wl,-soname,pycode_instrumentation -fPIC -shared -o pycode_instrumentation.so pycode_instrumentation.c

clean:
	rm -f *.o
	rm -f pycode_instrumentation.so
