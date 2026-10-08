#!/usr/bin/env python3
"""Rank offline HDMI experiments; never probe, flash, or configure a display.

HDMI-002/N02: an explicit heuristic, NOT a probability of monitor acceptance.
Candidates reuse the measured PLL240/7, two480Mbps lanes,1104x517 family.
EDID parsing is deliberately partial (base timings/ranges plus CTA DTDs/VIC IDs).
Unexpanded extension data is reported, never treated as proof of non-support.
Byte layouts: Linux include/drm/drm_edid.h; transport bounds: pinned IDF5.5.5
hw_ver1 MIPI host/bridge registers and our unchanged LT8912B component.
"""
import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OBSERVATIONS = ROOT / 'docs/tasks/HDMI-002/TIMING-OBSERVATIONS.json'
TIMING_KEYS = ('width', 'height', 'hfp', 'hs', 'hbp', 'vfp', 'vs', 'vbp',
               'htotal', 'vtotal', 'pll_hz', 'divider', 'lanes', 'lane_mbps',
               'h_positive', 'v_positive', 'vic', 'wide')


def parse_edid(raw):
    if len(raw) < 128 or raw[:8] != b'\x00\xff\xff\xff\xff\xff\xff\x00':
        raise ValueError('Missing EDID header/base block')
    if len(raw) != 128 * (1 + raw[126]):
        raise ValueError('EDID length does not match its extension count')
    if any(sum(raw[i:i+128]) % 256 for i in range(0, len(raw), 128)):
        raise ValueError('EDID checksum failure')
    if raw[18] != 1 or raw[19] not in (3, 4):
        raise ValueError('This focused decoder supports EDID1.3/1.4 only')
    result = dict(sha256=hashlib.sha256(raw).hexdigest(), version=f'1.{raw[19]}',
                  model='unspecified', ranges=None, detailed_timings=[],
                  geometry_hints=[], cta_vics=[], warnings=[])
    # No serial/manufacture identifiers are emitted into reports.
    def descriptor(d):
        clock = int.from_bytes(d[:2], 'little') * 10000
        if clock:
            w, hb = d[2] + (d[4] >> 4)*256, d[3] + (d[4] & 15)*256
            h, vb = d[5] + (d[7] >> 4)*256, d[6] + (d[7] & 15)*256
            if not w or not h or not hb or not vb:
                raise ValueError('Invalid EDID detailed timing dimensions')
            result['detailed_timings'].append(dict(
                width=w, height=h, htotal=w+hb, vtotal=h+vb,
                pixel_hz=clock, refresh_hz=clock/((w+hb)*(h+vb)),
                interlaced=bool(d[17] & 128)))
        elif d[:3] == b'\0\0\0' and d[3] == 0xfc:
            result['model'] = d[5:18].decode('ascii', errors='replace').strip()
        elif d[:3] == b'\0\0\0' and d[3] == 0xfd:
            if result['ranges'] is not None:
                raise ValueError('Multiple range descriptors require explicit review')
            offsets = d[4] if raw[19] == 4 else 0
            lo_v, hi_v, lo_h, hi_h = [d[5+i] + (255 if offsets & (1 << i) else 0)
                                     for i in range(4)]
            if not 0 < lo_v <= hi_v or not 0 < lo_h <= hi_h:
                raise ValueError('Invalid EDID frequency range')
            pixel_max = d[9] * 10000000 if d[9] not in (0, 255) else None
            # EDID1.4 CVT refines the rounded maximum pixel clock in0.25MHz units.
            if pixel_max is not None and raw[19] == 4 and d[10] == 4:
                pixel_max -= (d[12] >> 2) * 250000
            result['ranges'] = dict(v_min_hz=lo_v, v_max_hz=hi_v,
                                    h_min_khz=lo_h, h_max_khz=hi_h,
                                    pixel_max_hz=pixel_max)
    for i in range(54, 126, 18):
        descriptor(raw[i:i+18])
    for i in range(38, 54, 2):
        a, b = raw[i:i+2]
        if (a, b) == (1, 1) or not a:
            continue
        w = (a+31)*8
        num, den = ((16, 10), (4, 3), (5, 4), (16, 9))[b >> 6]
        result['geometry_hints'].append([w, w*den//num, 60+(b & 63)])
    # Established timings are geometry/rate hints, not exact porch contracts.
    established = [
        (35, 7, 720, 400, 70), (35, 6, 720, 400, 88),
        (35, 5, 640, 480, 60), (35, 4, 640, 480, 67),
        (35, 3, 640, 480, 72), (35, 2, 640, 480, 75),
        (35, 1, 800, 600, 56), (35, 0, 800, 600, 60),
        (36, 7, 800, 600, 72), (36, 6, 800, 600, 75),
        (36, 5, 832, 624, 75), (36, 3, 1024, 768, 60),
        (36, 2, 1024, 768, 70), (36, 1, 1024, 768, 75),
        (36, 0, 1280, 1024, 75), (37, 7, 1152, 870, 75)]
    for byte, bit, w, h, hz in established:
        if raw[byte] & (1 << bit):
            result['geometry_hints'].append([w, h, hz])
    for offset in range(128, len(raw), 128):
        block = raw[offset:offset+128]
        if block[0] != 2:
            result['warnings'].append(f'Extension type0x{block[0]:02x} not decoded')
            continue
        end = block[2]
        if end == 0:
            continue
        if not 4 <= end <= 127:
            raise ValueError('Invalid CTA data/DTD boundary')
        pos = 4
        while pos < end:
            tag, length = block[pos] >> 5, block[pos] & 31
            if pos+1+length > end:
                raise ValueError('CTA data block crosses DTD boundary')
            if tag == 2:
                # Bit7 means native only for the original VIC1..64 range.
                # Extended VIC193+ must not be folded back to65+.
                result['cta_vics'].extend((v & 127) if (1 <= v <= 64 or 129 <= v <= 192)
                                         else v for v in block[pos+1:pos+1+length])
            pos += 1+length
        for pos in range(end, 110, 18):
            if int.from_bytes(block[pos:pos+2], 'little'):
                descriptor(block[pos:pos+18])
    if result['ranges'] is None:
        result['warnings'].append('No monitor range descriptor: frequency acceptance unknown')
    result['warnings'].append('Partial EDID decoder: CTA VIC IDs retained but not expanded; '
                              'vendor/DisplayID/GTF/CVT mode generation not implemented')
    return result


def normalized(t):
    return {**t, 'h_positive': t.get('h_positive', True),
            'v_positive': t.get('v_positive', True)}


def timing_key(t):
    return tuple(normalized(t)[k] for k in TIMING_KEYS)


def candidates(heights):
    # Hold the complete tested848/684 clock, link, totals and sync widths fixed.
    # Width rounds to4 so every H interval has integral1.75 lane byte clocks.
    for h in heights:
        w = 4 * ((4*h + 4)//9)  # nearest multiple4 to16*h/9, integer arithmetic
        yield dict(name=f'{w}x{h}-known-clock', width=w, height=h, wide=True,
                   hfp=1104-w-224, hs=112, hbp=112, vfp=517-h-31, vs=8, vbp=23,
                   htotal=1104, vtotal=517, pll_hz=240000000, divider=7,
                   lanes=2, lane_mbps=480, h_positive=True, v_positive=True, vic=0)


def check(t, edid, source, refresh, tolerance, min_h_khz):
    errors = []
    if any(not isinstance(t[k], int) or isinstance(t[k], bool) or t[k] <= 0 for k in
           ('width', 'height', 'hfp', 'hs', 'hbp', 'vfp', 'vs', 'vbp', 'htotal',
            'vtotal', 'pll_hz', 'divider', 'lanes', 'lane_mbps')):
        return ['Timing dimensions, clock and intervals must be positive integers'], {}
    if sum(t[k] for k in ('width', 'hfp', 'hs', 'hbp')) != t['htotal'] or \
       sum(t[k] for k in ('height', 'vfp', 'vs', 'vbp')) != t['vtotal']:
        errors.append('Active/porch totals disagree')
    if max(t['htotal'], t['vtotal'], t['width'], t['height']) > 4095:
        errors.append('P4 bridge12-bit timing field overflow')
    if max(t['hs'], t['vs']) > 255:
        errors.append('LT8912B8-bit sync field overflow')
    if max(t['vfp'], t['vbp']) > 1023:
        errors.append('DSI10-bit vertical porch field overflow')
    clock = Fraction(t['pll_hz'], t['divider'])
    ratio = Fraction(t['lane_mbps']*1000000, 8) / clock
    byte_intervals = {k: t[k]*ratio for k in ('width', 'hfp', 'hs', 'hbp', 'htotal')}
    if any(v.denominator != 1 for v in byte_intervals.values()):
        errors.append('DSI lane byte-clock rounding would change the requested timing')
    if byte_intervals['hs'] > 4095 or byte_intervals['hbp'] > 4095 or byte_intervals['htotal'] > 32767:
        errors.append('DSI horizontal byte-clock field overflow')
    if 3*t['width']+6 > t['lanes']*byte_intervals['width']:
        errors.append('RGB888 line packet does not fit the active-time payload budget')
    if (t['pll_hz'], t['divider'], t['lanes'], t['lane_mbps']) not in \
            ((240000000, 7, 2, 480), (240000000, 9, 2, 480)):
        errors.append('Outside this tool\'s reviewed P4 clock/link profiles')
    hz = float(clock / t['htotal'] / t['vtotal'])
    h_khz = float(clock / t['htotal'] / 1000)
    if abs(hz-refresh) > tolerance:
        errors.append('Outside requested application cadence band')
    if t['width'] < source[0] or t['height'] < source[1]:
        errors.append('Source image would be cropped')
    ranges = edid['ranges']
    if ranges:
        if not ranges['v_min_hz'] <= hz <= ranges['v_max_hz']:
            errors.append('Outside EDID vertical range')
        if not max(ranges['h_min_khz'], min_h_khz) <= h_khz <= ranges['h_max_khz']:
            errors.append('Outside EDID/explicit horizontal range intersection')
        if ranges['pixel_max_hz'] is not None and clock > ranges['pixel_max_hz']:
            errors.append('Exceeds EDID maximum pixel clock')
    elif h_khz < min_h_khz:
        errors.append('Below explicit horizontal minimum')
    bytes_ = t['width']*t['height']*3
    return errors, dict(pixel_mhz=float(clock/1000000), h_khz=h_khz, refresh_hz=hz,
        rgb888_bytes=bytes_, one_read_MB_s=bytes_*hz/1000000,
        bytes_percent_of_848x480=100*bytes_/(848*480*3),
        source_offset=[(t['width']-source[0])//2, (t['height']-source[1])//2],
        source_height_percent=100*source[1]/t['height'])


def rank(edid, observations, heights, source=(320, 240), refresh=60, tolerance=.15, min_h_khz=0):
    warnings = list(edid['warnings'])
    rows = observations['observations']
    if observations['monitor_edid_sha256'] != edid['sha256']:
        warnings.append('Observation EDID fingerprint differs: all historical pass/fail evidence ignored')
        rows = []
    successes = [normalized(o['timing']) for o in rows if o['outcome'] == 'pass']
    failures = [normalized(o['timing']) for o in rows if o['outcome'] == 'fail']
    pool = list(candidates(heights)) + [normalized(o['timing']) for o in rows]
    seen, ranked, excluded = set(), [], []
    for t in pool:
        key = timing_key(t)
        if key in seen:
            continue
        seen.add(key)
        errors, metrics = check(t, edid, source, refresh, tolerance, min_h_khz)
        exact = [o for o in rows if timing_key(o['timing']) == key]
        row = dict(timing=t, metrics=metrics, observed=exact)
        if errors:
            excluded.append({**row, 'reasons': errors})
            continue
        if any(o['outcome'] == 'fail' for o in exact):
            tier, reason = 4, 'Exact timing failed visual review'
        elif any(o['outcome'] == 'pass' for o in exact):
            tier, reason = 0, 'Exact timing passed visual review on this monitor'
        elif any((s['width'], s['height']) == (t['width'], t['height']) for s in failures):
            tier, reason = 3, 'Same active geometry previously failed; this is not proof of impossibility'
        else:
            # Only compare geometry inside the SAME clock, totals, link, sync,
            # polarity and aspect family. Different clock experiments add no confidence.
            family = ('pll_hz', 'divider', 'lanes', 'lane_mbps', 'htotal', 'vtotal',
                      'hs', 'vs', 'hbp', 'vbp', 'h_positive', 'v_positive', 'vic', 'wide')
            anchors = [s for s in successes if all(s[k] == t[k] for k in family)]
            inside = len(anchors) >= 2 and all(
                min(s[k] for s in anchors) <= t[k] <= max(s[k] for s in anchors)
                for k in ('width', 'height'))
            tier, reason = ((1, 'Untested: between working canvas sizes in the same timing family')
                            if inside else (2, 'Untested: extrapolation beyond working sizes'))
            if not anchors:
                reason = 'Untested: no matching timing-family success for this monitor'
        distance = min((abs(t['width']/s['width']-1)+abs(t['height']/s['height']-1)
                        for s in successes), default=math.inf)
        row.update(tier=tier, reason=reason,
                   distance_to_success=distance if math.isfinite(distance) else None,
                   observed=exact)
        row['edid_geometry_hint'] = any(
            (w, h) == (t['width'], t['height']) and abs(rate-metrics['refresh_hz']) < 1
            for w, h, rate in edid['geometry_hints']) or any(
            not d['interlaced'] and (d['width'], d['height']) == (t['width'], t['height'])
            and abs(d['refresh_hz']-metrics['refresh_hz']) < 1 for d in edid['detailed_timings'])
        ranked.append(row)
    # EDID geometry hints are weak tie-breakers; they never imply exact timing support.
    ranked.sort(key=lambda r: (r['tier'], not r['edid_geometry_hint'],
        r['distance_to_success'] if r['distance_to_success'] is not None else math.inf,
        r['metrics']['rgb888_bytes']))
    return dict(schema=1, monitor=edid, source=list(source), requested_hz=refresh,
        tolerance_hz=tolerance, explicit_min_h_khz=min_h_khz, warnings=warnings,
        ranking='Ordinal heuristic: exact pass; geometry interpolation; extrapolation; '
                'failed geometry; exact failure. No probability or guarantee.',
        ranked=ranked, excluded=excluded,
        limits=['Framebuffer size and one-read payload are arithmetic estimates, not measured '
                'memory bandwidth or rendering time; exclude blanking, copies and sprites.',
                'DSI capacity check omits PHY transitions and other packet scheduling overhead.',
                'Proposed geometries need a separately reviewed pattern/build/physical test. '
                'No firmware selection or monitor settings changed.'])


def markdown(report, limit):
    lines = ['# Offline HDMI candidate shortlist', '',
             'These are ranked experiments, not predicted acceptance percentages. '
             'The bench was not changed.', '',
             f"Monitor: **{report['monitor']['model']}**, EDID{report['monitor']['version']}. "
             f"Source: {report['source'][0]}×{report['source'][1]}, unscaled. "
             f"Target: {report['requested_hz']:g}±{report['tolerance_hz']:g} Hz.", '']
    def table(title, rows):
        lines.extend([f'## {title}', '',
            '| Canvas | Hz | RGB888 KiB | Bytes vs848×480 | Source height filled | Evidence |',
            '|---|---:|---:|---:|---:|---|'])
        for r in rows:
            t, m = r['timing'], r['metrics']
            lines.append(f"| {t['width']}×{t['height']} | {m['refresh_hz']:.3f} | "
                f"{m['rgb888_bytes']/1024:.1f} | {m['bytes_percent_of_848x480']:.1f}% | "
                f"{m['source_height_percent']:.1f}% | {r['reason']} |")
        if not rows:
            lines.append('| — | — | — | — | — | No candidates |')
        lines.append('')
    table('Known working controls', [r for r in report['ranked'] if r['tier'] == 0])
    new = [r for r in report['ranked'] if r['tier'] in (1, 2)]
    table('Most conservative untested candidates', new[:limit])
    lowest_working = min((r['metrics']['rgb888_bytes'] for r in report['ranked']
                          if r['tier'] == 0), default=848*480*3)
    table('Untested candidates smaller than the smallest working control',
          [r for r in new if r['metrics']['rgb888_bytes'] < lowest_working][:limit])
    failed = [r for r in report['ranked']+report['excluded']
              if any(o['outcome'] == 'fail' for o in r['observed'])]
    if failed:
        lines.extend(['## Retained failed attempts', '',
                      '| Probe | Calculated Hz | Disposition |', '|---|---:|---|'])
        for r in failed:
            notes = '; '.join(r.get('reasons', [])) or 'Exact visual failure; do not repeat unchanged'
            lines.append(f"| {r['timing']['name']} | {r['metrics']['refresh_hz']:.3f} | {notes} |")
        lines.append('')
    lines.extend(['Frequency/packet checks passing does not establish monitor acceptance. '
                  'Smaller canvases retain black margins around the unscaled source; '
                  'bytes saved are not a promised speed improvement.', ''])
    for note in report['warnings']+report['limits']:
        lines.append('- '+note)
    lines.extend(['', 'Exact porches/clocks, retained failures and exclusions are in the JSON report.'])
    return '\n'.join(lines)+'\n'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--edid', required=True, type=Path)
    p.add_argument('--observations', type=Path, default=DEFAULT_OBSERVATIONS)
    p.add_argument('--heights', default='240,256,272,288,320,360,384,400,432,480')
    p.add_argument('--source', nargs=2, type=int, default=(320, 240), metavar=('WIDTH', 'HEIGHT'))
    p.add_argument('--refresh', type=float, default=60)
    p.add_argument('--tolerance', type=float, default=.15)
    p.add_argument('--min-h-khz', type=float, default=0,
                   help='Optional stricter manufacturer limit, e.g.31 for this Acer')
    p.add_argument('--limit', type=int, default=5)
    p.add_argument('--json', type=Path)
    p.add_argument('--markdown', type=Path)
    a = p.parse_args()
    try:
        heights = [int(s) for s in a.heights.split(',')]
        if not heights or min(heights) <= 0 or min(a.source) <= 0 or a.limit < 1:
            raise ValueError('Positive source dimensions, heights and limit required')
        if not all(math.isfinite(v) for v in (a.refresh, a.tolerance, a.min_h_khz)) or \
                a.refresh <= 0 or a.tolerance < 0 or a.min_h_khz < 0:
            raise ValueError('Invalid cadence/range option')
        report = rank(parse_edid(a.edid.read_bytes()), json.loads(a.observations.read_text()),
                      heights, a.source, a.refresh, a.tolerance, a.min_h_khz)
        report['tool_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        report['observations_sha256'] = hashlib.sha256(a.observations.read_bytes()).hexdigest()
        if a.json:
            a.json.write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
        rendered = markdown(report, a.limit)
        if a.markdown:
            a.markdown.write_text(rendered)
        print(rendered, end='')
    except (OSError, ValueError, KeyError, TypeError) as error:
        p.error(str(error))


if __name__ == '__main__':
    main()
