#pragma once
namespace agon::extender::local_sd {
// P4-PC Rev C: power GPIO46's shared SD I/O bank before console pad setup.
// No card mount; retain fixed 3.3V for the boot lifetime, including SD failure.
bool beginSharedIoSupply() noexcept;
// Dedicated server, one task, independent of mainboard SD and video sessions.
bool startHttp() noexcept;
}
