"""HDMI-002 native-active experiments using the supported PLL240 source.

These are deliberately custom timings (VIC0), not promised monitor modes. Extra
front porch is blanking, not transmitted black pixels or framebuffer padding.
The LT8912B brief does not establish a low HDMI clock limit. Most probes retain
the working divider; the named lowclock probe deliberately tests another divider
without extrapolating the separate LVDS specification.
"""
TIMINGS={
 '848x480':(848,480,True),
 '512x384':(512,384,False),
 '684x384':(684,384,True),
 '320x240':(320,240,False),
 '428x240':(428,240,True),
 '428x240-centered':(428,240,True),
 '428x240-lowclock':(428,240,True),
 '428x240-shortblank':(428,240,True),
}
def selected(name):
 w,h,wide=TIMINGS[name]
 mode = dict(name=name,width=w,height=h,wide=wide,hfp=1104-w-224,hs=112,hbp=112,
             vfp=517-h-31,vs=8,vbp=23,htotal=1104,vtotal=517,
             pll_hz=240000000,divider=7,lanes=2,lane_mbps=480,
             refresh_hz=240000000/7/1104/517,vic=0,
             aspect_error_percent=(w/h/(16/9)-1)*100 if wide else 0)
 if name == '428x240-centered':
  # N01: preserve the proven clock/totals; isolate extreme front-porch placement.
  # Blanking is not framebuffer storage and costs no render/scale pass.
  mode.update(hfp=280,hbp=284,vfp=134,vbp=135)
 if name == '428x240-lowclock':
  # Acer N01 second probe: supported PLL240/9, >25MHz TMDS, >31kHz line.
  # All H fields are multiples of4: 480Mbps DSI has2.25 byteclocks/pixel.
  mode.update(hfp=176,hs=80,hbp=176,htotal=860,vfp=134,vbp=135,divider=9)
  mode['refresh_hz'] = mode['pll_hz']/mode['divider']/mode['htotal']/mode['vtotal']
 if name == '428x240-shortblank':
  # N01 final standalone probe: retain known PLL/link/line cadence, shorten
  # blanking from277 to74 lines. This is98.904Hz, NOT a60Hz application mode.
  mode.update(hfp=280,hbp=284,vfp=33,vbp=33,vtotal=314)
  mode['refresh_hz'] = mode['pll_hz']/mode['divider']/mode['htotal']/mode['vtotal']
 return mode

def header(mode):
 return '#pragma once\n'+''.join(f'#define TEST_{k.upper()} {int(mode[k])}\n'
   for k in ('width','height','wide','hfp','hs','hbp','vfp','vs','vbp','htotal','vtotal','divider','lane_mbps'))
