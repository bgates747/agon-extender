// PlatformIO embeds each authoritative browser source as an immutable text
// object. The linker appends one NUL byte; HTTP lengths deliberately exclude
// that build artifact while preserving every source byte before it.
#include "extender/web/embedded_assets.hpp"

namespace agon::extender::web {
namespace {

extern std::uint8_t const index_html_start[]
    asm("_binary_index_html_start");
extern std::uint8_t const index_html_end[] asm("_binary_index_html_end");
extern std::uint8_t const style_css_start[]
    asm("_binary_style_css_start");
extern std::uint8_t const style_css_end[] asm("_binary_style_css_end");
extern std::uint8_t const app_js_start[] asm("_binary_app_js_start");
extern std::uint8_t const app_js_end[] asm("_binary_app_js_end");
extern std::uint8_t const frame_protocol_js_start[]
    asm("_binary_frame_protocol_js_start");
extern std::uint8_t const frame_protocol_js_end[]
    asm("_binary_frame_protocol_js_end");
extern std::uint8_t const webgl2_presenter_js_start[]
    asm("_binary_webgl2_presenter_js_start");
extern std::uint8_t const webgl2_presenter_js_end[]
    asm("_binary_webgl2_presenter_js_end");

std::size_t textSize(std::uint8_t const *start,
                     std::uint8_t const *end) noexcept {
  if (start == nullptr || end <= start) return 0;
  auto size = static_cast<std::size_t>(end - start);
  if (size != 0 && start[size - 1] == 0) --size;
  return size;
}

}  // namespace

std::array<EmbeddedAsset, 5> const &embeddedBrowserAssets() noexcept {
  static std::array<EmbeddedAsset, 5> const assets{{
      {"/", "text/html; charset=utf-8", index_html_start,
       textSize(index_html_start, index_html_end)},
      {"/style.css", "text/css; charset=utf-8", style_css_start,
       textSize(style_css_start, style_css_end)},
      {"/app.js", "text/javascript; charset=utf-8", app_js_start,
       textSize(app_js_start, app_js_end)},
      {"/frame_protocol.js", "text/javascript; charset=utf-8",
       frame_protocol_js_start,
       textSize(frame_protocol_js_start, frame_protocol_js_end)},
      {"/webgl2_presenter.js", "text/javascript; charset=utf-8",
       webgl2_presenter_js_start,
       textSize(webgl2_presenter_js_start, webgl2_presenter_js_end)},
  }};
  return assets;
}

}  // namespace agon::extender::web
