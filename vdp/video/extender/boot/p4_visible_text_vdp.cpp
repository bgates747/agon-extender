// PORT-014: bounded UART text using retained renderer and browser service.
#define AGON_EXTENDER_VISIBLE_TEXT_QUALIFICATION 1
// Literal include is required for incremental build dependency tracking.
#include "../../../.pio/build-identities/p4-visible-text/build_identity.hpp"
#define AGON_EXTENDER_BUILD_IDENTITY_HEADER \
 "../../../.pio/build-identities/p4-visible-text/build_identity.hpp"
#include "p4_browser_vdp.cpp"
#include "../diagnostic/visible_text_hardware.inc"
