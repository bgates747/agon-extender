// Ordinary ExCom UART console plus native USB input and retained browser video.
#define AGON_EXTENDER_CONSOLE 1
#define AGON_EXTENDER_PROCESSED_KEYBOARD 1
#include "../../../.pio/build-identities/p4-console/build_identity.hpp"
#define AGON_EXTENDER_BUILD_IDENTITY_HEADER \
 "../../../.pio/build-identities/p4-console/build_identity.hpp"
#include "p4_browser_vdp.cpp"
#include "../transport/console_hardware.inc"
