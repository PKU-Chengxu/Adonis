# you may need to change these for your system
CFLAGS	= -O0 -g \
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
MAKE = make
CC	= gcc
RM	= /bin/rm

TEX	= userguide music
ABC	= English Jigs Reels Strspys

all: abc2mtex abc2mtex-cov abc2mtex.wasm abc2mtex.wat 

# install: abc2mtex sort_in search
# 	$(RM) -f *.o

abc2mtex: abc2mtex.o abc.o tex.o index.o
	$(CC) -fno-elide-constructors -O0 -o abc2mtex abc2mtex.o abc.o tex.o index.o

abc2mtex-cov: abc2mtex-cov.o abc-cov.o tex-cov.o index-cov.o
	$(CC) -fprofile-arcs -ftest-coverage -o abc2mtex-cov abc2mtex-cov.o abc-cov.o tex-cov.o index-cov.o

abc2mtex-cov.o: abc2mtex-cov.c
	$(CC) -O0 -fprofile-arcs -ftest-coverage -c -DSTDC_HEADERS=1 -DHAVE_UNISTD_H=1 -DDIRENT=1 -DHAVE_ALLOCA_H=1 -o abc2mtex-cov.o abc2mtex-cov.c

abc-cov.o: abc-cov.c
	$(CC) -O0 -fprofile-arcs -ftest-coverage -c -DSTDC_HEADERS=1 -DHAVE_UNISTD_H=1 -DDIRENT=1 -DHAVE_ALLOCA_H=1 -o abc-cov.o abc-cov.c

tex-cov.o: tex-cov.c
	$(CC) -O0 -fprofile-arcs -ftest-coverage -c -DSTDC_HEADERS=1 -DHAVE_UNISTD_H=1 -DDIRENT=1 -DHAVE_ALLOCA_H=1 -o tex-cov.o tex-cov.c
	
index-cov.o: index-cov.c
	$(CC) -O0 -fprofile-arcs -ftest-coverage -c -DSTDC_HEADERS=1 -DHAVE_UNISTD_H=1 -DDIRENT=1 -DHAVE_ALLOCA_H=1 -o index-cov.o index-cov.c

abc2mtex.wasm: abc2mtex.c abc.c tex.c index.c
	emcc -g3 -DSTDC_HEADERS=1 -DHAVE_UNISTD_H=1 -DDIRENT=1 -DHAVE_ALLOCA_H=1 -D__GNU_LIBRARY__  abc2mtex.c abc.c tex.c index.c -o abc2mtex.html

abc2mtex.wat: abc2mtex.wasm
	wasm2wat abc2mtex.wasm > abc2mtex.wat

clean: 
	rm -f abc2mtex abc2mtex-cov abc2mtex.wasm abc2mtex.wat abc2mtex.js abc2mtex.html *.gcno *.gcda *.gcov *.o

# sort_in: sort_in.o index.o
# 	$(CC) $(CFLAGS) -o $@ sort_in.o index.o

# search: search.o abc.c tex.o index.o
# 	$(CC) $(CFLAGS) -o $@ search.o abc.o tex.o index.o

# index: *.abc
# 	abc2mtex -i *.abc
# 	sort_in

# ps: $(ABC:=.ps)

# tidy:
# 	$(RM) -f *.o index abc2mtex.log music.tex userguide.toc transpose.abc
# 	$(RM) -f $(TEX:=.dvi) $(TEX:=.log) $(TEX:=.ps) $(TEX:=.aux)
# 	$(RM) -f $(ABC:=.tex) $(ABC:=.dvi) $(ABC:=.log) $(ABC:=.ps) $(ABC:=.aux)

# clean: tidy
# 	$(RM) -f abc2mtex sort_in search

# .SUFFIXES:  .ps .dvi .tex .abc

# .abc.tex:
# 	abc2mtex -o $*.tex $*

# .abc.dvi:
# 	abc2mtex -o $*.tex $*
# 	tex $*

# .abc.ps:
# 	abc2mtex -o $*.tex $*
# 	tex $*
# 	dvips -o $*.ps $*.dvi -D 600

# .tex.dvi:
# 	tex $*

# .tex.ps:
# 	tex $*
# 	dvips -o $*.ps $*.dvi -D 600

# .dvi.ps:
# 	dvips -o $*.ps $*.dvi -D 600

