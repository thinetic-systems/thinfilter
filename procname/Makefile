PYTHON?=python
TESTFLAGS=-p -v
TESTOPTS=
SETUPFLAGS=
GCC=gcc
VER=2.5
DESTDIR=.

all: build

clean:
	rm -f *.o *.so

build:
	$(GCC) -c -fpic procnamemodule.c -DHAVE_CONFIG_H -I/usr/include/python$(VER) -I/usr/lib/python$(VER)/config
	$(GCC) -shared procnamemodule.o  -o $(DESTDIR)/procname.so
