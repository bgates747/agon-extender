PYTHON ?= python3
ASM ?= ez80asm

.PHONY: all
all: grid.bin

grid.vdu: generate.py
	$(PYTHON) generate.py

grid.bin: grid.asm grid.vdu
	$(ASM) grid.asm grid.bin
