// PORT-013 bounded General Poll composition over the retained EDP parser.
// Boot-TU-only selection: ordinary EDP remains disconnected pending activation.
#define AGON_EXTENDER_GENERAL_POLL_QUALIFICATION 1
// Keep a literal include visible to PlatformIO's dependency scanner. The
// macro-only include in the shared bridge did not invalidate this object when
// the generated identity changed, leaving the draft identity in a candidate.
#include "../../../.pio/build-identities/p4-general-poll/build_identity.hpp"
#define AGON_EXTENDER_BUILD_IDENTITY_HEADER \
 "../../../.pio/build-identities/p4-general-poll/build_identity.hpp"
#include "p4_browser_vdp.cpp"
#include "../diagnostic/general_poll_hardware.inc"
