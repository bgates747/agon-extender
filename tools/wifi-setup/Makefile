# Build with an explicit maintained AgonDev toolchain, no emulator or install.
NAME=wifi-setup
LDHAS_ARG_PROCESSING=0
LDHAS_EXIT_HANDLER=0
CFLAGS_EXTRA=-Wall -Wextra -Werror
include $(AGONDEV_TOOLCHAIN)/config/makefile.inc
CFLAGS+=$(CFLAGS_EXTRA) -Iinclude
ifneq ($(WIFI_BUILD_ID),)
CFLAGS+=-DWIFI_BUILD_ID='"$(WIFI_BUILD_ID)"'
endif

# Recompile this small utility on each explicit build so a new build identity
# cannot silently reuse objects bearing a previous WIFI_BUILD_ID. Avoid make -B:
# the retained SDK's directory rule uses plain mkdir on an existing bin folder.
.PHONY: wifi_force
wifi_force:
$(OBJS): wifi_force
