NAME = pariso
RAM_START = 0xB0000
RAM_SIZE = 0x8000
include $(AGONDEV_TOOLCHAIN)/config/makefile.inc
CFLAGS += -Wall -Wextra -Werror
$(LINKBINARY): $(OBJDIR)/emos_gateway.o
$(OBJDIR)/emos_gateway.o: src/emos_gateway.asm
	@mkdir -p $(dir $@)
	$(ASM) $(ASMFLAGS) $< -o $@
