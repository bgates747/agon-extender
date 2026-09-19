# EVP1 six-bit extension

## Executive summary

The packed=2 capability adds direct six-bit RGB222 samples. Existing packed=1
requests retain exactly the previous 1/2/4-bit palette choices. RLE2 remains
eligible with rle2=1&packed=2, which the new browser requests by default.

The existing32-byte header is unchanged. Payload begins [6,0,0,0]: six bits per
pixel, no palette, reserved zeros. Pixels are packed MSB-first across the whole
raster, four pixels per three bytes. Trailing low bits are zero. Payload length
is4+ceil(width*height*6/8). Decode reconstructs the original RGB222 byte values;
no transparency or quantization. Source pixels outside0–63 are rejected.

Lower-depth frames retain palette packing when eligible. Six-bit encoding is
used only after discovering more than16 final colours, and only if smaller than
the currently selected raw/RLE2 payload. Scratch capacity rises from393252 to
589828 bytes. No compositor, drawing, scheduler or game cadence changes.

For512×384, a direct six-bit packet is147492 bytes including headers, compared
to196640 raw. RLE2 may be much smaller than either, so six-bit support alone
must not be described as a guaranteed Nurples speed improvement.
