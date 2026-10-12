// Task-owned private linear snapshot and fixed RGB222 CLUT expander.
#pragma once
#include <cstddef>
#include <cstdint>
namespace agon::extender::display {
class HdmiPpaIndexed {
 public:
  bool initialize();
  void reset();
  std::uint8_t *source() { return source_; }
  bool expand(std::uint8_t *output,std::size_t bytes,int outputWidth,int outputHeight,
              int width,int height,int left=0,int top=0);
 private:
  void *client_{};
  std::uint8_t *source_{},*transparent_{};
};
}
