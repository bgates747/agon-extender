# Image encoder selection

## Executive summary

Use ESP-IDF's hardware JPEG driver with RGB888 input and YUV444 output. Use
PNGenc for indexed PNG: Espressif's official ESP-VISION PNG wrapper instead
uses OpenMV-derived LodePNG and does not expose our indexed source directly.
Neither name nor official provenance establishes performance on this workload.

1. Official JPEG API: https://docs.espressif.com/projects/esp-idf/en/stable/esp32p4/api-reference/peripherals/jpeg.html
   Installed build uses IDF5.5.5, specifically components/esp_driver_jpeg/
   include/driver/jpeg_encode.h and jpeg_encode.c. RGB888/BGR byte layout is
   checked on silicon with exact primary-colour patches. Allocator supplies
   DMA/cache alignment; driver performs cache synchronisation. CPU conversion,
   driver elapsed encode time and browser decode remain separate measurements.
   Driver itself may allocate internal descriptors; our wrapper reuses its engine
   and preallocated input/output buffers. We do not claim globally zero allocation.
2. Official ESP-VISION source https://github.com/espressif/esp-vision at
   7f8fa58cc6d6cf5c41bcbb881d3b999b39136f0b:
   components/imlib/upstream/png.c uses LodePNG, window1024; wrapper cases are
   binary, grayscale and RGB565, not a ready indexed-PNG encoder interface.
   It allocates through its framebuffer allocator and is coupled to its runtime.
   No need to import that framework just to encode our existing indices.
3. PNGenc https://github.com/bitbank2/PNGenc at
   23e97d1c146ef572fb9e073bbcafd2fbf212a57a:
   Apache2 license, bundled zlib notices retained. Embedded configuration uses
   MEM_SHRINK3, unlike Linux default0. Preserve embedded settings and report
   that this is not identical to the prior desktop zlib encoder. Fixed encoder
   workspace allocated once in PSRAM; row API receives exact indices. Its BGR
   palette input is expanded to PNG RGB entries by png.inl. 8-bit indexed output
   carries256 palette entries, of which64 are meaningful; unused entries black.
4. Existing native-pixel contract is final00BBGGRR; colour levels0/85/170/255.
   This is already composed colour, not an application palette number. Reference
   video/extender/web/frame_protocol.js and native_pixel_codec.cpp in retained
   candidate. No MOS/VDU command or rendering behaviour changes in this task.
5. Both compressed-image browser paths use createImageBitmap with colour-space
   conversion/premultiplication disabled, then WebGL texture upload. No per-frame
   canvas readback in delivery timing. Separate correctness tests read pixels and
   compare PNG exactly and JPEG by error metrics and retained images.

## Experimental envelope

EVJ1/EVP1 retain32-byte EVF1 metadata describing original RGB222 pixels; remaining
message is a complete JPEG/PNG. Dimensions are bounded512x384; embedded image
geometry must match envelope. Explicit jpeg=80/90/95 and png=1/3 queries only;
raw/RLE2 controls are unchanged. This private protocol is not a production API.
