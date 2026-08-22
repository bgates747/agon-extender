// See p4_display_controller.hpp.
//
// Generic wrappers and depth seams are adapted from the immutable vdp-gl
// all-the-plots spans fingerprinted by PORT-003 Phase B. This implementation
// uses the project bounds-safe codec; no classic VGA controller is compiled.
#include "extender/display/p4_display_controller.hpp"

#include <array>
#include <climits>
#include <cmath>
#include <cstdlib>

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

void rgb222ToHsv(int red, int green, int blue, double &hue,
                 double &saturation, double &value) noexcept {
  // Adapted from vdp-gl all-the-plots src/fabutils.cpp:443-463. Keeping this
  // tiny pure calculation local avoids selecting broad classic fabutils.cpp.
  double r = red / 3.0;
  double g = green / 3.0;
  double b = blue / 3.0;
  double maximum = std::fmax(std::fmax(r, g), b);
  double minimum = std::fmin(std::fmin(r, g), b);
  double difference = maximum - minimum;
  if (maximum == minimum)
    hue = 0;
  else if (maximum == r)
    hue = std::fmod(60.0 * ((g - b) / difference) + 360.0, 360.0);
  else if (maximum == g)
    hue = std::fmod(60.0 * ((b - r) / difference) + 120.0, 360.0);
  else
    hue = std::fmod(60.0 * ((r - g) / difference) + 240.0, 360.0);
  saturation = maximum == 0 ? 0 : (difference / maximum) * 100.0;
  value = maximum * 100.0;
}

struct RGB222Value {
  std::uint8_t red;
  std::uint8_t green;
  std::uint8_t blue;
};

constexpr std::array<RGB222Value, 16> kPalette16{{
    {0, 0, 0}, {2, 0, 0}, {0, 2, 0}, {2, 2, 0},
    {0, 0, 2}, {2, 0, 2}, {0, 2, 2}, {2, 2, 2},
    {1, 1, 1}, {3, 0, 0}, {0, 3, 0}, {3, 3, 0},
    {0, 0, 3}, {3, 0, 3}, {0, 3, 3}, {3, 3, 3},
}};
constexpr std::array<RGB222Value, 8> kPalette8{{
    {0, 0, 0}, {2, 0, 0}, {0, 2, 0}, {0, 0, 2},
    {3, 0, 0}, {0, 3, 0}, {0, 0, 3}, {3, 3, 3},
}};
constexpr std::array<RGB222Value, 4> kPalette4{{
    {0, 0, 0}, {0, 0, 3}, {0, 3, 0}, {3, 3, 3},
}};
constexpr std::array<RGB222Value, 2> kPalette2{{{0, 0, 0}, {3, 3, 3}}};

template <std::size_t Size>
std::uint8_t nearestPalette(std::array<RGB222Value, Size> const &palette,
                            std::uint8_t packed) noexcept {
  double h1 = 0, s1 = 0, v1 = 0;
  rgb222ToHsv(packed & 3, (packed >> 2) & 3, (packed >> 4) & 3, h1, s1, v1);
  std::uint8_t best = 0;
  double best_distance = 1.0e30;
  for (std::size_t index = 0; index < palette.size(); ++index) {
    double h2 = 0, s2 = 0, v2 = 0;
    rgb222ToHsv(palette[index].red, palette[index].green,
                palette[index].blue, h2, s2, v2);
    double dh = h1 - h2, ds = s1 - s2, dv = v1 - v2;
    double distance = dh * dh + ds * ds + dv * dv;
    if (distance <= best_distance) {
      best = static_cast<std::uint8_t>(index);
      best_distance = distance;
      if (distance == 0) break;
    }
  }
  return best;
}

template <std::size_t Size>
fabgl::RGB888 paletteColor(std::array<RGB222Value, Size> const &palette,
                           std::uint8_t index) noexcept {
  RGB222Value value = palette[index % palette.size()];
  return fabgl::RGB888(value.red * 85, value.green * 85, value.blue * 85);
}

