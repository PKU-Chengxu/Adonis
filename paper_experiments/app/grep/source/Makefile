DEFS = -DGREP  -DSTDC_HEADERS=1 -DHAVE_STRING_H=1 -DHAVE_SYS_PARAM_H=1 -DHAVE_UNISTD_H=1 -DHAVE_ALLOCA_H=1 -DHAVE_GETPAGESIZE=1 -DHAVE_MEMCHR=1 -DHAVE_STRERROR=1 -DHAVE_VALLOC=1 -DHAVE_WORKING_MMAP=1
CFLAGS = $(DEFS) -O0 -g \
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

SRCS = grep.c getopt.c regex.c dfa.c kwset.c obstack.c search.c
OBJS = grep.o getopt.o regex.o dfa.o kwset.o obstack.o search.o
COVOBJ = grep-cov.o getopt-cov.o regex-cov.o dfa-cov.o kwset-cov.o obstack-cov.o search-cov.o

all: grep grep-cov grep.wasm grep.wat

grep: $(OBJS)
	gcc -fno-elide-constructors -O0 -o grep $(OBJS)

grep-cov: $(COVOBJ)
	gcc $(DEFS) -fprofile-arcs -ftest-coverage -o grep-cov $(COVOBJ)

grep-cov.o: grep-cov.c
	gcc $(DEFS) -O0 -fprofile-arcs -ftest-coverage -c -DSTDC_HEADERS=1 -DHAVE_UNISTD_H=1 -DDIRENT=1 -DHAVE_ALLOCA_H=1 -o grep-cov.o grep-cov.c

getopt-cov.o: getopt-cov.c
	gcc $(DEFS) -O0 -fprofile-arcs -ftest-coverage -c -DSTDC_HEADERS=1 -DHAVE_UNISTD_H=1 -DDIRENT=1 -DHAVE_ALLOCA_H=1 -o getopt-cov.o getopt-cov.c

regex-cov.o: regex-cov.c
	gcc $(DEFS) -O0 -fprofile-arcs -ftest-coverage -c -DSTDC_HEADERS=1 -DHAVE_UNISTD_H=1 -DDIRENT=1 -DHAVE_ALLOCA_H=1 -o regex-cov.o regex-cov.c

dfa-cov.o: dfa-cov.c
	gcc $(DEFS) -O0 -fprofile-arcs -ftest-coverage -c -DSTDC_HEADERS=1 -DHAVE_UNISTD_H=1 -DDIRENT=1 -DHAVE_ALLOCA_H=1 -o dfa-cov.o dfa-cov.c

kwset-cov.o: kwset-cov.c
	gcc $(DEFS) -O0 -fprofile-arcs -ftest-coverage -c -DSTDC_HEADERS=1 -DHAVE_UNISTD_H=1 -DDIRENT=1 -DHAVE_ALLOCA_H=1 -o kwset-cov.o kwset-cov.c

obstack-cov.o: obstack-cov.c
	gcc $(DEFS) -O0 -fprofile-arcs -ftest-coverage -c -DSTDC_HEADERS=1 -DHAVE_UNISTD_H=1 -DDIRENT=1 -DHAVE_ALLOCA_H=1 -o obstack-cov.o obstack-cov.c

search-cov.o: search-cov.c
	gcc $(DEFS) -O0 -fprofile-arcs -ftest-coverage -c -DSTDC_HEADERS=1 -DHAVE_UNISTD_H=1 -DDIRENT=1 -DHAVE_ALLOCA_H=1 -o search-cov.o search-cov.c

grep.wasm: $(SRCS)
	emcc -g3 $(DEFS) -DSTDC_HEADERS=1 -DHAVE_UNISTD_H=1 -DDIRENT=1 -DHAVE_ALLOCA_H=1 -D__STDC__ $(SRCS) -o grep.html

grep.wat: grep.wasm
	wasm2wat grep.wasm > grep.wat

clean:
	rm -f grep grep-cov grep.wasm grep.wat grep.js grep.html *.gcno *.gcda *.gcov *.o
