#!/usr/bin/env python3
"""Offline UART/CTS attribution. No board access or claim of pure CPU cost.

Sampling-derived frame ends have approximately one-sample uncertainty. A byte
already in flight may finish after CTS rises; report this, never assert that
CTS must remain low throughout a byte. Validate bytes independently with
sigrok before trusting the gap partition. numpy is required on the host.
"""
import argparse
import bisect
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import zipfile
import numpy as np
from capture_trace import RATE, SAMPLES, metadata, sha

BAUD = 1_152_000
BIT = RATE/BAUD
MARKER = bytes([23, 0, 132, 200, 0, 144, 1])
TARGET = bytes([23, 0, 132, 64, 0, 24, 0])
PAYLOAD = b''.join(bytes([25, 69, x, 0, 24, 0, 0, 0]) for x in range(8, 65, 8))*512


def transitions(raw, pin):
    chunks = []
    for start in range(1, len(raw), 4_000_000):
        end = min(len(raw), start+4_000_000)
        chunks.append(np.flatnonzero((raw[start:end] ^ raw[start-1:end-1]) & (1 << pin))+start)
    return np.concatenate(chunks) if chunks else np.array([], dtype=np.int64)


def decode(raw, pin):
    edges = transitions(raw, pin)
    falling = edges[(raw[edges] & (1 << pin)) == 0]
    frames, errors, resume = [], [], 0
    for edge in falling:
        start = int(edge)
        if start < resume: continue
        positions = np.rint(start+(np.arange(10)+.5)*BIT).astype(np.int64)
        if positions[-1] >= len(raw):
            errors.append(start); break
        levels = (raw[positions] >> pin) & 1
        if levels[0] != 0 or levels[-1] != 1:
            errors.append(start)
        else:
            value = sum(int(levels[i+1]) << i for i in range(8))
            frames.append(dict(start=start, end=start+10*BIT, byte=value))
        resume = start+9.75*BIT
    return frames, errors


def high_intervals(raw, pin):
    edges = transitions(raw, pin)
    bounds = [0, *edges.tolist(), len(raw)]
    return [(a, b) for a, b in zip(bounds, bounds[1:]) if int(raw[a]) & (1 << pin)]


def overlap(left, right):
    """Intersection of two ordered, internally disjoint interval lists."""
    i = j = 0; total = 0.
    while i < len(left) and j < len(right):
        a, b = left[i]; c, d = right[j]
        total += max(0., min(b, d)-max(a, c))
        if b <= d: i += 1
        else: j += 1
    return total


def gap_metrics(frames, blocked):
    gaps = [(a['end'], b['start']) for a, b in zip(frames, frames[1:]) if b['start'] > a['end']]
    idle = sum(b-a for a, b in gaps)
    high = overlap(gaps, blocked)
    span = frames[-1]['end']-frames[0]['start']
    longest = sorted(gaps, key=lambda p: p[1]-p[0], reverse=True)[:10]
    return dict(wire_span_seconds=span/RATE, estimated_byte_time_seconds=(span-idle)/RATE,
                idle_seconds=idle/RATE, idle_cts_high_seconds=high/RATE,
                idle_cts_low_seconds=(idle-high)/RATE,
                cts_high_seconds=overlap([(frames[0]['start'], frames[-1]['end'])], blocked)/RATE,
                idle_cts_high_fraction=high/idle if idle else 0.,
                longest_gaps=[dict(start_seconds=a/RATE, duration_seconds=(b-a)/RATE,
                                   cts_high_seconds=overlap([(a,b)], blocked)/RATE) for a,b in longest])


def pixel_reply(frames, after, before, expected):
    selected = [f for f in frames if f['start'] >= after and f['end'] <= before]
    packets = []; i = 0
    while i < len(selected):
        if i+2 > len(selected) or selected[i]['byte'] < 0x80:
            raise ValueError('Malformed return packet in query window')
        end = i+2+selected[i+1]['byte']
        if end > len(selected): raise ValueError('Truncated return packet in query window')
        part = selected[i:end]
        if part[0]['byte'] == 0x84: packets.append(part)
        i = end
    if len(packets) != 1 or bytes(f['byte'] for f in packets[0]) != bytes([0x84,4])+expected:
        raise ValueError('Expected exactly one correctly coloured pixel reply in query window')
    return packets[0]


def boundaries(forward, reverse):
    data = bytes(f['byte'] for f in forward)
    positions = [m.start() for m in re.finditer(re.escape(MARKER), data)]
    if len(positions) != 1: raise ValueError('Expected one unique complete trace marker')
    m = positions[0]; p = m+len(MARKER); q = p+len(PAYLOAD); end = q+len(TARGET)
    if data[p:end] != PAYLOAD+TARGET:
        raise ValueError('Missing, extra or corrupt counted-point payload/final query')
    marker = forward[m:p]; payload = forward[p:q]; query = forward[q:end]
    initial = pixel_reply(reverse, marker[-1]['end'], payload[0]['start'], bytes(4))
    # The fixture resumes ordinary output only after this reply. Bound by that
    # next forward byte when present; otherwise capture end is checked by caller.
    upper = forward[end]['start'] if end < len(forward) else float('inf')
    reply = pixel_reply(reverse, query[-1]['end'], upper, bytes([255,255,255,15]))
    return marker, initial, payload, query, reply


