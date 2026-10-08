# Offline HDMI candidate ranking

The experimental [host script](../../scripts/hdmi_candidates.py) proposes a short
list of unscaled HDMI canvases using monitor EDID, exact visual observations and
the reviewed P4/LT8912B timing constraints. It ranks experiments; it does **not**
predict a percentage likelihood, prove monitor compatibility or change hardware.

## Running it

From the repository root, using a previously saved binary EDID:

```sh
.venv/bin/python scripts/hdmi_candidates.py \
  --edid /path/to/monitor.edid \
  --min-h-khz 31 \
  --json /tmp/hdmi-candidates.json \
  --markdown /tmp/hdmi-candidates.md
```

The optional31kHz floor is the Acer SB272 E manufacturer's specification; omit it
or supply the appropriate value for another monitor. The script intersects it
with the EDID range. Default source is320×240, target60±0.15Hz, and candidate
heights are240,256,272,288,320,360,384,400,432,480. `--source WIDTH HEIGHT`,
`--heights` (comma-separated) and `--limit` adjust the bounded report.

The tool reads local files only. It neither connects to the monitor nor invokes
SSH, flashing, a build, a mode change or a reset. Raw EDID may contain a device
serial; keep it in an ignored local record. Reports omit that serial and retain
an input hash for reproducibility. JSON additionally records script/observation
hashes and every proposed timing field.

## Ranking rules

1. **Exact visual passes** lead the report. Resolution alone is insufficient:
   porches, sync polarity, clock/divider, lane configuration and HDMI metadata
   must match the observation. The tested848×480 remains distinct from the
   generated852×480 nearest16:9 geometry.
2. **Untested interpolation** between working canvas sizes follows. It reuses
   the same clocks, totals, sync widths/back porches and metadata. Front porches
   absorb the changed active dimensions without storing additional pixels.
3. **Untested extrapolation** beyond the working sizes follows, with nearer
   geometries first. This is a transparent heuristic, not a measured relationship
   between geometry distance and acceptance. A separate table selects the smaller
   candidates useful for reducing framebuffer work.
4. **Failed geometries and exact failed timings** remain explicit. A failure
   does not prove the resolution impossible. A failed98.9Hz trial remains in the
   evidence even when excluded from the requested60Hz band.

Observations default to the bounded [HDMI timing evidence](../tasks/HDMI-002/TIMING-OBSERVATIONS.json).
An EDID fingerprint mismatch discards those pass/fail assertions and explains why;
observations do not silently transfer to another monitor. This collection is
experimental evidence, not a production mode list.

## Checks and limits

The tool validates all EDID block checksums, version and extension lengths. It
decodes base frequency ranges, established/standard geometry hints and detailed
timings, plus CTA detailed timings and raw VIC IDs. Other extensions, vendor
blocks and full GTF/CVT mode generation are outside this decoder. Missing range
data remains unknown. An advertised geometry is only a weak hint, not an exact
clock/porch match or a guarantee about custom modes.

Candidate generation deliberately reuses PLL240/7, two480Mbps DSI lanes,
1104×517 totals and positive syncs. It does not search arbitrary PLL settings.
The checker rejects bad totals, relevant P4/bridge register overflows,
non-integral DSI lane-byte intervals, inadequate RGB888 packet payload capacity,
source cropping, out-of-band cadence and known monitor-range violations. Packet
capacity is a limited arithmetic check: PHY transitions and full scheduling
behavior remain unmodelled. The tool does not establish a minimum HDMI clock or
minimum active size that the bridge/monitor documentation does not provide.

RGB888 size means **one active framebuffer**; the one-read payload estimate
means one full traversal per calculated scanout. Neither is a measurement of
total RAM, bandwidth or execution time. Double buffers, copies, cache behavior,
sprites and the renderer's actual access pattern are separate costs. With no
pixel scaling, a320×240 image occupies only part of any taller/wider canvas;
the remaining active area is black. Less framebuffer storage does not promise
the same percentage speed improvement.

Proposed dimensions still require fixture/firmware implementation and physical
picture review. The tool does not allocate VDU modes or select production builds.

## Validation and sources

Run `.venv/bin/python tests/hdmi_candidates_test.py`. Synthetic EDID checks cover
corrupt/truncated blocks, CTA boundaries/extended IDs, EDID1.4 range offsets and
unspecified/refined maximum clocks. Timing tests cover independent known values,
field/packet/rounding failures, exact observation matching and wrong-monitor
evidence rejection. The local Acer capture was also exercised separately.

Byte layouts were checked against Linux's
[EDID structures](https://github.com/torvalds/linux/blob/master/include/drm/drm_edid.h)
and [decoder](https://github.com/torvalds/linux/blob/master/drivers/gpu/drm/drm_edid.c).
P4 constraints come from pinned IDF5.5.5 commit
`b774170ff46c393eeb5e495ea37936038d3f4f4f`: `components/hal/mipi_dsi_hal.c`,
`components/esp_lcd/dsi/esp_lcd_panel_dpi.c`, and the
`components/soc/esp32p4/register/hw_ver1/soc/` MIPI host/bridge register headers.
The maintained [LT8912B component](../../vdp/components/esp_lcd_lt8912b/UPSTREAM.json)
identifies its upstream source. The
[task](../tasks/HDMI-002.md) owns physical follow-up and the
[generated shortlist](../tasks/HDMI-002/CANDIDATE-RANKING.md) records this run.
