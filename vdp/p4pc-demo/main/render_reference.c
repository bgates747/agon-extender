/* P4PC-001 render-only memory-format reference, not a replacement LVGL backend.
 * Both formats use the same opaque, aliased circle spans and full-frame clear.
 * RGB332 packs RRR GGG BB; RGB888 stores B,G,R to match the current panel memory.
 * No GUI labels, antialiasing, transport, scanout or palette conversion pass.
 * The format-specific span kernels intentionally avoid per-pixel dispatch.
 */
#include "render_reference.h"
#include <string.h>
#include <stdbool.h>
struct span { int left,length; };
static struct span circles[4][44];
static bool initialized;
uint8_t reference_rgb332(uint32_t rgb)
{
    return ((rgb>>16)&0xe0)|((rgb>>11)&0x1c)|((rgb>>6)&3);
}
static void fill(uint8_t *dst,size_t pixels,uint32_t rgb,int cpp)
{
    if(cpp==1) {memset(dst,reference_rgb332(rgb),pixels);return;}
    uint8_t b=rgb,g=rgb>>8,r=rgb>>16;
    /* Align without misaligned word stores; each 12-byte group is four pixels.
     * memcpy of constant size avoids strict-aliasing violations. */
    while(pixels && ((uintptr_t)dst&3)) {
        dst[0]=b;dst[1]=g;dst[2]=r;dst+=3;pixels--;
    }
    uint32_t words[3]={b|((uint32_t)g<<8)|((uint32_t)r<<16)|((uint32_t)b<<24),
        g|((uint32_t)r<<8)|((uint32_t)b<<16)|((uint32_t)g<<24),
        r|((uint32_t)b<<8)|((uint32_t)g<<16)|((uint32_t)r<<24)};
    while(pixels>=4) {memcpy(dst,words,12);dst+=12;pixels-=4;}
    while(pixels--) {dst[0]=b;dst[1]=g;dst[2]=r;dst+=3;}
}
static void initialize(void)
{
    for(int k=0;k<4;k++) {
        int size=14+10*k;
        for(int y=0;y<size;y++) {
            int first=size,last=-1,dy=2*y+1-size;
            for(int x=0;x<size;x++) {
                int dx=2*x+1-size;
                if(dx*dx+dy*dy<=size*size) {if(first==size)first=x;last=x;}
            }
            circles[k][y]=(struct span){first,last<first?0:last-first+1};
        }
    }
    initialized=true;
}
void reference_render(uint8_t *buffer,int width,int height,int cpp,
                      const struct reference_dot *dots,size_t count)
{
    if(!initialized)initialize();
    fill(buffer,(size_t)width*height,0x0b1020,cpp);
    for(size_t i=0;i<count;i++) {
        int size=dots[i].size;
        if(size<14 || size>44 || (size-14)%10)continue;
        int k=(size-14)/10;
        for(int row=0;row<size;row++) {
            int y=dots[i].y+row;if(y<0 || y>=height)continue;
            struct span span=circles[k][row];
            int left=dots[i].x+span.left,right=left+span.length;
            if(left<0)left=0;
            if(right>width)right=width;
            if(right>left)fill(buffer+((size_t)y*width+left)*cpp,right-left,dots[i].rgb,cpp);
        }
    }
}
