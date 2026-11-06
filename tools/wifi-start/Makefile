# Separate application; reuse only Extender-owned support, never edit upstream.
NAME=wifi-start
LDHAS_ARG_PROCESSING=0
LDHAS_EXIT_HANDLER=0
include $(AGONDEV_TOOLCHAIN)/config/makefile.inc
CFLAGS+=-Wall -Wextra -Werror -I../wifi-setup/include
ifneq ($(WIFI_BUILD_ID),)
CFLAGS+=-DWIFI_BUILD_ID='"$(WIFI_BUILD_ID)"'
endif
OBJS+=obj/shared_config.o obj/shared_setup.o obj/shared_uart.o
obj/shared_config.o: ../wifi-setup/src/config.c
	@mkdir -p obj
	$(CC) $(CFLAGS) $< -c -o $@
obj/shared_setup.o: ../wifi-setup/src/setup.c
	@mkdir -p obj
	$(CC) $(CFLAGS) $< -c -o $@
obj/shared_uart.o: ../wifi-setup/src/uart.src
	@mkdir -p obj
	$(ASM) $(ASMFLAGS) $< -o $@
.PHONY: wifi_force
wifi_force:
$(OBJS): wifi_force
# SDK expands prerequisite lists while reading its include, before our extra
# objects exist. Add these prerequisites explicitly after extending OBJS.
$(LINKBINARY): $(OBJS)
