// PORT-008-D002 fixed-backend composition.
//
// This top level is intentionally non-release and compile/link-only.  It
// supplies an already-authorized live epoch solely to compose the production
// data plane with the retained parser/browser path.  It implements no product
// activation grammar and owns no UART return path.
#pragma once

#include <cstdint>

#include "extender/transport/extender_vdp_stream.hpp"

#ifndef AGON_EXTENDER_PORT008_NONRELEASE_QUALIFICATION
#error "p4_parallel_qualification.hpp is forbidden outside its non-release target"
#endif

#ifdef AGON_EXTENDER_PORT008_FORWARD
#error "production qualification and the r01 prototype may not coexist"
#endif

namespace agon::extender::transport {

struct P4QualificationCaptureMetrics {
  std::uint32_t write_calls{};
  std::uint32_t bytes_captured{};
  std::uint32_t capture_failures{};
  std::uint32_t flush_calls{};
  std::uint32_t duplex_rejections{};
  TransportFault fault{TransportFault::kNone};
};

// Returns a heap-owned Stream.  VDUStreamProcessor's raw-pointer constructor
// immediately adopts that pointer into shared ownership; callers must neither
// retain ownership nor delete it separately.
ExtenderVdpStream *beginP4ParallelNonreleaseQualification() noexcept;
void requestP4ParallelNonreleaseQualificationStop() noexcept;
P4QualificationCaptureMetrics p4QualificationCaptureMetrics() noexcept;
void logP4QualificationStatus() noexcept;
void setP4QualificationProtocolDuplex(bool full_duplex) noexcept;

}  // namespace agon::extender::transport

// Retained vdp_variables.h calls this official hook by unqualified name.  The
// hook must reach the actual composite Stream; a no-op would falsely claim a
// UART duplex transition that this composition deliberately does not own.
inline void setVDPProtocolDuplex(bool full_duplex) noexcept {
  agon::extender::transport::setP4QualificationProtocolDuplex(full_duplex);
}
