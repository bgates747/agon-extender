// Experimental C boundary between the pinned DPI derivative and scene owner.
#pragma once
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
typedef struct {unsigned background;int left,top,width,height;} agon_scanout_frame;
agon_scanout_frame agon_scanout_latch(void);
void agon_scanout_compose(uint8_t *pixels,unsigned first_y,unsigned rows);
// No DMA/composition or staging may remain active at this lifetime boundary.
void agon_scanout_reset(void);
unsigned agon_scanout_front(void);
unsigned agon_scanout_width(void);
unsigned agon_scanout_height(void);
#ifdef __cplusplus
}
namespace fabgl {class P4Rgb888Controller;}
// Caller owns native exclusion when passing a live controller. Stage copies
// pixels; commit occurs only after the source background cache flush.
bool agon_scanout_stage(fabgl::P4Rgb888Controller *,unsigned,int,int);
void agon_scanout_commit();
#endif
