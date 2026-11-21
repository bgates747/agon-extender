// Independent known colours for the real stock software-sprite, hardware-sprite,
// XOR text-cursor and mouse-cursor paths. Both levels straddle a 32-line seam.
#pragma once

static void exerciseOverlayMarkers(int width, int height, int carrier_width, int carrier_height) {
  using namespace fabgl;
  TestController<VGA64Controller> display;
  display.begin();
  display.enableBackgroundPrimitiveExecution(false);
  char modeline[120];
  std::snprintf(modeline, sizeof(modeline), "\"markers\" 1 %d %d %d %d %d %d %d %d -HSync -VSync",
                width, width+4, width+8, width+16, height, height+2, height+4, height+8);
  display.setResolution(modeline, width, height, false);
  assert(display.getViewPortWidth() == width && display.getViewPortHeight() == height);
  const int repeat = width == 320 ? 2 : 1;
  const int seam = 32 / repeat - 1, left = (carrier_width - width * repeat) / 2;
  Canvas canvas(&display);
  canvas.setBrushColor(RGB888(0,0,255));
  canvas.clear();
  canvas.setPixel(9, seam - 2, RGB888(255,255,0));
  uint8_t software_pixels[] = {0xc3,0x00,0xcc,0xcf}; // red, transparent; green, yellow
  uint8_t hardware_pixels[] = {0xff,0xff,0xff,0xff};
  uint8_t text_pixels[] = {0xc3,0xc3,0xc3,0xc3};   // XOR red over blue = magenta
  uint8_t mouse_pixels[] = {0xfc,0xfc,0xfc,0xfc};  // cyan, covers hardware at intersection
  Bitmap software(2,2,software_pixels,PixelFormat::RGBA2222);
  Bitmap hardware(2,2,hardware_pixels,PixelFormat::RGBA2222);
  Bitmap text_bitmap(2,2,text_pixels,PixelFormat::RGBA2222);
  Cursor mouse{1,1,Bitmap(2,2,mouse_pixels,PixelFormat::RGBA2222)};
  Sprite sprites[2], text_cursor;
  sprites[0].addBitmap(&software)->moveTo(20,seam);
  sprites[1].addBitmap(&hardware)->moveTo(35,seam);
  sprites[1].hardware = true;
  display.setSprites(sprites,2);
  text_cursor.addBitmap(&text_bitmap)->moveTo(34,seam);
  text_cursor.hardware = true;
  text_cursor.paintOptions.mode = PaintMode::XOR;
  display.setTextCursor(&text_cursor);
  display.setMouseCursor(&mouse);
  display.setMouseCursorPos(37,seam+2); // bitmap origin is (36,seam+1)

  NativeRowComposer composer;
  assert(composer.configure(width,height,carrier_width,carrier_height));
  std::array<std::vector<uint8_t>,3> strips;
  std::array<bool,3> black{};
  for (auto &s : strips) s.resize(carrier_width * 32 * 3);
  for (int phase = 0; phase < 2; ++phase) {
    if (phase != 0) {
      // Scroll through the original software sprite; restoration must recover
      // the background pixels when the sprite moves across the viewport edge.
      canvas.setScrollingRegion(8,seam-3,21,seam+4);
      canvas.scroll(0,1);
      sprites[0].moveTo(24,seam);
      display.refreshSprites();
      text_cursor.visible = false;
    }
    auto expected = [&](int x, int y, bool physical) -> uint8_t {
      int result = x == 9 && y == seam - 2 + phase ? 15 : 48;
      const int dx = x-(phase ? 24 : 20), dy = y-seam;
      if (dx >= 0 && dx < 2 && dy >= 0 && dy < 2) {
        const int pattern = software_pixels[dy*2+dx];
        if (pattern & 0xc0) result = pattern & 63;
      }
      if (physical) {
        if (phase == 0 && x >= 34 && x <= 35 && y >= seam && y <= seam+1) result ^= 3;
        if (x >= 35 && x <= 36 && y >= seam && y <= seam+1) result = 63;
        if (x >= 36 && x <= 37 && y >= seam+1 && y <= seam+2) result = 60;
      }
      return static_cast<uint8_t>(result);
    };
    auto checkLogical = [&] {
      for (int y = seam-3; y <= seam+4; ++y) {
        RGB888 row[34];
        display.readScreen(Rect(7,y,40,y),row);
        for (int x = 7; x <= 40; ++x) {
          const auto &p = row[x-7];
          const uint8_t rgb = (p.R >> 6) | ((p.G >> 6) << 2) | ((p.B >> 6) << 4);
          assert(rgb == expected(x,y,false));
        }
      }
    };
    checkLogical();
    for (int y0 = 0; y0 < carrier_height; y0 += 32) {
      const int slot = (y0 / 32) % 3;
      uint8_t *strip = strips[slot].data();
      assert(composer.fill(strip,y0,32,slot,black[slot],[&](int y,bool,uint8_t *row) {
        display.prepareStockRowQuiescent(y,row);
      }));
      for (int y = std::max(y0,(seam-3)*repeat); y < std::min(y0+32,(seam+5)*repeat); ++y) {
        for (int x = 7*repeat; x < 41*repeat; ++x) {
          const int c = expected(x/repeat,y/repeat,true);
          const auto *p = strip + 3*((y-y0)*carrier_width+left+x);
          assert(p[0] == (c>>4)*85 && p[1] == ((c>>2)&3)*85 && p[2] == (c&3)*85);
        }
      }
    }
    checkLogical();
  }
  display.setTextCursor(nullptr);
  display.setMouseCursor(nullptr);
  display.removeSprites();
  display.end();
  std::printf("PASS %dx%d %dx markers, same software pixels on readback, XOR cursor, hardware and mouse priority across strip seam\n",
              width,height,repeat);
}