void *allocateDisplay(void *, std::size_t size) {
#if defined(ESP_PLATFORM)
  void *result = heap_caps_malloc(size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
  return result != nullptr ? result : heap_caps_malloc(size, MALLOC_CAP_8BIT);
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

Allocator defaultDisplayAllocator() noexcept {
  return {nullptr, allocateDisplay, deallocateDisplay};
}

P4DisplayController::P4DisplayController(Allocator allocator) noexcept
    : storage_(allocator) {}

ConfigureResult P4DisplayController::configure(ModeDescriptor const &mode) noexcept {
  if (frame_service_running_.load(std::memory_order_acquire)) {
    return ConfigureResult::ServiceRunning;
  }
  if (mode.width > INT_MAX || mode.height > INT_MAX) {
    return ConfigureResult::InvalidDimensions;
  }
  ConfigureResult result = storage_.configure(mode);
  if (result != ConfigureResult::Ok) return result;
  setScreenSize(static_cast<int>(mode.width), static_cast<int>(mode.height));
  m_viewPortWidth = static_cast<int>(mode.width);
  m_viewPortHeight = static_cast<int>(mode.height);
  setDoubleBuffered(mode.double_buffered);
  resetPaintState();
  enableBackgroundPrimitiveExecution(false);
  // PORT-003 Phase C inherited-behavior containment: upstream vdp-gl
  // enableBackgroundPrimitiveExecution(false) calls processPrimitives() before
  // changing its private mode flag. processPrimitives() consequently queues a
  // final Refresh instead of executing it synchronously. Drain that artifact
  // now that the flag is false, then establish a clean project-owned sequence
  // baseline. Remove this workaround only if the vendored ordering changes.
  processPrimitives();
  reserved_sequence_.store(0, std::memory_order_release);
  submitted_sequence_.store(0, std::memory_order_release);
  started_sequence_.store(0, std::memory_order_release);
  completed_sequence_.store(0, std::memory_order_release);
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
  frame_service_running_.store(running, std::memory_order_release);
  if (running) {
    reserved_sequence_.store(0, std::memory_order_release);
    submitted_sequence_.store(0, std::memory_order_release);
    started_sequence_.store(0, std::memory_order_release);
    completed_sequence_.store(0, std::memory_order_release);
    cancelled_primitives_.store(0, std::memory_order_release);
  } else {
    // The P4 adapter joins its sole service task before entering this path, so
    // no primitive can be active while queued payloads are cancelled.
    cancelQueuedPrimitives();
    // Return to the Phase B synchronous lifecycle state. Upstream's disable
    // ordering may enqueue its final Refresh in a single-buffered mode, so a
    // second cancellation is required for an actually empty stopped queue.
    enableBackgroundPrimitiveExecution(false);
    cancelQueuedPrimitives();
    auto waiter = completion_waiter_.exchange(nullptr, std::memory_order_acq_rel);
    if (waiter != nullptr) xTaskNotifyGive(waiter);
    if (pending_swap_waiter_ != nullptr) {
      xTaskNotifyGive(pending_swap_waiter_);
      pending_swap_waiter_ = nullptr;
    }
  }
}

std::size_t P4DisplayController::executeFrameWork(
    std::size_t maximum_primitives) {
  if (maximum_primitives == 0 ||
      suspension_depth_.load(std::memory_order_acquire) != 0) {
    return 0;
  }
  executing_frame_work_.store(true, std::memory_order_release);
  fabgl::Rect update(SHRT_MAX, SHRT_MAX, SHRT_MIN, SHRT_MIN);
  std::size_t executed = 0;
  fabgl::Primitive primitive;
  while (executed < maximum_primitives && getPrimitive(&primitive, 0)) {
    execPrimitive(primitive, update, false);
    ++executed;
  }
  showSprites(update);
  executing_frame_work_.store(false, std::memory_order_release);
  return executed;
}

void P4DisplayController::completeFrameWork(
    std::size_t executed_primitives) noexcept {
  while (executed_primitives-- > 0) primitiveCompleted();
}

std::uint32_t P4DisplayController::frameCounter() const noexcept {
  return frame_counter_.load(std::memory_order_acquire);
}

void P4DisplayController::writeFrameCounter(std::uint32_t value) noexcept {
  frame_counter_.store(value, std::memory_order_release);
}

std::uint32_t P4DisplayController::advanceFrameCounter(
    std::uint32_t elapsed_ticks) noexcept {
  return frame_counter_.fetch_add(elapsed_ticks, std::memory_order_acq_rel) +
         elapsed_ticks;
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

std::uint64_t P4DisplayController::submittedSequence() const noexcept {
  return submitted_sequence_.load(std::memory_order_acquire);
}

std::uint64_t P4DisplayController::startedSequence() const noexcept {
  return started_sequence_.load(std::memory_order_acquire);
}

std::uint64_t P4DisplayController::completedSequence() const noexcept {
  return completed_sequence_.load(std::memory_order_acquire);
}

void P4DisplayController::primitivesExecutionWait() {
  std::uint64_t target = submittedSequence();
  while (completedSequence() < target &&
         frame_service_running_.load(std::memory_order_acquire)) {
    auto current = xTaskGetCurrentTaskHandle();
    completion_waiter_.store(current, std::memory_order_release);
    if (completedSequence() >= target ||
        !frame_service_running_.load(std::memory_order_acquire)) {
      completion_waiter_.store(nullptr, std::memory_order_release);
      break;
    }
    ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
    completion_waiter_.store(nullptr, std::memory_order_release);
  }
}

void P4DisplayController::suspendBackgroundPrimitiveExecution() {
  suspension_depth_.fetch_add(1, std::memory_order_acq_rel);
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

void P4DisplayController::primitiveQueued(
    fabgl::Primitive const &) {
  reserved_sequence_.fetch_add(1, std::memory_order_acq_rel);
}

void P4DisplayController::primitiveEnqueued(
    fabgl::Primitive const &) {
  submitted_sequence_.fetch_add(1, std::memory_order_acq_rel);
}

void P4DisplayController::primitiveStarted(
    fabgl::Primitive const &primitive) {
  // The common hook reserves before the blocking send and publishes submission
  // after it. If a frame-service task dequeues in between, wait only for the
  // sender to finish that already-successful queue handoff.
  std::uint64_t next = started_sequence_.load(std::memory_order_acquire) + 1;
  while (submitted_sequence_.load(std::memory_order_acquire) < next) taskYIELD();
  started_sequence_.fetch_add(1, std::memory_order_acq_rel);
  if (primitive.cmd == fabgl::PrimitiveCmd::SwapBuffers)
    pending_swap_waiter_ = primitive.notifyTask;
}

void P4DisplayController::primitiveCompleted() {
  completed_sequence_.fetch_add(1, std::memory_order_acq_rel);
  if (pending_swap_waiter_ != nullptr) {
    xTaskNotifyGive(pending_swap_waiter_);
    pending_swap_waiter_ = nullptr;
  }
  auto waiter = completion_waiter_.load(std::memory_order_acquire);
  if (waiter != nullptr) xTaskNotifyGive(waiter);
}

void P4DisplayController::primitiveCancelled(
    fabgl::Primitive const &primitive) {
  cancelled_primitives_.fetch_add(1, std::memory_order_acq_rel);
  completed_sequence_.fetch_add(1, std::memory_order_acq_rel);
  if (primitive.cmd == fabgl::PrimitiveCmd::SwapBuffers &&
      primitive.notifyTask != nullptr) {
    xTaskNotifyGive(primitive.notifyTask);
  }
}

bool P4DisplayController::deferPrimitiveTaskNotification(
    fabgl::Primitive const &primitive) {
  return primitive.cmd == fabgl::PrimitiveCmd::SwapBuffers;
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
  std::uint8_t packed = static_cast<std::uint8_t>(
      (color.R >> 6) | ((color.G >> 6) << 2) | ((color.B >> 6) << 4));
  switch (storage_.mode().format) {
    case NativePixelFormat::PALETTE2: return nearestPalette(kPalette2, packed);
    case NativePixelFormat::PALETTE4: return nearestPalette(kPalette4, packed);
    case NativePixelFormat::PALETTE8: return nearestPalette(kPalette8, packed);
    case NativePixelFormat::PALETTE16: return nearestPalette(kPalette16, packed);
    case NativePixelFormat::SBGR2222: return packed;
  }
  return 0;
}

fabgl::RGB888 P4DisplayController::logicalToColor(std::uint8_t value) const noexcept {
  switch (storage_.mode().format) {
    case NativePixelFormat::PALETTE2: return paletteColor(kPalette2, value);
    case NativePixelFormat::PALETTE4: return paletteColor(kPalette4, value);
    case NativePixelFormat::PALETTE8: return paletteColor(kPalette8, value);
    case NativePixelFormat::PALETTE16: return paletteColor(kPalette16, value);
    case NativePixelFormat::SBGR2222:
      return fabgl::RGB888((value & 3) * 85, ((value >> 2) & 3) * 85,
                           ((value >> 4) & 3) * 85);
  }
  return {};
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
