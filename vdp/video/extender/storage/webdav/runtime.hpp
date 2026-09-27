#pragma once
#ifndef AGON_EXTENDER_STAGED_WEBDAV
#define AGON_EXTENDER_STAGED_WEBDAV 0
#endif
namespace agon::extender::webdav {
// No device endpoint in ordinary builds until paired qualification.
bool startRuntime() noexcept;
}
