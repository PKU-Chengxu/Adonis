CFLAGS	= -I . \
	-O0 -g \
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
	-c -fno-elide-constructors

LIBSRC = modbus-data.c modbus-rtu.c modbus-tcp.c modbus.c
LIBCOVSRC = $(wildcard modbus*-cov.c)
TSTSRC = $(wildcard test-*.c)
LIBOBJ = $(LIBSRC:%.c=%.o)
LIBCOVOBJ = $(LIBCOVSRC:%.c=%.o)
TSTOBJ = $(TSTSRC:%.c=%.o)
TST = $(TSTSRC:%.c=%)  # test-rw test-floats test-illegal test-many test-slave test-bad test-raw test-exception
EXEC = mb-server mb-server-cov $(TST)

all: $(EXEC) mb-server.wasm mb-server.wat 

mb-server: $(LIBOBJ) mb-server.o
	$(CC) -I. -fno-elide-constructors -O0 -o mb-server $(LIBOBJ) mb-server.o 

mb-server-cov: $(LIBCOVOBJ) mb-server-cov.o
	$(CC) -I. -fprofile-arcs -ftest-coverage -o mb-server-cov $(LIBCOVOBJ) mb-server-cov.o

mb-server-cov.o: mb-server-cov.c
	$(CC) -I. -O0 -fprofile-arcs -ftest-coverage -c -o mb-server-cov.o mb-server-cov.c

$(LIBCOVOBJ): $(LIBCOVSRC)
	$(CC) -I. -O0 -fprofile-arcs -ftest-coverage -c -o $@ $(subst .o,.c,$@)

$(TST): $(TSTOBJ)
	$(CC) -I. -fno-elide-constructors -O0 -o $@ $(LIBOBJ) $(patsubst test-%,test-%.o,$@)

mb-server.wasm: $(LIBSRC) mb-server.c
	emcc -g3 -I. $(LIBSRC) mb-server.c -o mb-server.html

mb-server.wat: mb-server.wasm
	wasm2wat mb-server.wasm > mb-server.wat

clean:
	rm -f $(EXEC) mb-server.wasm mb-server.wat *.js *.html *.gcno *.gcda *.gcov *.o

