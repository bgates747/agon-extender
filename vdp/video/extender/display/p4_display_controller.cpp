// See p4_display_controller.hpp.
//
// Generic wrappers and depth seams are adapted from the immutable vdp-gl
// all-the-plots spans fingerprinted by PORT-003 Phase B. This implementation
// uses the project bounds-safe codec; no classic VGA controller is compiled.
#include "extender/display/p4_display_controller.hpp"
#include "extender/diagnostics/frame_timing.hpp"

#include <climits>
#include <cstdlib>
#include <limits>

#if defined(ESP_PLATFORM)
#include "esp_heap_caps.h"
#include "esp_log.h"
#endif

namespace agon::extender::display {
namespace {

[[noreturn]] void unavailable(char const *operation) {
#if defined(ESP_PLATFORM)
  ESP_EARLY_LOGE("p4-display-renderer", "deferred operation invoked: %s",
                 operation);
#else
  (void)operation;
#endif
  std::abort();
}

void *allocateDisplay(void *, std::size_t size) {
#if defined(ESP_PLATFORM)
  void *result = heap_caps_malloc(size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
  return result != nullptr ? result : heap_caps_malloc(size, MALLOC_CAP_8BIT);
#else
  return std::malloc(size);
#endif
}

void *allocateSnapshot(void *, std::size_t size) {
#if defined(ESP_PLATFORM)
  // Phase F requires all three maximum-size immutable slots in PSRAM. Unlike
  // logical display storage, this optional service must not consume internal
  // RAM as a fallback when PSRAM capacity is unavailable.
  return heap_caps_malloc(size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
#else
  return std::malloc(size);
#endif
}

void deallocateDisplay(void *, void *allocation) {
#if defined(ESP_PLATFORM)
  heap_caps_free(allocation);
#else
  std::free(allocation);
#endif
}

}  // namespace

FrameCounterRegister::operator std::uint32_t() const noexcept {
  return value_.load(std::memory_order_acquire);
}

FrameCounterRegister &FrameCounterRegister::operator=(
    std::uint32_t value) noexcept {
  value_.store(value, std::memory_order_release);
  return *this;
}

std::uint32_t FrameCounterRegister::advance(
    std::uint32_t elapsed_ticks) noexcept {
  return value_.fetch_add(elapsed_ticks, std::memory_order_acq_rel) +
         elapsed_ticks;
}

Allocator defaultDisplayAllocator() noexcept {
  return {nullptr, allocateDisplay, deallocateDisplay};
}

Allocator defaultSnapshotAllocator() noexcept {
  return {nullptr, allocateSnapshot, deallocateDisplay};
}

P4DisplayController::P4DisplayController(
    Allocator allocator, Allocator snapshot_allocator) noexcept
    : storage_(allocator), palettes_(allocator), snapshots_(snapshot_allocator, SnapshotPixelFormat::RGB222, 0, true) {}

ConfigureResult P4DisplayController::configure(ModeDescriptor const &mode) noexcept {
  if (frame_service_running_.load(std::memory_order_acquire)) {
    return ConfigureResult::ServiceRunning;
  }
  if (mode.width > INT_MAX || mode.height > INT_MAX) {
    return ConfigureResult::InvalidDimensions;
  }
  ConfigureResult result = storage_.configure(mode);
  if (result != ConfigureResult::Ok) return result;
  palettes_.reset(mode.format);
  setScreenSize(static_cast<int>(mode.width), static_cast<int>(mode.height));
  m_viewPortWidth = static_cast<int>(mode.width);
  m_viewPortHeight = static_cast<int>(mode.height);
  setDoubleBuffered(mode.double_buffered);
  resetPaintState();
  enableBackgroundPrimitiveExecution(false);
  return ConfigureResult::Ok;
}

ConstPlaneView P4DisplayController::drawingPlane() const noexcept {
  return storage_.drawingPlane();
}
ConstPlaneView P4DisplayController::visiblePlane() const noexcept {
  return storage_.visiblePlane();
}

std::uint8_t P4DisplayController::drawingPlaneIdentity() const noexcept {
  return storage_.drawingPlaneIdentity();
}

std::uint8_t P4DisplayController::visiblePlaneIdentity() const noexcept {
  return storage_.visiblePlaneIdentity();
}

void P4DisplayController::begin() {
  if (!storage_.configured() &&
      configure({1, 1, NativePixelFormat::SBGR2222, false, 0xC0}) !=
          ConfigureResult::Ok) {
    unavailable("begin allocation");
  }
}

void P4DisplayController::setResolution(char const *modeline, int width,
                                        int height, bool double_buffered) {
  if (modeline != nullptr || width <= 0 || height <= 0) {
    unavailable("modeline-based setResolution (Phase E)");
  }
  NativePixelFormat format = storage_.configured()
                                 ? storage_.mode().format
                                 : NativePixelFormat::SBGR2222;
  std::uint8_t sync = storage_.configured()
                          ? storage_.mode().native_save_sync_bits
                          : 0xC0;
  if (configure({static_cast<std::size_t>(width), static_cast<std::size_t>(height),
                 format, double_buffered, sync}) != ConfigureResult::Ok) {
    unavailable("setResolution allocation");
  }
}

int P4DisplayController::colorsCount() {
  if (!storage_.configured()) return 0;
  std::uint8_t maximum = 0;
  return NativePixelCodec::maximumValue(storage_.mode().format, maximum) ==
                 CodecResult::Ok
             ? maximum + 1
             : 0;
}

fabgl::NativePixelFormat P4DisplayController::nativePixelFormat() {
  if (!storage_.configured()) return fabgl::NativePixelFormat::SBGR2222;
  switch (storage_.mode().format) {
    case NativePixelFormat::PALETTE2: return fabgl::NativePixelFormat::PALETTE2;
    case NativePixelFormat::PALETTE4: return fabgl::NativePixelFormat::PALETTE4;
    case NativePixelFormat::PALETTE8: return fabgl::NativePixelFormat::PALETTE8;
    case NativePixelFormat::PALETTE16: return fabgl::NativePixelFormat::PALETTE16;
    case NativePixelFormat::SBGR2222: return fabgl::NativePixelFormat::SBGR2222;
  }
  return fabgl::NativePixelFormat::SBGR2222;
}

void P4DisplayController::setFrameServiceRunning(bool running) noexcept {
  if (!running) {
    // The P4 adapter joins its sole service task first. Use the unchanged
    // upstream transition to drain work and return to synchronous execution;
    // this intentionally retains upstream Refresh and payload behavior.
    enableBackgroundPrimitiveExecution(false);
  }
  frame_service_running_.store(running, std::memory_order_release);
}

void P4DisplayController::setLogicalFramePeriodMicroseconds(
    std::uint64_t period_microseconds) noexcept {
  logical_frame_period_us_ = period_microseconds;
}

std::size_t P4DisplayController::executeFrameWork() {
  if (suspension_depth_.load(std::memory_order_acquire) != 0) {
    return 0;
  }
  executing_frame_work_.store(true, std::memory_order_release);
  fabgl::Rect update(SHRT_MAX, SHRT_MAX, SHRT_MIN, SHRT_MIN);
  std::size_t executed = 0;
  fabgl::Primitive primitive;
  // PORT-003-D013: match stock vdp-gl all-the-plots (ac2dd598) VGA worker
  // with its timeout disabled. Drain until empty or suspended; the previous
  // 64-per-frame cap throttled UART admission (AUDIT-005 W8). Keep the common
  // executor, snapshot boundary and immediate-completion path unchanged.
  {
    diagnostics::Scope timing(diagnostics::Phase::Queue);
    while (getPrimitive(&primitive, 0)) {
      execPrimitive(primitive, update, false);
      ++executed;
      if (suspension_depth_.load(std::memory_order_acquire) != 0) break;
    }
    timing.units(static_cast<std::uint32_t>(executed));
  }
  {
    diagnostics::Scope timing(diagnostics::Phase::Sprites);
    showSprites(update);
  }
  publishSnapshotAtBoundary();
  executing_frame_work_.store(false, std::memory_order_release);
  return executed;
}

std::uint32_t P4DisplayController::readFrameCounter() const noexcept {
  return frameCounter;
}

void P4DisplayController::writeFrameCounter(std::uint32_t value) noexcept {
  frameCounter = value;
}

std::uint32_t P4DisplayController::advanceFrameCounter(
    std::uint32_t elapsed_ticks) noexcept {
  return frameCounter.advance(elapsed_ticks);
}

std::size_t P4DisplayController::logicalWidth() const noexcept {
  return storage_.configured() ? storage_.mode().width : 0;
}

std::size_t P4DisplayController::logicalHeight() const noexcept {
  return storage_.configured() ? storage_.mode().height : 0;
}

NativePixelFormat P4DisplayController::logicalFormat() const noexcept {
  return storage_.configured() ? storage_.mode().format
                               : NativePixelFormat::SBGR2222;
}

bool P4DisplayController::logicalDoubleBuffered() const noexcept {
  return storage_.configured() && storage_.mode().double_buffered;
}

bool P4DisplayController::createPalette(std::uint16_t palette_id) noexcept {
  return palettes_.createPalette(palette_id);
}

void P4DisplayController::deletePalette(std::uint16_t palette_id) noexcept {
  palettes_.deletePalette(palette_id);
}

bool P4DisplayController::setItemInPalette(
    std::uint16_t palette_id, std::uint8_t index, std::uint8_t red,
    std::uint8_t green, std::uint8_t blue) noexcept {
  return palettes_.setItemInPalette(palette_id, index, red, green, blue);
}

void P4DisplayController::updateRGB2PaletteLUT() noexcept {
  palettes_.updateRGB2PaletteLUT();
}

bool P4DisplayController::updateSignalList(std::uint16_t const *raw_pairs,
                                           std::size_t entries) noexcept {
  return palettes_.updateSignalList(raw_pairs, entries);
}

bool P4DisplayController::setDisplayCursorPosition(int x, int y) noexcept {
  if (mouseCursor() == nullptr) return false;
  setMouseCursorPos(x, y);
  return true;
}

void P4DisplayController::suspendBackgroundPrimitiveExecution() {
  const auto previous_depth = suspension_depth_.fetch_add(1, std::memory_order_acq_rel);
  diagnostics::Scope timing(diagnostics::Phase::Suspend, previous_depth + 1);
  while (executing_frame_work_.load(std::memory_order_acquire)) taskYIELD();
}

void P4DisplayController::resumeBackgroundPrimitiveExecution() {
  std::uint32_t depth = suspension_depth_.load(std::memory_order_acquire);
  while (depth != 0 &&
         !suspension_depth_.compare_exchange_weak(
             depth, depth - 1, std::memory_order_acq_rel,
             std::memory_order_acquire)) {
  }
}

void P4DisplayController::swapBuffers() {
  if (!storage_.swapPlanes()) unavailable("swapBuffers without double buffering");
}

std::uint8_t *P4DisplayController::row(int y) noexcept {
  PlaneView plane = storage_.drawingPlane();
  return plane.data + static_cast<std::size_t>(y) * plane.stride;
}
std::uint8_t const *P4DisplayController::row(int y) const noexcept {
  ConstPlaneView plane = storage_.drawingPlane();
  return plane.data + static_cast<std::size_t>(y) * plane.stride;
}

std::uint8_t P4DisplayController::readLogical(std::uint8_t const *source,
                                              int x) const noexcept {
  std::uint8_t result = 0;
  if (NativePixelCodec::read(source, storage_.mode().width, storage_.mode().format,
                             static_cast<std::size_t>(x), result) != CodecResult::Ok)
    std::abort();
  return result;
}

void P4DisplayController::writeLogical(std::uint8_t *destination, int x,
                                       std::uint8_t value) noexcept {
  if (NativePixelCodec::write(destination, storage_.mode().width,
                              storage_.mode().format,
                              static_cast<std::size_t>(x), value) !=
      CodecResult::Ok)
    std::abort();
}

std::uint8_t P4DisplayController::colorToLogical(
    fabgl::RGB888 const &color) const noexcept {
  return palettes_.drawingIndex(color.R, color.G, color.B);
}

fabgl::RGB888 P4DisplayController::logicalToColor(std::uint8_t value) const noexcept {
  std::uint8_t packed = palettes_.palette0Color(value);
  return fabgl::RGB888((packed & 3) * 85, ((packed >> 2) & 3) * 85,
                       ((packed >> 4) & 3) * 85);
}

void P4DisplayController::writePainted(std::uint8_t *destination, int x,
                                       std::uint8_t value,
                                       fabgl::PaintMode mode) noexcept {
  std::uint8_t maximum = 0;
  NativePixelCodec::maximumValue(storage_.mode().format, maximum);
  std::uint8_t old = readLogical(destination, x), result = old;
  switch (mode) {
    case fabgl::PaintMode::Set: result = value; break;
    case fabgl::PaintMode::OR: result = old | value; break;
    case fabgl::PaintMode::ORNOT: result = old | (~value & maximum); break;
    case fabgl::PaintMode::AND: result = old & value; break;
    case fabgl::PaintMode::ANDNOT: result = old & (~value & maximum); break;
    case fabgl::PaintMode::XOR: result = old ^ value; break;
    case fabgl::PaintMode::Invert: result = old ^ maximum; break;
    case fabgl::PaintMode::NoOp: return;
  }
  writeLogical(destination, x, result & maximum);
}

P4DisplayController::PixelWriter P4DisplayController::pixelWriter(
    fabgl::PaintMode mode) {
  return [this, mode](int x, int y, std::uint8_t value) {
    writePainted(row(y), x, value, mode);
  };
}
P4DisplayController::RowPixelWriter P4DisplayController::rowPixelWriter(
    fabgl::PaintMode mode) {
  return [this, mode](std::uint8_t *target, int x, std::uint8_t value) {
    writePainted(target, x, value, mode);
  };
}
P4DisplayController::RowFiller P4DisplayController::rowFiller(
    fabgl::PaintMode mode) {
  return [this, mode](int y, int x1, int x2, std::uint8_t value) {
    auto *target = row(y);
    for (int x = x1; x <= x2; ++x) writePainted(target, x, value, mode);
  };
}

void P4DisplayController::rawFillRow(int y, int x1, int x2,
                                     std::uint8_t value) noexcept {
  auto *target = row(y);
  for (int x = x1; x <= x2; ++x) writeLogical(target, x, value);
}
void P4DisplayController::rawCopyRow(int x1, int x2, int source_y,
                                     int destination_y) noexcept {
  auto const *source = row(source_y);
  auto *destination = row(destination_y);
  for (int x = x1; x <= x2; ++x)
    writeLogical(destination, x, readLogical(source, x));
}

void P4DisplayController::setPixelAt(fabgl::PixelDesc const &pixel,
                                     fabgl::Rect &update) {
  auto mode = paintState().paintOptions.mode;
  genericSetPixelAt(pixel, update,
                    [this](fabgl::RGB888 const &color) { return colorToLogical(color); },
                    pixelWriter(mode));
}

void P4DisplayController::absDrawLine(int x1, int y1, int x2, int y2,
                                      fabgl::RGB888 color) {
  auto mode = paintState().paintOptions.NOT ? fabgl::PaintMode::NOT
                                             : paintState().paintOptions.mode;
  genericAbsDrawLine(x1, y1, x2, y2, color,
                     [this](fabgl::RGB888 const &value) { return colorToLogical(value); },
                     rowFiller(mode), pixelWriter(mode));
}

void P4DisplayController::fillRow(int y, int x1, int x2, fabgl::RGB888 color) {
  auto mode = paintState().paintOptions.mode;
  rowFiller(mode)(y, x1, x2, colorToLogical(color));
}

void P4DisplayController::drawEllipse(fabgl::Size const &size,
                                      fabgl::Rect &update) {
  auto mode = paintState().paintOptions.mode;
  genericDrawEllipse(size, update,
                     [this](fabgl::RGB888 const &color) { return colorToLogical(color); },
                     pixelWriter(mode));
}

void P4DisplayController::absDrawEllipseSheared(
    fabgl::EllipseShearedParams const &params, fabgl::Rect &update) {
  auto mode = paintState().paintOptions.mode;
  genericDrawEllipseSheared(
      params, update,
      [this](fabgl::RGB888 const &color) { return colorToLogical(color); },
      pixelWriter(mode));
}

void P4DisplayController::drawArc(fabgl::Rect const &rect, fabgl::Rect &update) {
  auto mode = paintState().paintOptions.mode;
  genericDrawArc(rect, update,
                 [this](fabgl::RGB888 const &color) { return colorToLogical(color); },
                 pixelWriter(mode));
}

void P4DisplayController::fillSegment(fabgl::Rect const &rect,
                                      fabgl::Rect &update) {
  auto mode = paintState().paintOptions.mode;
  genericFillSegment(rect, update,
                     [this](fabgl::RGB888 const &color) { return colorToLogical(color); },
                     rowFiller(mode));
}

void P4DisplayController::fillSector(fabgl::Rect const &rect,
                                     fabgl::Rect &update) {
  auto mode = paintState().paintOptions.mode;
  genericFillSector(rect, update,
                    [this](fabgl::RGB888 const &color) { return colorToLogical(color); },
                    rowFiller(mode));
}

void P4DisplayController::clear(fabgl::Rect &update) {
  hideSprites(update);
  PlaneView plane = storage_.drawingPlane();
  if (NativePixelCodec::clear(plane.data, storage_.mode().width,
                              storage_.mode().height, storage_.mode().format,
                              colorToLogical(getActualBrushColor())) !=
      CodecResult::Ok)
    std::abort();
}

void P4DisplayController::VScroll(int scroll, fabgl::Rect &update) {
  genericVScroll(scroll, update,
                 [this](int x1, int x2, int source_y, int destination_y) {
                   rawCopyRow(x1, x2, source_y, destination_y);
                 },
                 [this](int y, int x1, int x2, fabgl::RGB888 color) {
                   rawFillRow(y, x1, x2, colorToLogical(color));
                 });
}

void P4DisplayController::HScroll(int scroll, fabgl::Rect &update) {
  genericHScroll(
      scroll, update,
      [this](fabgl::RGB888 const &color) { return colorToLogical(color); },
      [this](int y) { return row(y); },
      [this](std::uint8_t *source, int x) { return readLogical(source, x); },
      [this](std::uint8_t *destination, int x, std::uint8_t value) {
        writeLogical(destination, x, value);
      });
}

void P4DisplayController::drawGlyph(fabgl::Glyph const &glyph,
                                    fabgl::GlyphOptions options,
                                    fabgl::RGB888 pen, fabgl::RGB888 brush,
                                    fabgl::Rect &update) {
  auto mode = paintState().paintOptions.mode;
  genericDrawGlyph(
      glyph, options, pen, brush, update,
      [this](fabgl::RGB888 const &color) { return colorToLogical(color); },
      [this](int y) { return row(y); }, rowPixelWriter(mode));
}

void P4DisplayController::invertRect(fabgl::Rect const &rect,
                                     fabgl::Rect &update) {
  genericInvertRect(rect, update, [this](int y, int x1, int x2) {
    rowFiller(fabgl::PaintMode::Invert)(y, x1, x2, 0);
  });
}

void P4DisplayController::swapFGBG(fabgl::Rect const &rect,
                                   fabgl::Rect &update) {
  genericSwapFGBG(
      rect, update,
      [this](fabgl::RGB888 const &color) { return colorToLogical(color); },
      [this](int y) { return row(y); },
      [this](std::uint8_t *source, int x) { return readLogical(source, x); },
      [this](std::uint8_t *destination, int x, std::uint8_t value) {
        writeLogical(destination, x, value);
      });
}

void P4DisplayController::copyRect(fabgl::Rect const &source,
                                   fabgl::Rect &update) {
  genericCopyRect(
      source, update, [this](int y) { return row(y); },
      [this](std::uint8_t *source_row, int x) { return readLogical(source_row, x); },
      [this](std::uint8_t *destination, int x, std::uint8_t value) {
        writeLogical(destination, x, value);
      });
}

void P4DisplayController::readScreen(fabgl::Rect const &rect,
                                     fabgl::RGB888 *destination) {
  for (int y = rect.Y1; y <= rect.Y2; ++y) {
    auto const *source = row(y);
    for (int x = rect.X1; x <= rect.X2; ++x, ++destination)
      *destination = logicalToColor(readLogical(source, x));
  }
}

CompositionResult P4DisplayController::composeSprite(
    fabgl::Sprite *sprite, PresentationRegion const &region,
    PresentationRGB888 *destination,
    std::size_t destination_pixels) noexcept {
  if (sprite == nullptr) return CompositionResult::Ok;
  fabgl::Bitmap const *bitmap = sprite->getFrame();
  if (bitmap == nullptr) return CompositionResult::Ok;
  if (bitmap->width <= 0 || bitmap->height <= 0 || bitmap->data == nullptr)
    return CompositionResult::InvalidOverlay;

  OverlayPixelFormat format;
  std::size_t bytes_per_pixel = 0;
  switch (bitmap->format) {
    case fabgl::PixelFormat::RGBA2222:
      format = OverlayPixelFormat::RGBA2222;
      bytes_per_pixel = 1;
      break;
    case fabgl::PixelFormat::RGBA8888:
      format = OverlayPixelFormat::RGBA8888;
      bytes_per_pixel = 4;
      break;
    default:
      // Exact upstream physical-overlay behavior: unsupported hardware bitmap
      // formats are ignored rather than entering the software sprite path.
      return CompositionResult::Ok;
  }

  std::size_t width = static_cast<std::size_t>(bitmap->width);
  std::size_t height = static_cast<std::size_t>(bitmap->height);
  if (height > std::numeric_limits<std::size_t>::max() / width ||
      width * height >
          std::numeric_limits<std::size_t>::max() / bytes_per_pixel)
    return CompositionResult::SizeOverflow;
  OverlayView overlay{
      sprite->x,
      sprite->y,
      width,
      height,
      format,
      sprite->paintOptions.mode == fabgl::PaintMode::XOR
          ? OverlayPaint::Xor
          : OverlayPaint::Overwrite,
      bitmap->data,
      width * height * bytes_per_pixel,
  };
  return PresentationCompositor::applyOverlay(
      region, destination, destination_pixels, overlay);
}

CompositionResult P4DisplayController::composeVisibleRegionQuiescent(
    PresentationRegion const &region, PresentationRGB888 *destination,
    std::size_t destination_pixels) noexcept {
  if (!storage_.configured()) return CompositionResult::InvalidMode;
  // Phase D deliberately permits this borrowed-state seam only while logical
  // execution is stopped or explicitly suspended by its caller. This check is
  // a misuse detector, not the future frame-consumer lifetime contract: the
  // caller must retain its suspension and own all overlay mutation until this
  // synchronous call returns.
  if (executing_frame_work_.load(std::memory_order_acquire) ||
      (frame_service_running_.load(std::memory_order_acquire) &&
       suspension_depth_.load(std::memory_order_acquire) == 0))
    return CompositionResult::NotQuiescent;
  return composeVisibleRegionAtBoundary(region, destination,
                                        destination_pixels);
}

CompositionResult P4DisplayController::composeVisibleRegionAtBoundary(
    PresentationRegion const &region, PresentationRGB888 *destination,
    std::size_t destination_pixels) noexcept {
  CompositionResult result = PresentationCompositor::composeBase(
      static_cast<PlaneStorage const &>(storage_).visiblePlane(),
      storage_.mode(), palettes_, region, destination, destination_pixels);
  if (result != CompositionResult::Ok) return result;

  fabgl::Sprite *text = textCursor();
  if (text != nullptr && text->visible) {
    result = composeSprite(text, region, destination, destination_pixels);
    if (result != CompositionResult::Ok) return result;
  }
  for (int index = 0; index < spritesCount(); ++index) {
    fabgl::Sprite *sprite = getSprite(index);
    if (sprite->hardware && sprite->visible && sprite->allowDraw) {
      result = composeSprite(sprite, region, destination, destination_pixels);
      if (result != CompositionResult::Ok) return result;
    }
  }
  fabgl::Sprite *mouse = mouseCursor();
  if (mouse != nullptr && mouse->visible)
    return composeSprite(mouse, region, destination, destination_pixels);
  return CompositionResult::Ok;
}

void P4DisplayController::publishSnapshotAtBoundary() noexcept {
  if (!snapshots_.enabled() || logical_frame_period_us_ == 0 ||
      !storage_.configured())
    return;
  snapshot_clock_us_ += logical_frame_period_us_;
  MutableSnapshotView destination{};
  std::size_t width = storage_.mode().width;
  std::size_t height = storage_.mode().height;
  if (snapshots_.tryBegin(width, height, snapshot_clock_us_, destination) !=
      SnapshotBeginResult::Ok)
    return;
  // Time actual composition only; an unrequested/skipped snapshot is no work.
  diagnostics::Scope timing(diagnostics::Phase::Snapshot,
                           static_cast<std::uint32_t>(width * height));
  PresentationRegion full{0, 0, width, height};
  CompositionResult result = composeVisibleRegionAtBoundary(
      full, destination.pixels, destination.pixel_capacity);
  snapshots_.finish(result, logical_frame_period_us_);
}

PresentationSnapshotPool &P4DisplayController::snapshotPool() noexcept {
  return snapshots_;
}

PresentationSnapshotPool const &P4DisplayController::snapshotPool() const
    noexcept {
  return snapshots_;
}

int P4DisplayController::getBitmapSavePixelSize() { return 1; }

std::uint8_t P4DisplayController::nativeSavePixel(std::uint8_t logical) const noexcept {
  if (storage_.mode().format == NativePixelFormat::SBGR2222)
    return static_cast<std::uint8_t>((logical & 0x3F) |
                                     storage_.mode().native_save_sync_bits);
  fabgl::RGB888 color = logicalToColor(logical);
  return static_cast<std::uint8_t>(storage_.mode().native_save_sync_bits |
                                   (color.R >> 6) | ((color.G >> 6) << 2) |
                                   ((color.B >> 6) << 4));
}

void P4DisplayController::rawDrawBitmap_Native(
    int dest_x, int dest_y, fabgl::Bitmap const *bitmap, int x1, int y1,
    int x_count, int y_count) {
  genericRawDrawBitmap_Native(
      dest_x, dest_y, bitmap->data, bitmap->width, x1, y1, x_count, y_count,
      [this](int y) { return row(y); },
      [this](std::uint8_t *destination, int x, std::uint8_t value) {
        writeLogical(destination, x, value);
      });
}

void P4DisplayController::rawDrawBitmap_Mask(
    int dest_x, int dest_y, fabgl::Bitmap const *bitmap, void *saved_background,
    int x1, int y1, int x_count, int y_count) {
  auto writer = rowPixelWriter(paintState().paintOptions.mode);
  std::uint8_t foreground = colorToLogical(
      paintState().paintOptions.swapFGBG ? paintState().penColor
                                         : bitmap->foregroundColor);
  genericRawDrawBitmap_Mask(
      dest_x, dest_y, bitmap, static_cast<std::uint8_t *>(saved_background), x1,
      y1, x_count, y_count, [this](int y) { return row(y); },
      [this](std::uint8_t *source, int x) { return readLogical(source, x); },
      [writer, foreground](std::uint8_t *destination, int x) {
        writer(destination, x, foreground);
      });
}

void P4DisplayController::rawDrawBitmap_RGBA2222(
    int dest_x, int dest_y, fabgl::Bitmap const *bitmap, void *saved_background,
    int x1, int y1, int x_count, int y_count) {
  auto writer = rowPixelWriter(paintState().paintOptions.mode);
  bool background = paintState().paintOptions.swapFGBG;
  std::uint8_t background_value = colorToLogical(paintState().penColor);
  genericRawDrawBitmap_RGBA2222(
      dest_x, dest_y, bitmap, static_cast<std::uint8_t *>(saved_background), x1,
      y1, x_count, y_count, [this](int y) { return row(y); },
      [this](std::uint8_t *source, int x) { return readLogical(source, x); },
      [this, writer, background, background_value](std::uint8_t *destination,
                                                    int x, std::uint8_t value) {
        auto rgb = fabgl::RGB888((value & 3) * 85, ((value >> 2) & 3) * 85,
                                 ((value >> 4) & 3) * 85);
        writer(destination, x,
               background ? background_value : colorToLogical(rgb));
      });
}

void P4DisplayController::rawDrawBitmap_RGBA8888(
    int dest_x, int dest_y, fabgl::Bitmap const *bitmap, void *saved_background,
    int x1, int y1, int x_count, int y_count) {
  auto writer = rowPixelWriter(paintState().paintOptions.mode);
  bool background = paintState().paintOptions.swapFGBG;
  std::uint8_t background_value = colorToLogical(paintState().penColor);
  genericRawDrawBitmap_RGBA8888(
      dest_x, dest_y, bitmap, static_cast<std::uint8_t *>(saved_background), x1,
      y1, x_count, y_count, [this](int y) { return row(y); },
      [this](std::uint8_t *source, int x) { return readLogical(source, x); },
      [this, writer, background, background_value](std::uint8_t *destination,
                                                    int x,
                                                    fabgl::RGBA8888 const &value) {
        writer(destination, x,
               background ? background_value
                          : colorToLogical(fabgl::RGB888(value.R, value.G, value.B)));
      });
}

void P4DisplayController::rawCopyToBitmap(int src_x, int src_y, int width,
                                          void *save_buffer, int x1, int y1,
                                          int x_count, int y_count) {
  genericRawCopyToBitmap(
      src_x, src_y, width, static_cast<std::uint8_t *>(save_buffer), x1, y1,
      x_count, y_count, [this](int y) { return row(y); },
      [this](std::uint8_t *source, int x) {
        return nativeSavePixel(readLogical(source, x));
      });
}

void P4DisplayController::rawDrawBitmapWithMatrix_Mask(
    int dest_x, int dest_y, fabgl::Rect &drawing_rect,
    fabgl::Bitmap const *bitmap, float const *inverse) {
  auto writer = rowPixelWriter(paintState().paintOptions.mode);
  std::uint8_t foreground = colorToLogical(
      paintState().paintOptions.swapFGBG ? paintState().penColor
                                         : bitmap->foregroundColor);
  genericRawDrawTransformedBitmap_Mask(
      dest_x, dest_y, drawing_rect, bitmap, inverse,
      [this](int y) { return row(y); },
      [writer, foreground](std::uint8_t *destination, int x) {
        writer(destination, x, foreground);
      });
}

void P4DisplayController::rawDrawBitmapWithMatrix_RGBA2222(
    int dest_x, int dest_y, fabgl::Rect &drawing_rect,
    fabgl::Bitmap const *bitmap, float const *inverse) {
  auto writer = rowPixelWriter(paintState().paintOptions.mode);
  bool background = paintState().paintOptions.swapFGBG;
  std::uint8_t background_value = colorToLogical(paintState().penColor);
  genericRawDrawTransformedBitmap_RGBA2222(
      dest_x, dest_y, drawing_rect, bitmap, inverse,
      [this](int y) { return row(y); },
      [this, writer, background, background_value](std::uint8_t *destination,
                                                    int x, std::uint8_t value) {
        auto rgb = fabgl::RGB888((value & 3) * 85, ((value >> 2) & 3) * 85,
                                 ((value >> 4) & 3) * 85);
        writer(destination, x,
               background ? background_value : colorToLogical(rgb));
      });
}

void P4DisplayController::rawDrawBitmapWithMatrix_RGBA8888(
    int dest_x, int dest_y, fabgl::Rect &drawing_rect,
    fabgl::Bitmap const *bitmap, float const *inverse) {
  auto writer = rowPixelWriter(paintState().paintOptions.mode);
  bool background = paintState().paintOptions.swapFGBG;
  std::uint8_t background_value = colorToLogical(paintState().penColor);
  genericRawDrawTransformedBitmap_RGBA8888(
      dest_x, dest_y, drawing_rect, bitmap, inverse,
      [this](int y) { return row(y); },
      [this, writer, background, background_value](std::uint8_t *destination,
                                                    int x,
                                                    fabgl::RGBA8888 const &value) {
        writer(destination, x,
               background ? background_value
                          : colorToLogical(fabgl::RGB888(value.R, value.G, value.B)));
      });
}

std::unique_ptr<fabgl::BitmappedDisplayController> makeP4DisplayController() {
  return std::make_unique<P4DisplayController>(defaultDisplayAllocator());
}

}  // namespace agon::extender::display
