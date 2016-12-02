#/usr/bin/make -f

#
# Path of pypy checkout
PYPYPATH ?= pypy

# Invocation of pytest, defaults to pypy's stuff
# but may also be `py.test`
PYTEST ?= $(PYPYPATH)/pytest.py
RPYTHON ?= $(PYPYPATH)/rpython/bin/rpython --batch


TRANSLATE_TARGETS := translate-jit translate-no-callgraph translate-no-two-state \
		translate-no-strategies translate-no-type-size-specialization

PYFILES := $(shell find . -name '*.py' -type f)

.PHONY: all translate-jit-all $(TRANSLATE_TARGETS) translate-no-jit
.PHONY: setup test coverage

PYPY_EXECUTABLE := $(shell which pypy)

ifeq ($(PYPY_EXECUTABLE),)
RUNINTERP = python
else
RUNINTERP = $(PYPY_EXECUTABLE)
endif

translate-jit-all: $(TRANSLATE_TARGETS)
all: translate-jit-all translate-no-jit


translate-jit: pycket-c
translate-no-hidden-classes: pycket-c-no-hidden-classes
translate-no-prune-env: pycket-c-no-prune-env
translate-no-two-state: pycket-c-no-two-state
translate-no-callgraph: pycket-c-no-callgraph
translate-no-strategies: pycket-c-no-strategies
translate-no-type-size-specialization: pycket-c-no-type-size-specialization
translate-no-jit: pycket-c-nojit

pycket-c: $(PYFILES)
	$(RUNINTERP) $(RPYTHON) -Ojit --translation-jit_opencoder_model=big targetpycket.py

pycket-c-no-hidden-classes: $(PYFILES)
	$(RUNINTERP) $(RPYTHON) -Ojit --translation-jit_opencoder_model=big targetpycket.py --no-hidden-classes

pycket-c-no-prune-env: $(PYFILES)
	$(RUNINTERP) $(RPYTHON) -Ojit --translation-jit_opencoder_model=big targetpycket.py --no-prune-env

pycket-c-no-two-state: $(PYFILES)
	$(RUNINTERP) $(RPYTHON) -Ojit --translation-jit_opencoder_model=big targetpycket.py --no-two-state

pycket-c-no-callgraph: $(PYFILES)
	$(RUNINTERP) $(RPYTHON) -Ojit --translation-jit_opencoder_model=big targetpycket.py --no-callgraph

pycket-c-no-strategies: $(PYFILES)
	$(RUNINTERP) $(RPYTHON) -Ojit targetpycket.py --no-strategies

pycket-c-no-type-size-specialization: $(PYFILES)
	$(RUNINTERP) $(RPYTHON) -Ojit targetpycket.py --no-type-size-specialization

pycket-c-nojit: $(PYFILES)
	$(RUNINTERP) $(RPYTHON) targetpycket.py

debug: $(PYFILES)
	$(RUNINTERP) $(RPYTHON) -Ojit --translation-jit_opencoder_model=big --lldebug targetpycket.py

setup:
	raco pkg install -t dir pycket/pycket-lang/ || \
		raco pkg update --link pycket/pycket-lang
	hg -R $(PYPYPATH) pull && \
	hg -R $(PYPYPATH) update

test: $(PYFILES)
	$(PYTEST) pycket

test-bytecode: $(PYFILES)
	$(PYTEST) --bytecode go pycket

coverage: pycket/test/coverage_report .coverage
pycket/test/coverage_report .coverage: $(PYFILES)
	$(PYTEST) pycket --cov pycket \
		--cov-report=term-missing --cov-report=html
