#include "pattern.h"

#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint32_t colour(const uint8_t *p, size_t stride, unsigned x, unsigned y)
{
    p += (size_t)y * stride + x * 3;
    return ((uint32_t)p[2] << 16) | ((uint32_t)p[1] << 8) | p[0];
}

static void check(unsigned width, const char *ppm_path)
{
    const unsigned height = 480, left = (width - 512) / 2, top = 48;
    const size_t stride = width * 3 + 13, bytes = stride * height;
    uint8_t *allocation = malloc(bytes + 128);
    assert(allocation);
    memset(allocation, 0xa5, bytes + 128);
    uint8_t *pixels = allocation + 64;
    assert(hdmi_timing_pattern_bgr888(pixels, bytes, stride, width, height));

    for (size_t i = 0; i < 64; ++i) {
        assert(allocation[i] == 0xa5);
        assert(allocation[64 + bytes + i] == 0xa5);
    }
    for (unsigned y = 0; y < height; ++y) {
        assert(colour(pixels, stride, 0, y) == 0xffffff);
        assert(colour(pixels, stride, width - 1, y) == 0xffffff);
        for (size_t i = width * 3; i < stride; ++i)
            assert(pixels[y * stride + i] == 0xa5);
    }
    for (unsigned x = 0; x < width; ++x) {
        assert(colour(pixels, stride, x, 0) == 0xffffff);
        assert(colour(pixels, stride, x, height - 1) == 0xffffff);
    }
    for (unsigned x = left; x < left + 512; ++x) {
        assert(colour(pixels, stride, x, top) == 0xffffff);
        assert(colour(pixels, stride, x, top + 383) == 0xffffff);
    }
    for (unsigned y = top; y < top + 384; ++y) {
        assert(colour(pixels, stride, left, y) == 0xffffff);
        assert(colour(pixels, stride, left + 511, y) == 0xffffff);
        assert(colour(pixels, stride, left - 1, y) == 0);
        assert(colour(pixels, stride, left + 512, y) == 0);
    }
    const uint32_t expected[] = {
        0x000000, 0xff0000, 0x00ff00, 0x0000ff,
        0xffff00, 0xff00ff, 0x00ffff, 0xffffff
    };
    for (unsigned bar = 0; bar < 8; ++bar)
        assert(colour(pixels, stride, left + bar * 64 + 32, top + 100) == expected[bar]);
    assert(colour(pixels, stride, 5, 5) == 0xff0000);
    assert(colour(pixels, stride, width - 5, 5) == 0x00ff00);
    assert(colour(pixels, stride, 5, height - 5) == 0x0000ff);
    assert(colour(pixels, stride, width - 5, height - 5) == 0xffff00);
    assert(colour(pixels, stride, width / 2, 1) == 0xff0000);
    assert(colour(pixels, stride, width / 2, height - 2) == 0x00ffff);
    assert(colour(pixels, stride, left + 16, top + 204) == 0xffffff);
    assert(colour(pixels, stride, left + 17, top + 204) == 0);
    assert(colour(pixels, stride, left + 17, top + 205) == 0xffffff);
    assert(colour(pixels, stride, left + 199, top + 204) == 0xffffff);
    assert(colour(pixels, stride, left + 200, top + 204) == 0);
    assert(colour(pixels, stride, left + 16, top + 312) == 0xffffff);
    assert(colour(pixels, stride, left + 16, top + 313) == 0);
    assert(colour(pixels, stride, left + 208, top + 312) == 0xffffff);
    assert(colour(pixels, stride, left + 209, top + 312) == 0);

    if (ppm_path) {
        FILE *f = fopen(ppm_path, "wb");
        assert(f);
        fprintf(f, "P6\n%u %u\n255\n", width, height);
        for (unsigned y = 0; y < height; ++y)
            for (unsigned x = 0; x < width; ++x) {
                uint32_t rgb = colour(pixels, stride, x, y);
                const uint8_t sample[3] = { rgb >> 16, rgb >> 8, rgb };
                assert(fwrite(sample, 1, 3, f) == 3);
            }
        assert(fclose(f) == 0);
    }
    free(allocation);
}

