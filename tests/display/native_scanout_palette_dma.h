// Host fixture interface between the production C DMA driver and C++ stock renderer.
#pragma once
#include <stdbool.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
void palette_dma_start(void);
bool palette_dma_bind(void *context,
                      bool (*render)(void *,uint8_t *,unsigned,unsigned,unsigned,unsigned,unsigned,uint32_t,bool *),
                      void (*wake)(void *));
void palette_dma_unbind(void);
void palette_dma_advance_to(unsigned frame, unsigned block);
void palette_dma_stop(void);
void palette_check_strip(unsigned frame, unsigned block, const uint8_t *pixels);
void palette_frame_complete(unsigned completed);
#ifdef __cplusplus
}
#endif
