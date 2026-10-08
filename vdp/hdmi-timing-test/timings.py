"""HDMI-002 native-active experiments; reuse the accepted PLL and line cadence.

These are deliberately custom timings (VIC0), not promised monitor modes. Extra
front porch is blanking, not transmitted black pixels or framebuffer padding.
The LT8912B brief does not establish a low HDMI clock limit; keep the known
working clock rather than extrapolating its separate LVDS specification.
"""
TIMINGS={
 '848x480':(848,480,True),
 '512x384':(512,384,False),
 '684x384':(684,384,True),
 '320x240':(320,240,False),
 '428x240':(428,240,True),
}
def selected(name):
 w,h,wide=TIMINGS[name]
 return dict(name=name,width=w,height=h,wide=wide,hfp=1104-w-224,hs=112,hbp=112,
             vfp=517-h-31,vs=8,vbp=23,htotal=1104,vtotal=517,
             pll_hz=240000000,divider=7,lanes=2,lane_mbps=480,
             refresh_hz=240000000/7/1104/517,vic=0,
             aspect_error_percent=(w/h/(16/9)-1)*100 if wide else 0)
def header(mode):
 return '#pragma once\n'+''.join(f'#define TEST_{k.upper()} {int(mode[k])}\n'
   for k in ('width','height','wide','hfp','hs','hbp','vfp','vs','vbp','htotal','vtotal'))
