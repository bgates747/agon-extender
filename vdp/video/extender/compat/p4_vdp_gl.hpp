// PORT-003 narrow retained-vdp vdp-gl include surface for ESP32-P4.
//
// Upstream video headers use the all-in-one fabgl.h for common geometry,
// canvas, bitmap, sprite, font, key-value, and utility types. That umbrella
// also imports classic VGA/CVBS, PS/2, Terminal, Scene, and SoundGenerator
// headers whose hardware bindings are explicitly outside the P4 closure. This
// target-only header preserves the common declarations and upstream global
// aliases without importing those physical subsystems.
#pragma once

#include <canvas.h>
#include <codepages.h>
#include <fabfonts.h>

namespace fabgl {

// MouseDelta normally arrives through the physical mouse driver header. The
// retained processor uses only its value shape at the PORT-005 seam, whose
// Gate-F implementation produces no events.
struct MouseDelta {
  std::int16_t deltaX{};
  std::int16_t deltaY{};
  std::int8_t deltaZ{};
  MouseButtons buttons{};
  std::uint8_t overflowX : 1 {};
  std::uint8_t overflowY : 1 {};
};

}  // namespace fabgl

using fabgl::Bitmap;
using fabgl::Canvas;
using fabgl::CoreUsage;
using fabgl::CursorName;
using fabgl::GlyphOptions;
using fabgl::MouseDelta;
using fabgl::MouseStatus;
using fabgl::PixelFormat;
using fabgl::Point;
using fabgl::Rect;
using fabgl::RGB222;
using fabgl::RGB888;
using fabgl::RGBA2222;
using fabgl::RGBA8888;
using fabgl::Size;
using fabgl::Sprite;
using fabgl::VirtualKey;
using fabgl::VirtualKeyItem;
