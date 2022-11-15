all: sqlite sqlite.wasm sqlite.wat sqlite-cov


SRCS = os.c shell.c sqlite3.c vfs.c
SRCS_COV = os-cov.c shell-cov.c sqlite3-cov.c vfs-cov.c
OBJS = os.o shell.o sqlite3.o vfs.o
FLAGS = -DDEBUG -O0 -g3 -DSQLITE_OS_OTHER
COV_FLAGS = -fprofile-arcs -ftest-coverage

sqlite: $(SRCS)
	gcc $(FLAGS) -o sqlite $(SRCS)

sqlite.wasm: $(SRCS)
	emcc $(FLAGS) -o sqlite.html $(SRCS)
	rm sqlite.html sqlite.js

sqlite.wat: sqlite.wasm
	wasm2wat sqlite.wasm > sqlite.wat

sqlite-cov: $(SRCS_COV)
	gcc $(COV_FLAGS) $(FLAGS) -o sqlite-cov $(SRCS_COV)

clean:
	rm -f sqlite sqlite-cov sqlite.wasm sqlite.wat sqlite.js sqlite.html *.gcno *.gcda *.gcov *.o
