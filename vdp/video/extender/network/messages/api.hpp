// Console-facing fixed mailboxes. Socket operations belong exclusively to worker.
#pragma once
#include "wire.h"
namespace agon::extender::network::messages {
bool submit(const uint8_t*,unsigned) noexcept;
unsigned take(uint8_t*) noexcept;
}
