// HDMI-002: explicit output timings; no logical VDP mode change or scaling.
// The smaller signal is custom near60Hz, not exact VESA DMT0Eh. PLL240/7
// and two480Mbps lanes give integer DSI horizontal fields and zero IDF porch
// compensation. Avoid the unsupported/suspect DPI APLL mux on P4 silicon1.3.
#pragma once
namespace agon::extender::display {
struct HdmiTiming {
  int width, height;
  float pixel_mhz;
  unsigned lane_mbps;
  int h_front, h_sync, h_back, v_front, v_sync, v_back;
  bool h_positive, v_positive;
  unsigned vic;
  constexpr int hTotal() const { return width+h_front+h_sync+h_back; }
  constexpr int vTotal() const { return height+v_front+v_sync+v_back; }
  constexpr double refreshHz() const { return double(pixel_mhz)*1000000/(hTotal()*vTotal()); }
};
inline constexpr HdmiTiming kHdmi684{684,384,240.0f/7.0f,480,196,112,112,102,8,23,true,true,0};
inline constexpr HdmiTiming kHdmi848{848,480,240.0f/7.0f,480,32,112,112,6,8,23,true,true,0};
// HDMI02-R: only proven carriers. Smaller modes remain unscaled; no new
// 240-line signal is implied. Larger modes retain the documented crop fallback.
inline constexpr HdmiTiming selectHdmiTiming(int width, int height) {
  return width > 0 && height > 0 && width <= 684 && height <= 384 ? kHdmi684 : kHdmi848;
}
#if (defined(AGON_EXTENDER_HDMI_AUTO) + defined(AGON_EXTENDER_HDMI_512X384) + defined(AGON_EXTENDER_HDMI_848X480) + defined(AGON_EXTENDER_HDMI_684X384)) > 1
#error Select only one experimental HDMI timing
#endif
#ifdef AGON_EXTENDER_HDMI_AUTO
inline constexpr HdmiTiming kHdmiTiming = kHdmi848; // startup mode0 fits
#elif defined(AGON_EXTENDER_HDMI_512X384)
// Native active geometry; extra porch is blanking, not stored black pixels.
// Matches HDMI-002's standalone pattern. Monitor acceptance is still required.
inline constexpr HdmiTiming kHdmiTiming{512,384,240.0f/7.0f,480,368,112,112,102,8,23,true,true,0};
#elif defined(AGON_EXTENDER_HDMI_684X384)
// HDMI-002 visually verified wide carrier;512x384 games sit at(86,0).
inline constexpr HdmiTiming kHdmiTiming{684,384,240.0f/7.0f,480,196,112,112,102,8,23,true,true,0};
#elif defined(AGON_EXTENDER_HDMI_848X480)
inline constexpr HdmiTiming kHdmiTiming{848,480,240.0f/7.0f,480,32,112,112,6,8,23,true,true,0};
#else
// Existing visually accepted720p clock/porches and metadata are unchanged.
inline constexpr HdmiTiming kHdmiTiming{1280,720,60,720,10,32,28,3,5,13,true,false,4};
#endif
} // namespace agon::extender::display
