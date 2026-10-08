# Offline HDMI candidate shortlist

These are ranked experiments, not predicted acceptance percentages. The bench was not changed.

Monitor: **SB272**, EDID1.3. Source: 320×240, unscaled. Target: 60±0.15 Hz.

## Known working controls

| Canvas | Hz | RGB888 KiB | Bytes vs848×480 | Source height filled | Evidence |
|---|---:|---:|---:|---:|---|
| 684×384 | 60.069 | 769.5 | 64.5% | 62.5% | Exact timing passed visual review on this monitor |
| 848×480 | 60.069 | 1192.5 | 100.0% | 50.0% | Exact timing passed visual review on this monitor |

## Most conservative untested candidates

| Canvas | Hz | RGB888 KiB | Bytes vs848×480 | Source height filled | Evidence |
|---|---:|---:|---:|---:|---|
| 712×400 | 60.069 | 834.4 | 70.0% | 60.0% | Untested: between working canvas sizes in the same timing family |
| 768×432 | 60.069 | 972.0 | 81.5% | 55.6% | Untested: between working canvas sizes in the same timing family |
| 852×480 | 60.069 | 1198.1 | 100.5% | 50.0% | Untested: extrapolation beyond working sizes |
| 640×360 | 60.069 | 675.0 | 56.6% | 66.7% | Untested: extrapolation beyond working sizes |
| 568×320 | 60.069 | 532.5 | 44.7% | 75.0% | Untested: extrapolation beyond working sizes |

## Untested candidates smaller than the smallest working control

| Canvas | Hz | RGB888 KiB | Bytes vs848×480 | Source height filled | Evidence |
|---|---:|---:|---:|---:|---|
| 640×360 | 60.069 | 675.0 | 56.6% | 66.7% | Untested: extrapolation beyond working sizes |
| 568×320 | 60.069 | 532.5 | 44.7% | 75.0% | Untested: extrapolation beyond working sizes |
| 512×288 | 60.069 | 432.0 | 36.2% | 83.3% | Untested: extrapolation beyond working sizes |
| 484×272 | 60.069 | 385.7 | 32.3% | 88.2% | Untested: extrapolation beyond working sizes |
| 456×256 | 60.069 | 342.0 | 28.7% | 93.8% | Untested: extrapolation beyond working sizes |

## Retained failed attempts

| Probe | Calculated Hz | Disposition |
|---|---:|---|
| 428x240-known-clock | 60.069 | Exact visual failure; do not repeat unchanged |
| 428x240-centered | 60.069 | Exact visual failure; do not repeat unchanged |
| 428x240-lowclock | 59.976 | Exact visual failure; do not repeat unchanged |
| 428x240-shortblank | 98.904 | Outside requested application cadence band |

Frequency/packet checks passing does not establish monitor acceptance. Smaller canvases retain black margins around the unscaled source; bytes saved are not a promised speed improvement.

- Partial EDID decoder: CTA VIC IDs retained but not expanded; vendor/DisplayID/GTF/CVT mode generation not implemented
- Framebuffer size and one-read payload are arithmetic estimates, not measured memory bandwidth or rendering time; exclude blanking, copies and sprites.
- DSI capacity check omits PHY transitions and other packet scheduling overhead.
- Proposed geometries need a separately reviewed pattern/build/physical test. No firmware selection or monitor settings changed.

Exact porches/clocks, retained failures and exclusions are in the JSON report.
