#pragma once
#include "adapter.hpp"
namespace agon::extender::webdav {
// A dedicated transfer worker owns this stream. Implementations must bound each
// read/write with a socket deadline and close on errors. Never supply the
// existing video HTTP connection or bypass its private parser buffer. No
// listen/start API is provided here; composition must first install the
// admission/media owners.
struct Stream : Input {
  virtual int send(const void *, size_t) = 0;
  virtual void close() = 0;
};
// One request, then close. Header read-ahead is retained for Body. The raw
// chunked path therefore works without patching esp_http_server's session recv
// callback.
void serveConnection(Adapter &, Stream &);
} // namespace agon::extender::webdav
