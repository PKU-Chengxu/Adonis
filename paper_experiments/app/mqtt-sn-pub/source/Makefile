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

TARGETS = mqtt-sn-pub mqtt-sn-pub-cov mqtt-sn-pub.wasm mqtt-sn-pub.wat mqtt-sn-sub mqtt-sn-dump mqtt-sn-serial-bridge

all: $(TARGETS)

mqtt-sn-pub: mqtt-sn-pub.o mqtt-sn.o
	$(CC) -fno-elide-constructors -O0 -o mqtt-sn-pub mqtt-sn-pub.o mqtt-sn.o

mqtt-sn-pub-cov: mqtt-sn-pub-cov.o mqtt-sn-cov.o
	$(CC) -fprofile-arcs -ftest-coverage -o mqtt-sn-pub-cov mqtt-sn-pub-cov.o mqtt-sn-cov.o

mqtt-sn-pub-cov.o: mqtt-sn-pub-cov.c
	$(CC) -O0 -fprofile-arcs -ftest-coverage -c -DSTDC_HEADERS=1 -DHAVE_UNISTD_H=1 -DDIRENT=1 -DHAVE_ALLOCA_H=1 -o mqtt-sn-pub-cov.o mqtt-sn-pub-cov.c

mqtt-sn-cov.o: mqtt-sn-cov.c
	$(CC) -O0 -fprofile-arcs -ftest-coverage -c -DSTDC_HEADERS=1 -DHAVE_UNISTD_H=1 -DDIRENT=1 -DHAVE_ALLOCA_H=1 -o mqtt-sn-cov.o mqtt-sn-cov.c

mqtt-sn-pub.wasm: mqtt-sn-pub.c mqtt-sn.c
	emcc -g3 -DSTDC_HEADERS=1 -DHAVE_UNISTD_H=1 -DDIRENT=1 -DHAVE_ALLOCA_H=1 -D__GNU_LIBRARY__  mqtt-sn-pub.c mqtt-sn.c -o mqtt-sn-pub.html

mqtt-sn-pub.wat: mqtt-sn-pub.wasm
	wasm2wat mqtt-sn-pub.wasm > mqtt-sn-pub.wat

# other executables to support testing
mqtt-sn-sub: mqtt-sn-sub.o mqtt-sn.o
	$(CC) -fno-elide-constructors -O0 -o mqtt-sn-sub mqtt-sn-sub.o mqtt-sn.o

mqtt-sn-dump: mqtt-sn-dump.o mqtt-sn.o
	$(CC) -fno-elide-constructors -O0 -o mqtt-sn-dump mqtt-sn-dump.o mqtt-sn.o

mqtt-sn-serial-bridge: mqtt-sn-serial-bridge.o mqtt-sn.o
	$(CC) -fno-elide-constructors -O0 -o mqtt-sn-serial-bridge mqtt-sn-serial-bridge.o mqtt-sn.o

clean: 
	rm -f $(TARGETS) mqtt-sn-pub.js mqtt-sn-pub.html *.gcno *.gcda *.gcov *.o

# CC=cc
# PACKAGE=mqtt-sn-tools
# VERSION=0.0.7
# CFLAGS=-g -Wall -DVERSION=$(VERSION)
# LDFLAGS=
# INSTALL?=install
# prefix=/usr/local

# TARGETS=mqtt-sn-dump mqtt-sn-pub mqtt-sn-sub mqtt-sn-serial-bridge

# .PHONY : all install uninstall clean dist test coverage


# all: $(TARGETS)

# $(TARGETS): %: mqtt-sn.o %.o
# 	$(CC) $(LDFLAGS) -o $@ $^

# %.o : %.c mqtt-sn.h
# 	$(CC) $(CFLAGS) -c $<

# install: $(TARGETS)
# 	$(INSTALL) -d "$(DESTDIR)$(prefix)/bin"
# 	$(INSTALL) -s $(TARGETS) "$(DESTDIR)$(prefix)/bin"

# uninstall:
# 	@for target in $(TARGETS); do \
# 		cmd="rm -f $(DESTDIR)$(prefix)/bin/$$target"; \
# 		echo "$$cmd" && $$cmd; \
# 	done

# clean:
# 	-rm -f *.o *.gcda *.gcno $(TARGETS)
# 	-rm -Rf coverage

# dist:
# 	distdir='$(PACKAGE)-$(VERSION)'; mkdir $$distdir || exit 1; \
# 	list=`git ls-files`; for file in $$list; do \
# 		cp -pR $$file $$distdir || exit 1; \
# 	done; \
# 	tar -zcf $$distdir.tar.gz $$distdir; \
# 	rm -fr $$distdir

# test: all
# 	@(which bundle > /dev/null) || (echo "Ruby Bundler is not installed"; exit -1)
# 	cd test && bundle install && bundle exec rake test

# # Use gcc for coverage report - it works better than clang/llvm
# coverage: CC=gcc
# coverage: CFLAGS += --coverage
# coverage: LDFLAGS += --coverage
# coverage: clean test
# 	mkdir -p coverage
# 	lcov \
#     --capture \
#     --directory . \
#     --no-external \
#     --output coverage/lcov.info
# 	genhtml \
#     --title 'MQTT-SN Tools' \
#     --output-directory coverage \
#     coverage/lcov.info
