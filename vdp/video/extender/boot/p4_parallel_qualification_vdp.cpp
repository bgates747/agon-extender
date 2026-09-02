// PORT-008 qualification-only retained-sketch compilation bridge.
//
// This exceptional translation unit supplies the non-release composition
// definition only while compiling the retained sketch.  It includes the
// ordinary P4 sketch bridge instead of duplicating its Arduino-generated
// declarations.  Source selection must compile this wrapper or the ordinary
// bridge, never both.

#define AGON_EXTENDER_PORT008_NONRELEASE_QUALIFICATION 1
#define AGON_EXTENDER_BUILD_IDENTITY_HEADER \
  "../../../.pio/build-identities/p4-port008-nonrelease-qualification/build_identity.hpp"

#include "p4_browser_vdp.cpp"
