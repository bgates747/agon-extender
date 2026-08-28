#pragma once

#include <array>
#include <cstddef>
#include <cstdint>

namespace agon::extender::web {

struct EmbeddedAsset {
  char const *route;
  char const *media_type;
  std::uint8_t const *data;
  std::size_t size;
};

std::array<EmbeddedAsset, 5> const &embeddedBrowserAssets() noexcept;

}  // namespace agon::extender::web
