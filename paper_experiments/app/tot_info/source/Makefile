all: tot_info tot_info-cov tot_info.wasm tot_info.wat

tot_info: tot_info.o
	gcc -fno-elide-constructors -O0 -o tot_info tot_info.o -lm

tot_info-cov: tot_info-cov.o
	gcc -fprofile-arcs -ftest-coverage -o tot_info-cov tot_info-cov.o -lm

tot_info.o: tot_info.c std.h gamma.h chisq.h
	gcc -O0 -g \
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
	-DHAVE_ALLOCA_H=1 -fno-elide-constructors tot_info.c

tot_info-cov.o: tot_info-cov.c std.h gamma.h chisq.h
	gcc -O0 -fprofile-arcs -ftest-coverage -c -DSTDC_HEADERS=1 -DHAVE_UNISTD_H=1 -DDIRENT=1 -DHAVE_ALLOCA_H=1 -o tot_info-cov.o tot_info-cov.c

tot_info.wasm: tot_info.c
	emcc -g3 -DSTDC_HEADERS=1 -DHAVE_UNISTD_H=1 -DDIRENT=1 -DHAVE_ALLOCA_H=1 -D__GNU_LIBRARY__ tot_info.c -o tot_info.html

tot_info.wat: tot_info.wasm
	wasm2wat tot_info.wasm > tot_info.wat

clean: 
	rm -f tot_info tot_info-cov tot_info.o tot_info-cov.o tot_info.wasm tot_info.js tot_info.html tot_info-cov.gcno tot_info-cov.gcda tot_info-cov.c.gcov