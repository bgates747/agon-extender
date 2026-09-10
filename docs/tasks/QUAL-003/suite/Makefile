ASM ?= ez80asm
PYTHON ?= $(abspath ../../../../.venv/bin/python)
ENV_ROOT ?= $(HOME)/Agon/mystuff/agon-dev-env
APP ?= bitmaps
PAGE ?=

API_FILES := build/paired-identity.inc src/asm/paired.inc $(wildcard vendor/nurples/*.inc) src/asm/api.inc
BITMAP_INPUTS := $(wildcard assets/bitmaps/source/*)

.PHONY: all clean check review emulator-setup deploy select run
.DELETE_ON_ERROR:

all: tgt/shapes.bin tgt/bitmaps.bin

check: all
	$(PYTHON) tests/validate_shapes.py
	$(PYTHON) tests/validate_bitmaps.py

# The upstream single-display review/deployment recipe is not valid for this
# paired EMOS fixture. Use the task-owned prepare_review.py profile builder.
review emulator-setup deploy select run:
	@echo "Use QUAL-003/scripts/prepare_review.py; upstream deployment is disabled."
	@exit 2

build/paired-identity.inc: ../identity.json scripts/build_identity.py $(wildcard src/asm/*) $(wildcard vendor/nurples/*) $(wildcard scripts/*.py) $(BITMAP_INPUTS) Makefile
	$(PYTHON) scripts/build_identity.py

# Assemble a staged source so listings and symbols stay under build/.
tgt/hello.bin: src/asm/hello.asm $(API_FILES) Makefile
	mkdir -p build tgt
	cp src/asm/hello.asm build/hello.asm
	cd build && $(ASM) hello.asm ../tgt/hello.bin -c -l -s

build/shapes-data.stamp: scripts/build_shapes.py scripts/shapes_pages.py
	$(PYTHON) scripts/build_shapes.py
	touch $@

tgt/shapes.bin: src/asm/shapes.asm build/shapes-data.stamp $(API_FILES) Makefile
	mkdir -p build tgt
	cp src/asm/shapes.asm build/shapes.asm
	cd build && $(ASM) shapes.asm ../tgt/shapes.bin -c -l -s

build/bitmaps-data.stamp: scripts/bitmap_suite.py scripts/bitmap_assets.py $(BITMAP_INPUTS)
	$(PYTHON) scripts/bitmap_suite.py
	touch $@

tgt/bitmaps.bin: src/asm/bitmaps.asm src/asm/bitmap_adapters.inc build/bitmaps-data.stamp $(API_FILES) Makefile
	mkdir -p build tgt
	cp src/asm/bitmaps.asm build/bitmaps.asm
	cd build && $(ASM) bitmaps.asm ../tgt/bitmaps.bin -c -l -s

clean:
	rm -f build/hello.asm build/hello.lst build/hello.symbols build/hello.lbl tgt/hello.bin
	rm -f build/shapes.asm build/shapes.lst build/shapes.symbols build/shapes.lbl tgt/shapes.bin
	rm -f build/shapes-data.stamp build/shapes-data.inc build/catalog.json build/shp??.vdu build/shp??.probes build/shp??.json
	rm -f build/bitmaps.asm build/bitmaps.lst build/bitmaps.symbols build/bitmaps.lbl tgt/bitmaps.bin
	rm -f build/bitmaps-data.stamp build/bitmaps-data.inc build/bitmaps-catalog.json build/bitmaps-cleanup.vdu build/bsp??_??.vm build/bsp??_??.probes
	rm -rf tgt/assets/bitmaps
