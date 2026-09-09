// USB -> retained processed-key/serializer -> UART1 -> ordinary EMOS CLI.
// Mainboard VDP supplies display and clock; browser service stays disabled.
#define AGON_EXTENDER_USB_CLI 1
#define AGON_EXTENDER_KEYBOARD_QUALIFICATION 1
#define AGON_EXTENDER_PROCESSED_KEYBOARD 1
#include "../../../.pio/build-identities/p4-usb-cli/build_identity.hpp"
#define AGON_EXTENDER_BUILD_IDENTITY_HEADER \
 "../../../.pio/build-identities/p4-usb-cli/build_identity.hpp"
#include "p4_browser_vdp.cpp"
#include "../diagnostic/usb_cli_hardware.inc"
