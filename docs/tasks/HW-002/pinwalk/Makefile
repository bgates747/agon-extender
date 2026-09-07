NAME = PWBOOT
AGONDEV_TOOLCHAIN ?= $(shell agondev-config --prefix)
include $(AGONDEV_TOOLCHAIN)/config/makefile.inc
CFLAGS += -Wall -Wextra -Werror -Isrc
obj/main.o: src/main.c src/pinwalk_wire.h src/build_identity.h
obj/pinwalk_wire.o: src/pinwalk_wire.asm
