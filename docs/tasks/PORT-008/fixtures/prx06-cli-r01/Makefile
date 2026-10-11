NAME = prxcli
AGONDEV_TOOLCHAIN ?= $(shell agondev-config --prefix)
include $(AGONDEV_TOOLCHAIN)/config/makefile.inc
CFLAGS += -Wall -Wextra -Werror -Isrc -Icommon
OBJS += obj/p4_canary.o
$(LINKBINARY): obj/p4_canary.o
obj/main.o: src/main.c src/prx06_wire.h common/p4_canary.h
obj/prx06_wire.o: src/prx06_wire.asm
obj/p4_canary.o: common/p4_canary.c common/p4_canary.h
	@echo [compiling $<]
	@mkdir -p $(dir $@)
	$(V)$(CC) $(CFLAGS) $< -c -o $@
.PHONY: inspect
inspect: $(BINARY)
	$(AGONDEV_TOOLCHAIN)/bin/ez80-none-elf-objdump -d obj/prx06_wire.o