def independent_decode(trace, out, pin, frames, begin, end):
    args = ['sigrok-cli', '--input-file', str(trace), '--protocol-decoders',
            f'uart:rx=D{pin}:baudrate={BAUD}:data_bits=8:parity=none:stop_bits=1:format=hex',
            '--protocol-decoder-samplenum', '--protocol-decoder-annotations',
            'uart=rx-data:rx-warnings:rx-parity-err:rx-break']
    (out/f'decoder-D{pin}-command.json').write_text(json.dumps(args)+'\n')
    with (out/f'decoder-D{pin}.txt').open('w') as log, (out/f'decoder-D{pin}.stderr').open('w') as err:
        subprocess.run(args, stdout=log, stderr=err, check=True, timeout=180)
    parsed = []
    for line in (out/f'decoder-D{pin}.txt').read_text().splitlines():
        match = re.fullmatch(r'(\d+)-(\d+) uart-\d+: (.*)', line)
        if not match: raise ValueError('Unexpected sigrok annotation: '+line)
        a, b = int(match[1]), int(match[2])
        if b < begin or a >= end: continue
        if not re.fullmatch('[0-9a-fA-F]{2}', match[3]):
            raise ValueError('Sigrok warning in measured window: '+line)
        parsed.append((a,b,int(match[3],16)))
    expected = [f for f in frames if f['start'] >= begin and f['end'] <= end]
    if len(parsed) != len(expected): raise ValueError('Independent decoder frame count differs')
    for (a,b,value), f in zip(parsed, expected):
        if value != f['byte'] or not f['start'] <= a <= b <= f['end']+1:
            raise ValueError('Independent decoder byte/timestamp disagreement')


def analyze(raw):
    forward, ferr = decode(raw, 1); reverse, rerr = decode(raw, 6)
    marker, initial, payload, query, reply = boundaries(forward, reverse)
    begin, end = marker[0]['start'], reply[-1]['end']
    if end+BIT >= len(raw): raise ValueError('No complete capture tail after final reply')
    if any(begin <= p < end for p in ferr+rerr): raise ValueError('UART framing error in measured window')
    blocked = high_intervals(raw, 4)  # P4 RTS -> eZ80 CTS, high withholds permission.
    reverse_blocked = high_intervals(raw, 3)
    record = dict(coverage_pass=True, forward_payload_bytes=len(payload),
                  marker_start_seconds=begin/RATE, final_reply_end_seconds=end/RATE,
                  marker_reply_seconds=(initial[-1]['end']-marker[-1]['end'])/RATE,
                  marker_reply_to_first_payload_seconds=(payload[0]['start']-initial[-1]['end'])/RATE,
                  payload_end_to_query_seconds=(query[0]['start']-payload[-1]['end'])/RATE,
                  final_query_reply_seconds=(reply[-1]['end']-query[-1]['end'])/RATE,
                  final_query_to_first_reply_seconds=(reply[0]['start']-query[-1]['end'])/RATE,
                  final_query_to_first_reply_agon_rts_high_seconds=overlap(
                      [(query[-1]['end'], reply[0]['start'])], reverse_blocked)/RATE,
                  final_query_through_reply_agon_rts_high_seconds=overlap(
                      [(query[-1]['end'], reply[-1]['end'])], reverse_blocked)/RATE,
                  payload_start_to_reply_seconds=(end-payload[0]['start'])/RATE,
                  payload=gap_metrics(payload, blocked),
                  final_reply=gap_metrics(reply, reverse_blocked),
                  framing_errors_outside_window=len(ferr)+len(rerr),
                  byte_starts_while_cts_high=sum(bool(int(raw[f['start']]) & 16) for f in payload),
                  final_reply_starts_while_agon_rts_high=sum(bool(int(raw[f['start']]) & 8) for f in reply),
                  limits='CTS overlap is not pure CPU stall time; CTS-low gaps do not identify their software cause. '
                         'Frame ends have approximately one-sample uncertainty; in-flight bytes may finish after CTS rises.')
    return record, forward, reverse, begin, end


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('trace', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    result = dict(coverage_pass=False, acquisition_pass=False, independent_decode_matches=False,
                  trace_sha256=sha(args.trace), analysis_sha256=sha(__file__), numpy_version=np.__version__)
    try:
        with tempfile.TemporaryDirectory(prefix='uart-raw-', dir=args.output) as tmp:
            path = Path(tmp)/'logic.raw'
            with zipfile.ZipFile(args.trace) as archive, path.open('wb') as stream:
                names, count = metadata(archive)
                for name in names:
                    with archive.open(name) as source: shutil.copyfileobj(source, stream, 4_000_000)
            result.update(samples=count, sample_rate_hz=RATE, uart_baud=BAUD,
                          acquisition_pass=count == SAMPLES)
            raw = np.memmap(path, dtype=np.uint8, mode='r')
            record, forward, reverse, begin, end = analyze(raw)
            del raw
            for pin, frames in ((1, forward), (6, reverse)):
                independent_decode(args.trace, args.output, pin, frames, begin, end)
            result.update(record, independent_decode_matches=True)
            (args.output/'frames.json').write_text(json.dumps(dict(forward=forward, reverse=reverse))+'\n')
    except Exception as exc:
        result['error'] = str(exc)
    (args.output/'analysis.json').write_text(json.dumps(result, indent=2)+'\n')
    if 'error' in result: raise SystemExit('Waveform validation failed: '+result['error'])
    print('Waveform coverage passed: marker, exact 32 KiB payload and correct final reply.')
    print(json.dumps(result['payload'], indent=2))
    if not result['acquisition_pass']:
        raise SystemExit('Sample extent differs from the procedure; retain coverage separately.')


if __name__ == '__main__': main()
