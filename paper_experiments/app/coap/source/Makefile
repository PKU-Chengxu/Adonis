CFLAGS = -DDEBUG -O0 -g \
	-fno-builtin-strcpy -fno-exceptions -fno-web \
	-fno-var-tracking-assignments -fno-var-tracking -fno-unwind-tables \
	-fno-tree-scev-cprop  -fno-tree-reassoc -fno-tree-phiprop \
	-fno-tree-loop-optimize \
	-fno-tree-loop-ivcanon -fno-tree-loop-im -fno-tree-loop-if-convert \
	-fno-tree-forwprop -fno-tree-cselim -fno-trapping-math \
	-fthreadsafe-statics -fno-strict-volatile-bitfields -fno-stdarg-opt \
	-fno-ssa-backprop  -fno-split-ivs-in-unroller -fno-signed-zeros \
	-fno-shrink-wrap-separate -fno-short-enums -fno-schedule-fusion \
	-fno-sched-stalled-insns-dep -fno-sched-spec-insn-heuristic \
	-fno-sched-spec -fno-sched-rank-heuristic -fno-sched-last-insn-heuristic \
	-fno-sched-interblock  -fno-sched-group-heuristic \
	-fno-sched-dep-count-heuristic -fno-sched-critical-path-heuristic \
	-fno-rtti -fno-rename-registers -fno-reg-struct-return \
	-fno-printf-return-value -fno-prefetch-loop-arrays -fno-plt  \
	-fno-peephole -fno-math-errno -fno-lifetime-dse -fno-jump-tables \
	-fno-ivopts -fno-ira-share-spill-slots -fno-ira-share-save-slots \
	-fno-ira-hoist-pressure -fno-inline-atomics -fno-inline \
	-fno-gcse-lm -fno-function-cse -fno-fp-int-builtin-inexact \
	-fno-early-inlining -fno-dse -fno-delete-null-pointer-checks \
	-fno-dce -fno-auto-inc-dec -fno-asynchronous-unwind-tables \
	-fno-aggressive-loop-optimizations \
	-c -DSTDC_HEADERS=1 -DHAVE_UNISTD_H=1 -DDIRENT=1 \
	-DHAVE_ALLOCA_H=1 -fno-elide-constructors
# -DIPV6
# SRC = $(wildcard *.c)
# OBJ = $(SRC:%.c=%.o)
# DEPS = $(SRC:%.c=%.d)
# EXEC = coap client

# all: $(EXEC)

# -include $(DEPS)

# $(EXEC): $(OBJ)
# 	@$(CC) $(CFLAGS) -o $@ $^

# %.o: %.c %.d
# 	@$(CC) -c $(CFLAGS) -o $@ $<

# %.d: %.c
# 	@$(CC) -MM $(CFLAGS) $< > $@

# clean:
# 	@$(RM) $(EXEC) $(OBJ) $(DEPS)

COVOBJ = coap-cov.o endpoints-cov.o main-posix-cov.o
OBJ = coap.o endpoints.o main-posix.o
SRC = coap.c endpoints.c main-posix.c

all: coap coap-cov client coap.wasm coap.wat

coap: $(OBJ)
	gcc -DDEBUG -fno-elide-constructors -O0 -o coap $(OBJ)

coap-cov: $(COVOBJ)
	gcc -DDEBUG -fprofile-arcs -ftest-coverage -o coap-cov $(COVOBJ)

coap-cov.o: coap-cov.c
	gcc -DDEBUG -O0 -fprofile-arcs -ftest-coverage -c -DSTDC_HEADERS=1 -DHAVE_UNISTD_H=1 -DDIRENT=1 -DHAVE_ALLOCA_H=1 -o coap-cov.o coap-cov.c

endpoints-cov.o: endpoints-cov.c
	gcc -DDEBUG -O0 -fprofile-arcs -ftest-coverage -c -DSTDC_HEADERS=1 -DHAVE_UNISTD_H=1 -DDIRENT=1 -DHAVE_ALLOCA_H=1 -o endpoints-cov.o endpoints-cov.c

main-posix-cov.o: main-posix-cov.c
	gcc -DDEBUG -O0 -fprofile-arcs -ftest-coverage -c -DSTDC_HEADERS=1 -DHAVE_UNISTD_H=1 -DDIRENT=1 -DHAVE_ALLOCA_H=1 -o main-posix-cov.o main-posix-cov.c

coap.wasm: $(SRC)
	emcc -g3 -DDEBUG -DSTDC_HEADERS=1 -DHAVE_UNISTD_H=1 -DDIRENT=1 -DHAVE_ALLOCA_H=1 -D__GNU_LIBRARY__  $(SRC) -o coap.html

coap.wat: coap.wasm
	wasm2wat coap.wasm > coap.wat

client: client.cc common.cc
	g++ -std=c++14 -Wall -Wextra -I/usr/local/include  -c -o client.o client.cc
	g++ -std=c++14 -Wall -Wextra -I/usr/local/include  -c -o common.o common.cc
	g++ -std=c++14 -Wall -Wextra -I/usr/local/include  client.o common.o  -L/usr/local/lib -lcoap-3-openssl -o client

clean:
	rm -f coap coap-cov coap.wasm coap.wat coap.js coap.html *.gcno *.gcda *.gcov *.o client

