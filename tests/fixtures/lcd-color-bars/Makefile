PYTHON ?= python3
ASM ?= ez80asm

.PHONY: all clean
all: bars.bin

bars.vdu: generate.py
	$(PYTHON) generate.py

bars.bin: bars.asm bars.vdu
	$(ASM) bars.asm bars.bin

clean:
	rm -f bars.bin
