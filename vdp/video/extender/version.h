// SETUP-001 canary identity boundary.
//
// This file exists so temporary bring-up firmware follows the same rule as
// future production firmware: source identity is tracked, while a unique build
// ID is injected by the build invocation. It will be replaced by the permanent
// generated-identity interface when the official VDP source is imported.
#pragma once

#define AGON_EXTENDER_SOURCE_ID "setup-001-canary-r03"

#if defined(AGON_EXTENDER_QUALIFICATION_BUILD) && \
    !defined(AGON_EXTENDER_BUILD_ID)
#error "Qualification builds require AGON_EXTENDER_BUILD_ID"
#endif

// Ordinary developer builds remain convenient but identify themselves as
// unsuitable for qualification. A qualified build must override this macro
// with its UTC timestamped ID and define AGON_EXTENDER_QUALIFICATION_BUILD.
#ifndef AGON_EXTENDER_BUILD_ID
#define AGON_EXTENDER_BUILD_ID \
  AGON_EXTENDER_SOURCE_ID "-unidentified-experimental-build"
#endif
