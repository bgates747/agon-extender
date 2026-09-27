#pragma once
#include "../spool/store.hpp"
#include "adapter.hpp"
namespace agon::extender::webdav {
inline int spoolStatus(spool::Result r) {
  using R = spool::Result;
  switch (r) {
  case R::ok:
    return 200;
  case R::busy:
  case R::unavailable:
  case R::stale:
    return 503;
  case R::quota:
  case R::full:
    return 507;
  case R::invalid:
    return 400;
  default:
    return 500;
  }
}
// Backend::put implementation building block. The caller already owns exact
// EMOS READY and supplies its upload descriptor/binding; this function never
// fabricates admission or opens UART. Transfer must verify the remote stage;
// Activate must return 200 ONLY for a matching confirmed activation response.
// Return of 200 from seal or a local filesystem write is not that response.
// Store's single slot is reserved against local-card HTTP access by
// composition.
template <class IO, class Transfer, class Activate>
Outcome stagedPut(spool::Store<IO> &store, const spool::Job &job, Body &body,
                  Transfer transfer, Activate activate) {
  int status = spoolStatus(store.begin(job));
  if (status != 200)
    return {status, 0, {}};
  std::array<std::uint8_t, 4096> buffer{};
  std::uint32_t offset = 0;
  int n;
  while ((n = body.read(buffer.data(), buffer.size())) > 0) {
    status = spoolStatus(store.append(job.binding, offset, buffer.data(), n));
    if (status != 200) {
      store.invalidate();
      return {status, 0, {}};
    }
    offset += n;
  }
  if (n < 0 || !body.finished() || offset != job.size) {
    // No remote transaction has started; explicit abandonment is safe. A
    // failed cleanup retains evidence and blocks the next begin().
    store.discard(job.binding);
    store.invalidate();
    return {400, 0, {}};
  }
  status = spoolStatus(store.seal(job.binding));
  if (status != 200) {
    store.invalidate();
    return {status, 0, {}};
  }
  status = transfer(store, job);
  if (status != 200) {
    store.invalidate();
    return {status, 0, {}};
  }
  status = spoolStatus(store.activationStarted(job.binding));
  if (status != 200) {
    store.invalidate();
    return {status, 0, {}};
  }
  // Marker precedes remote activation. No further payload reads are needed;
  // transfer already verified the remote stage while the snapshot was sealed.
  status = activate(job);
  if (status != 200) {
    store.invalidate();
    return {status, 0, {}};
  }
  status = spoolStatus(store.confirmed(job.binding));
  if (status == 200)
    status = spoolStatus(store.discard(job.binding));
  store.invalidate();
  return {status, status == 200 ? 1U : 0U, {}};
}
} // namespace agon::extender::webdav
