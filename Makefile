all:	hello

hello:	hello.c
	cc	-o $@ $<


run:	hello
	./hello