int main(int argc, char **argv)
{
    uint8_t too_small[16];
    memset(too_small, 0xa5, sizeof too_small);
    assert(!hdmi_timing_pattern_bgr888(NULL, SIZE_MAX, 848 * 3, 848, 480));
    assert(!hdmi_timing_pattern_bgr888(too_small, sizeof too_small, 848 * 3, 848, 480));
    assert(!hdmi_timing_pattern_bgr888(too_small, SIZE_MAX, SIZE_MAX, 848, 480));
    assert(!hdmi_timing_pattern_bgr888(too_small, SIZE_MAX, 848, 848, 480));
    assert(!hdmi_timing_pattern_bgr888(too_small, SIZE_MAX, SIZE_MAX, UINT32_MAX, 480));
    assert(!hdmi_timing_pattern_bgr888(too_small, SIZE_MAX, 640 * 3, 639, 480));
    assert(!hdmi_timing_pattern_bgr888(too_small, SIZE_MAX, 848 * 3, 848, 479));
    for (unsigned i = 0; i < sizeof too_small; ++i)
        assert(too_small[i] == 0xa5);
    check(848, argc > 1 ? argv[1] : NULL);
    check(640, NULL);
    const unsigned geometries[][2]={{512,384},{684,384},{320,240},{428,240}};
    const uint32_t bars[]={0,0xff0000,0x00ff00,0x0000ff,0xffff00,0xff00ff,0x00ffff,0xffffff};
    for(unsigned n=0;n<4;++n) {
        unsigned w=geometries[n][0],h=geometries[n][1];size_t stride=w*3+7,bytes=stride*h;
        unsigned iw=(w==684?512:w==428?320:w),left=(w-iw)/2;
        uint8_t *p=malloc(bytes+64);assert(p);memset(p,0xa5,bytes+64);
        assert(hdmi_timing_pattern_bgr888(p,bytes,stride,w,h));
        for(unsigned y=0;y<h;++y) {
            assert(colour(p,stride,0,y)==0xffffff && colour(p,stride,w-1,y)==0xffffff);
            for(size_t x=w*3;x<stride;++x)assert(p[y*stride+x]==0xa5);
        }
        for(unsigned x=0;x<w;++x)assert(colour(p,stride,x,0)==0xffffff && colour(p,stride,x,h-1)==0xffffff);
        for(unsigned y=1;y<h-1;++y) {
            assert(colour(p,stride,left,y)==0xffffff);
            assert(colour(p,stride,left+iw-1,y)==0xffffff);
            for(unsigned x=1;x<left;++x)assert(colour(p,stride,x,y)==0);
            for(unsigned x=left+iw;x<w-1;++x)assert(colour(p,stride,x,y)==0);
        }
        for(unsigned i=0;i<8;++i) {
            unsigned begin=1+i*(iw-2)/8,end=1+(i+1)*(iw-2)/8;
            assert(colour(p,stride,left+(begin+end)/2,60)==bars[i]);
            // Every label must occupy the middle six columns of its own bar.
            // This detects the previous constant-spacing label regression.
            unsigned label=begin+(end-begin-6)/2,lit=0;
            for(unsigned y=28;y<36;++y)for(unsigned x=begin;x<end;++x) {
                uint32_t c=colour(p,stride,left+x,y);
                if(x<label || x>=label+6)assert(c==0);
                else if(c==0xffffff)++lit;
            }
            assert(lit>0);
        }
        for(unsigned i=0;i<64;++i)assert(p[bytes+i]==0xa5);
        free(p);
    }
    puts("PASS: BGR channels, 512x384 margins, edges, checkers, stride padding and canaries");
    return 0;
}
