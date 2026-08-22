// PORT-003 Phase B retained-renderer host adapter.
//
// This executable contains no expected pixels. It translates fixture commands
// into the real vendored Canvas/common renderer and reports raw storage plus
// public readScreen output for comparison with the independent Python oracle.
#include <cstdlib>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "canvas.h"
#include "extender/display/p4_display_controller.hpp"

namespace display = agon::extender::display;

namespace {

std::vector<std::string> fields(std::string const &value) {
  std::vector<std::string> result;
  std::stringstream stream(value);
  std::string field;
  while (std::getline(stream, field, ',')) result.push_back(field);
  return result;
}

int number(std::vector<std::string> const &values, std::size_t index) {
  if (index >= values.size()) throw std::invalid_argument("missing operation field");
  return std::stoi(values[index]);
}

std::vector<std::uint8_t> byteList(std::string const &encoded) {
  std::vector<std::uint8_t> result;
  std::stringstream stream(encoded);
  std::string item;
  while (std::getline(stream, item, ':'))
    result.push_back(static_cast<std::uint8_t>(std::stoi(item)));
  return result;
}

fabgl::PaintMode paintMode(std::string const &name) {
  if (name == "Set") return fabgl::PaintMode::Set;
  if (name == "OR") return fabgl::PaintMode::OR;
  if (name == "AND") return fabgl::PaintMode::AND;
  if (name == "XOR") return fabgl::PaintMode::XOR;
  if (name == "Invert") return fabgl::PaintMode::Invert;
  if (name == "NoOp") return fabgl::PaintMode::NoOp;
  if (name == "ANDNOT") return fabgl::PaintMode::ANDNOT;
  if (name == "ORNOT") return fabgl::PaintMode::ORNOT;
  throw std::invalid_argument("unknown paint mode");
}

display::NativePixelFormat parseFormat(std::string const &name) {
  if (name == "PALETTE2") return display::NativePixelFormat::PALETTE2;
  if (name == "PALETTE4") return display::NativePixelFormat::PALETTE4;
  if (name == "PALETTE8") return display::NativePixelFormat::PALETTE8;
  if (name == "PALETTE16") return display::NativePixelFormat::PALETTE16;
  if (name == "SBGR2222") return display::NativePixelFormat::SBGR2222;
  throw std::invalid_argument("unknown format");
}

fabgl::RGB888 logicalColor(display::NativePixelFormat format, int value) {
  static constexpr int palette2[][3] = {{0, 0, 0}, {3, 3, 3}};
  static constexpr int palette4[][3] = {
      {0, 0, 0}, {0, 0, 3}, {0, 3, 0}, {3, 3, 3}};
  static constexpr int palette8[][3] = {
      {0, 0, 0}, {2, 0, 0}, {0, 2, 0}, {0, 0, 2},
      {3, 0, 0}, {0, 3, 0}, {0, 0, 3}, {3, 3, 3}};
  static constexpr int palette16[][3] = {
      {0, 0, 0}, {2, 0, 0}, {0, 2, 0}, {2, 2, 0},
      {0, 0, 2}, {2, 0, 2}, {0, 2, 2}, {2, 2, 2},
      {1, 1, 1}, {3, 0, 0}, {0, 3, 0}, {3, 3, 0},
      {0, 0, 3}, {3, 0, 3}, {0, 3, 3}, {3, 3, 3}};
  auto make = [](int const rgb[3]) {
    return fabgl::RGB888(rgb[0] * 85, rgb[1] * 85, rgb[2] * 85);
  };
  switch (format) {
    case display::NativePixelFormat::PALETTE2: return make(palette2[value]);
    case display::NativePixelFormat::PALETTE4: return make(palette4[value]);
    case display::NativePixelFormat::PALETTE8: return make(palette8[value]);
    case display::NativePixelFormat::PALETTE16: return make(palette16[value]);
    case display::NativePixelFormat::SBGR2222: {
      int rgb[] = {value & 3, (value >> 2) & 3, (value >> 4) & 3};
      return make(rgb);
    }
  }
  std::abort();
}

void setValue(fabgl::Canvas &canvas, display::NativePixelFormat format,
              int x, int y, int value) {
  canvas.setPixel(x, y, logicalColor(format, value));
}

void execute(fabgl::Canvas &canvas, display::NativePixelFormat format,
             int width, int height, std::string const &encoded) {
  auto op = fields(encoded);
  if (op.empty()) throw std::invalid_argument("empty operation");
  if (op[0] == "set_pixel") {
    setValue(canvas, format, number(op, 1), number(op, 2), number(op, 3));
  } else if (op[0] == "seed_formula") {
    int x_factor = number(op, 1), y_factor = number(op, 2), maximum = number(op, 3);
    for (int y = 0; y < height; ++y)
      for (int x = 0; x < width; ++x)
        setValue(canvas, format, x, y, (x * x_factor + y * y_factor) & maximum);
  } else if (op[0] == "line") {
    canvas.setPenColor(logicalColor(format, number(op, 5)));
    canvas.drawLine(number(op, 1), number(op, 2), number(op, 3), number(op, 4));
  } else if (op[0] == "fill_row") {
    canvas.setPenColor(logicalColor(format, number(op, 4)));
    canvas.drawLine(number(op, 2), number(op, 1), number(op, 3), number(op, 1));
  } else if (op[0] == "copy_rect") {
    int x1 = number(op, 1), y1 = number(op, 2), x2 = number(op, 3), y2 = number(op, 4);
    canvas.copyRect(x1, y1, number(op, 5), number(op, 6), x2 - x1 + 1, y2 - y1 + 1);
  } else if (op[0] == "vscroll") {
    canvas.setScrollingRegion(number(op, 1), number(op, 2), number(op, 3), number(op, 4));
    canvas.scroll(0, number(op, 5));
  } else if (op[0] == "hscroll") {
    canvas.setScrollingRegion(number(op, 1), number(op, 2), number(op, 3), number(op, 4));
    canvas.scroll(number(op, 5), 0);
  } else if (op[0] == "set_origin") {
    canvas.setOrigin(number(op, 1), number(op, 2));
  } else if (op[0] == "set_clip") {
    canvas.setClippingRect(fabgl::Rect(number(op, 1), number(op, 2),
                                       number(op, 3), number(op, 4)));
  } else if (op[0] == "fill_rect") {
    canvas.setBrushColor(logicalColor(format, number(op, 5)));
    canvas.fillRectangle(number(op, 1), number(op, 2), number(op, 3), number(op, 4));
  } else if (op[0] == "invert_rect") {
    canvas.invertRectangle(number(op, 1), number(op, 2), number(op, 3), number(op, 4));
  } else if (op[0] == "paint_pixel") {
    fabgl::PaintOptions options;
    options.mode = paintMode(op.at(1));
    canvas.setPaintOptions(options);
    setValue(canvas, format, number(op, 2), number(op, 3), number(op, 4));
    canvas.resetPaintOptions();
  } else if (op[0] == "clear") {
    canvas.setBrushColor(logicalColor(format, number(op, 1)));
    canvas.clear();
  } else if (op[0] == "glyph") {
    auto rows = byteList(op.at(6));
    canvas.setPenColor(logicalColor(format, number(op, 3)));
    canvas.setBrushColor(logicalColor(format, number(op, 4)));
    fabgl::GlyphOptions options{};
    options.value = 0;
    options.fillBackground = number(op, 5) != 0;
    canvas.setGlyphOptions(options);
    canvas.drawGlyph(number(op, 1), number(op, 2), 3, 3, rows.data());
  } else if (op[0] == "flood_fill") {
    canvas.setPenColor(logicalColor(format, number(op, 4)));
    canvas.moveTo(number(op, 1), number(op, 2));
    canvas.floodFill(logicalColor(format, number(op, 3)), number(op, 5) != 0);
  } else if (op[0] == "ellipse") {
    canvas.setPenColor(logicalColor(format, number(op, 5)));
    canvas.drawEllipse(number(op, 1), number(op, 2), number(op, 3), number(op, 4));
  } else if (op[0] == "arc" || op[0] == "segment" || op[0] == "sector") {
    canvas.setPenColor(logicalColor(format, number(op, 7)));
    canvas.setBrushColor(logicalColor(format, number(op, 7)));
    if (op[0] == "arc")
      canvas.drawArc(number(op, 1), number(op, 2), number(op, 3), number(op, 4),
                     number(op, 5), number(op, 6));
    else if (op[0] == "segment")
      canvas.fillSegment(number(op, 1), number(op, 2), number(op, 3), number(op, 4),
                         number(op, 5), number(op, 6));
    else
      canvas.fillSector(number(op, 1), number(op, 2), number(op, 3), number(op, 4),
                        number(op, 5), number(op, 6));
  } else if (op[0].rfind("bitmap_", 0) == 0) {
    int x = number(op, 1), y = number(op, 2), bitmap_width = number(op, 3);
    int bitmap_height = number(op, 4);
    bool mask = op[0] == "bitmap_mask";
    auto data = byteList(op.at(mask ? 6 : 5));
    fabgl::PixelFormat pixel_format = fabgl::PixelFormat::Native;
    if (mask) pixel_format = fabgl::PixelFormat::Mask;
    else if (op[0].find("rgba2222") != std::string::npos)
      pixel_format = fabgl::PixelFormat::RGBA2222;
    else if (op[0] == "bitmap_rgba8888")
      pixel_format = fabgl::PixelFormat::RGBA8888;
    fabgl::Bitmap bitmap(bitmap_width, bitmap_height, data.data(), pixel_format,
                         mask ? logicalColor(format, number(op, 5))
                              : fabgl::RGB888(255, 255, 255), false);
    if (op[0] == "bitmap_transform_rgba2222") {
      float identity[] = {1, 0, 0, 0, 1, 0, 0, 0, 1};
      canvas.drawTransformedBitmap(x, y, &bitmap, identity, identity);
    } else {
      canvas.drawBitmap(x, y, &bitmap);
    }
  } else {
    throw std::invalid_argument("unknown operation: " + op[0]);
  }
}

void printHex(std::uint8_t const *data, std::size_t size) {
  static constexpr char hex[] = "0123456789abcdef";
  for (std::size_t index = 0; index < size; ++index)
    std::cout << hex[data[index] >> 4] << hex[data[index] & 15];
}

}  // namespace

