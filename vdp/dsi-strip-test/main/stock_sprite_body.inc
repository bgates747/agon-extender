/*
  Created by Fabrizio Di Vittorio (fdivitto2013@gmail.com) - <http://www.fabgl.com>
  Copyright (c) 2019-2022 Fabrizio Di Vittorio.
  All rights reserved.


* Please contact fdivitto2013@gmail.com if you need a commercial license.


* This library and related software is available under GPL v3.

  FabGL is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  FabGL is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with FabGL.  If not, see <http://www.gnu.org/licenses/>.
 */
// Unchanged function body from vendor source; see source-provenance.json.
void IRAM_ATTR VGAPalettedController::rawDrawSpriteScanline(uint8_t * pixelData, Sprite * sprite, int scanRow, int scanWidth, int viewportHeight) {
  auto spriteFrame = sprite->getFrame();
  if (!spriteFrame) {
    return;
  }
  int spriteWidth = spriteFrame->width;
  int spriteHeight = spriteFrame->height;

  int spriteY = sprite->y;
  int spriteYend = spriteY + spriteHeight;
  if (scanRow < spriteY) return;
  if (scanRow >= spriteYend) return;
  int offsetY = scanRow - spriteY;

  int spriteX = sprite->x;
  if (spriteX >= scanWidth) return;
  int spriteXend = spriteX + spriteWidth;
  if (spriteXend <= 0) return;

  int offsetX = spriteX < 0 ? -spriteX : 0;
  int drawWidth = spriteXend > scanWidth ?
      scanWidth - spriteX :
      spriteWidth - offsetX;
  if (drawWidth <= 0) return;

  switch (spriteFrame->format) {
    case PixelFormat::RGBA8888: {
        auto src = (const uint32_t*)(spriteFrame->data) + (offsetY * spriteWidth) + offsetX;
        auto pos = spriteX + offsetX;
        while (drawWidth--) {
          auto src_pix = *src++;
          if (src_pix & 0xFF000000) {
            auto r = (src_pix & 0x000000C0) >> (8-2);
            auto g = (src_pix & 0x0000C000) >> (16-4);
            auto b = (src_pix & 0x00C00000) >> (24-6);
            pixelData[pos^2] = r | g | b | m_HVSync;
          }
          pos++;
        }
      }
      break;

    case PixelFormat::RGBA2222: {
        auto src = spriteFrame->data + (offsetY * spriteWidth) + offsetX;
        auto pos = spriteX + offsetX;
        if (sprite->paintOptions.mode == PaintMode::XOR) {
          // XOR mode
          while (drawWidth--) {
            if (*src & 0xC0) {
              auto rgb = *src & 0x3F;
              pixelData[pos^2] ^= rgb;
            }
            src++;
            pos++;
          }
        } else {
          // normal mode
          while (drawWidth--) {
            if (*src & 0xC0) {
              auto rgb = *src & 0x3F;
              pixelData[pos^2] = rgb | m_HVSync;
            }
            src++;
            pos++;
          }
        }
      }
      break;
  }
}

