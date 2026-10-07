#ifndef P4PC_RENDER_REFERENCE_H
#define P4PC_RENDER_REFERENCE_H
#include <stdint.h>
#include <stddef.h>
#define REFERENCE_DOTS 24
struct reference_dot { int x,y,size; uint32_t rgb; };
uint8_t reference_rgb332(uint32_t rgb);
void reference_render(uint8_t *buffer,int width,int height,int bytes_per_pixel,
                      const struct reference_dot *dots,size_t count);
#endif