int main(int argc, char **argv) {
  if (argc < 5) return 2;
  try {
    auto format = parseFormat(argv[1]);
    int width = std::stoi(argv[2]), height = std::stoi(argv[3]);
    bool double_buffered = std::stoi(argv[4]) != 0;
    display::P4DisplayController controller(display::defaultDisplayAllocator());
    if (controller.configure({static_cast<std::size_t>(width),
                              static_cast<std::size_t>(height), format, double_buffered,
                              0xC0}) != display::ConfigureResult::Ok)
      return 3;
    fabgl::Canvas canvas(&controller);
    for (int argument = 5; argument < argc; ++argument)
      execute(canvas, format, width, height, argv[argument]);

    auto plane = controller.drawingPlane();
    std::cout << "bytes=";
    printHex(plane.data, plane.size);
    auto visible = controller.visiblePlane();
    std::cout << "\nvisible=";
    printHex(visible.data, visible.size);
    std::cout << "\nreadback=";
    std::vector<fabgl::RGB888> pixels(static_cast<std::size_t>(width) * height);
    controller.readScreen(fabgl::Rect(0, 0, width - 1, height - 1), pixels.data());
    for (auto const &pixel : pixels) {
      printHex(&pixel.R, 1);
      printHex(&pixel.G, 1);
      printHex(&pixel.B, 1);
    }
    std::vector<std::uint8_t> saved(static_cast<std::size_t>(width) * height);
    canvas.setOrigin(0, 0);
    canvas.setClippingRect(fabgl::Rect(0, 0, width - 1, height - 1));
    // Canvas exposes screen capture only through an RGBA2222-tagged bitmap;
    // the controller's one-byte native-save contract fills that buffer.
    fabgl::Bitmap native(width, height, saved.data(), fabgl::PixelFormat::RGBA2222, false);
    canvas.copyToBitmap(0, 0, &native);
    std::cout << "\nnative_save=";
    printHex(saved.data(), saved.size());
    std::cout << '\n';
    return 0;
  } catch (std::exception const &error) {
    std::cerr << error.what() << '\n';
    return 4;
  }
}
