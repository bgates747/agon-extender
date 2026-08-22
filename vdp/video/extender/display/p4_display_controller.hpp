// PORT-003 Phase B synchronous logical display controller.
//
// This class binds retained vdp-gl common renderer templates to project-owned
// P4-neutral storage. It deliberately has no frame service, output sink,
// mutable palette/Copper compositor, or physical display-driver inheritance.
#pragma once

#include <atomic>
#include <functional>
#include <memory>

#include "displaycontroller.h"
#include "extender/display/logical_frame_service.hpp"
#include "extender/display/plane_storage.hpp"

namespace agon::extender::display {

class P4DisplayController final : public fabgl::GenericBitmappedDisplayController,
                                  public FrameWorkExecutor {
 public:
  explicit P4DisplayController(Allocator allocator) noexcept;

  ConfigureResult configure(ModeDescriptor const &mode) noexcept;
  ConstPlaneView drawingPlane() const noexcept;
  ConstPlaneView visiblePlane() const noexcept;
  std::uint8_t drawingPlaneIdentity() const noexcept;
  std::uint8_t visiblePlaneIdentity() const noexcept override;

  void setFrameServiceRunning(bool running) noexcept override;
  std::size_t executeFrameWork(
      std::size_t maximum_primitives) override;
  void completeFrameWork(
      std::size_t executed_primitives) noexcept override;
  std::uint32_t frameCounter() const noexcept override;
  void writeFrameCounter(std::uint32_t value) noexcept;
  std::uint32_t advanceFrameCounter(
      std::uint32_t elapsed_ticks) noexcept override;
  std::size_t logicalWidth() const noexcept override;
  std::size_t logicalHeight() const noexcept override;
  NativePixelFormat logicalFormat() const noexcept override;
  bool logicalDoubleBuffered() const noexcept override;
  std::uint64_t submittedSequence() const noexcept;
  std::uint64_t startedSequence() const noexcept;
  std::uint64_t completedSequence() const noexcept;

  void begin() override;
  void setResolution(char const *modeline, int view_port_width = -1,
                     int view_port_height = -1,
                     bool double_buffered = false) override;
  int colorsCount() override;
  fabgl::NativePixelFormat nativePixelFormat() override;
  void primitivesExecutionWait() override;
  void suspendBackgroundPrimitiveExecution() override;
  void resumeBackgroundPrimitiveExecution() override;
  void readScreen(fabgl::Rect const &rect, fabgl::RGB888 *destination) override;

  // Public solely so a deferred Phase B swap request has an explicit
  // fail-fast entry point. Logical swap-at-frame-edge is Phase C behavior.
  void swapBuffers() override;

 protected:
  void setPixelAt(fabgl::PixelDesc const &pixel, fabgl::Rect &update) override;
  void absDrawLine(int x1, int y1, int x2, int y2, fabgl::RGB888 color) override;
  void fillRow(int y, int x1, int x2, fabgl::RGB888 color) override;
  void drawEllipse(fabgl::Size const &size, fabgl::Rect &update) override;
  void absDrawEllipseSheared(fabgl::EllipseShearedParams const &params,
                             fabgl::Rect &update) override;
  void drawArc(fabgl::Rect const &rect, fabgl::Rect &update) override;
  void fillSegment(fabgl::Rect const &rect, fabgl::Rect &update) override;
  void fillSector(fabgl::Rect const &rect, fabgl::Rect &update) override;
  void clear(fabgl::Rect &update) override;
  void VScroll(int scroll, fabgl::Rect &update) override;
  void HScroll(int scroll, fabgl::Rect &update) override;
  void drawGlyph(fabgl::Glyph const &glyph, fabgl::GlyphOptions options,
                 fabgl::RGB888 pen, fabgl::RGB888 brush,
                 fabgl::Rect &update) override;
  void invertRect(fabgl::Rect const &rect, fabgl::Rect &update) override;
  void swapFGBG(fabgl::Rect const &rect, fabgl::Rect &update) override;
  void copyRect(fabgl::Rect const &source, fabgl::Rect &update) override;
  int getBitmapSavePixelSize() override;
  void rawDrawBitmap_Native(int dest_x, int dest_y, fabgl::Bitmap const *bitmap,
                            int x1, int y1, int x_count, int y_count) override;
  void rawDrawBitmap_Mask(int dest_x, int dest_y, fabgl::Bitmap const *bitmap,
                          void *saved_background, int x1, int y1, int x_count,
                          int y_count) override;
  void rawDrawBitmap_RGBA2222(int dest_x, int dest_y,
                              fabgl::Bitmap const *bitmap,
                              void *saved_background, int x1, int y1,
                              int x_count, int y_count) override;
  void rawDrawBitmap_RGBA8888(int dest_x, int dest_y,
                              fabgl::Bitmap const *bitmap,
                              void *saved_background, int x1, int y1,
                              int x_count, int y_count) override;
  void rawCopyToBitmap(int src_x, int src_y, int width, void *save_buffer,
                       int x1, int y1, int x_count, int y_count) override;
  void rawDrawBitmapWithMatrix_Mask(int dest_x, int dest_y,
                                    fabgl::Rect &drawing_rect,
                                    fabgl::Bitmap const *bitmap,
                                    float const *inverse) override;
  void rawDrawBitmapWithMatrix_RGBA2222(int dest_x, int dest_y,
                                        fabgl::Rect &drawing_rect,
                                        fabgl::Bitmap const *bitmap,
                                        float const *inverse) override;
  void rawDrawBitmapWithMatrix_RGBA8888(int dest_x, int dest_y,
                                        fabgl::Rect &drawing_rect,
                                        fabgl::Bitmap const *bitmap,
                                        float const *inverse) override;
  void primitiveQueued(fabgl::Primitive const &primitive) override;
  void primitiveEnqueued(fabgl::Primitive const &primitive) override;
  void primitiveStarted(fabgl::Primitive const &primitive) override;
  void primitiveCompleted() override;
  void primitiveCancelled(fabgl::Primitive const &primitive) override;
  bool deferPrimitiveTaskNotification(
      fabgl::Primitive const &primitive) override;

 private:
  using PixelWriter = std::function<void(int, int, std::uint8_t)>;
  using RowPixelWriter = std::function<void(std::uint8_t *, int, std::uint8_t)>;
  using RowFiller = std::function<void(int, int, int, std::uint8_t)>;

  std::uint8_t *row(int y) noexcept;
  std::uint8_t const *row(int y) const noexcept;
  std::uint8_t readLogical(std::uint8_t const *source, int x) const noexcept;
  void writeLogical(std::uint8_t *destination, int x, std::uint8_t value) noexcept;
  std::uint8_t colorToLogical(fabgl::RGB888 const &color) const noexcept;
  fabgl::RGB888 logicalToColor(std::uint8_t value) const noexcept;
  void writePainted(std::uint8_t *destination, int x, std::uint8_t value,
                    fabgl::PaintMode mode) noexcept;
  PixelWriter pixelWriter(fabgl::PaintMode mode);
  RowPixelWriter rowPixelWriter(fabgl::PaintMode mode);
  RowFiller rowFiller(fabgl::PaintMode mode);
  void rawFillRow(int y, int x1, int x2, std::uint8_t value) noexcept;
  void rawCopyRow(int x1, int x2, int source_y, int destination_y) noexcept;
  std::uint8_t nativeSavePixel(std::uint8_t logical) const noexcept;

  PlaneStorage storage_;
  std::atomic<std::uint64_t> reserved_sequence_{};
  std::atomic<std::uint64_t> submitted_sequence_{};
  std::atomic<std::uint64_t> started_sequence_{};
  std::atomic<std::uint64_t> completed_sequence_{};
  std::atomic<std::uint64_t> cancelled_primitives_{};
  std::atomic<std::uint32_t> frame_counter_{};
  std::atomic<std::uint32_t> suspension_depth_{};
  std::atomic<bool> frame_service_running_{};
  std::atomic<bool> executing_frame_work_{};
  std::atomic<TaskHandle_t> completion_waiter_{};
  TaskHandle_t pending_swap_waiter_{};
};

Allocator defaultDisplayAllocator() noexcept;
std::unique_ptr<fabgl::BitmappedDisplayController> makeP4DisplayController();

}  // namespace agon::extender::display
