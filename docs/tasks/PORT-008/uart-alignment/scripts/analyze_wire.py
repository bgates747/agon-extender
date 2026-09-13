#!/usr/bin/env python3
"""Exact private-probe wire oracle and idle/backpressure attribution.

Reuse the previously tested sample decoder and independent sigrok comparison.
This does not infer CPU instructions from CTS-low idle or analogue integrity.
"""
import argparse
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import zipfile
import numpy as np

TASK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TASK.parents[1] / 'AUDIT-005/scripts'))
from analyze_trace import decode, high_intervals, gap_metrics, independent_decode, overlap, BIT
from capture_trace import RATE, SAMPLES, metadata, sha


def random_bytes(n):
    state = 0x12345678
    data = bytearray()
    for _ in range(n):
        state ^= (state << 13) & 0xffffffff
        state ^= state >> 17
        state ^= (state << 5) & 0xffffffff
        data.append(state & 255)
    return bytes(data)


def request(op, token, length):
    return bytes([23, 0, 0xee, op, token, 0, length & 255, length >> 8, 3])


def locate(frames, data):
    values = bytes(f['byte'] for f in frames)
    positions = [m.start() for m in re.finditer(re.escape(data), values)]
    if len(positions) != 1:
        raise ValueError(f'Expected one exact request, found {len(positions)}')
    return positions[0]


def probe_packets(frames, begin, end):
    selected = [f for f in frames if f['start'] >= begin and f['end'] <= end]
    packets = []
    index = 0
    while index < len(selected):
        if index+2 > len(selected) or selected[index]['byte'] < 0x80:
            raise ValueError('Malformed packet header in probe window')
        stop = index+2+selected[index+1]['byte']
        if stop > len(selected):
            raise ValueError('Truncated packet in probe window')
        part = selected[index:stop]
        data = bytes(f['byte'] for f in part)
        if data[:6] == bytes([0x8c, 16])+b'QTG\xa1':
            if data[9] != 1:
                raise ValueError('Unexpected probe source on P4 UART')
            packets.append((part, data))
        index = stop
    return packets


def analyze(raw):
    forward, ferr = decode(raw, 1)
    reverse, rerr = decode(raw, 6)
    # Forward token2, return token4: frozen wire selection, not a guessed marker.
    start = locate(forward, request(1, 2, 65535))
    data_start = start+9+8
    data_end = data_start+65535
    expected = (request(1, 2, 65535)+bytes([23,0,160,10,250,0,255,255])+
                random_bytes(65535)+request(2,2,65535)+request(3,2,65535))
    if bytes(f['byte'] for f in forward[start:start+len(expected)]) != expected:
        raise ValueError('Missing, extra, reordered or corrupt forward transfer')
    last_query = forward[start+len(expected)-1]
    # Bound reply parsing by the next forward command, if present.
    after = start+len(expected)
    bound = forward[after]['start'] if after < len(forward) else len(raw)-1
    fp = probe_packets(reverse, forward[start]['start'], bound)
    if len(fp) != 3:
        raise ValueError('Expected three forward probe replies')
    local = {}
    for kind, (part, data) in enumerate(fp):
        if data[6:10] != bytes([2,0,kind,1]):
            raise ValueError('Forward probe token/kind mismatch')
        local[kind] = (int.from_bytes(data[10:14],'little'), int.from_bytes(data[14:18],'little'))
    if local[0] != (65535,3) or local[1][1] != 65535 or local[2] != (0,0xffffffff):
        raise ValueError('Destination forward byte/count validation failed')
    q = locate(forward, request(4,4,256))
    bound = forward[q+9]['start'] if q+9 < len(forward) else len(raw)-1
    rp = probe_packets(reverse, forward[q]['start'], bound)
    if len(rp) != 257:
        raise ValueError(f'Expected 257 return records, found {len(rp)}')
    expected_return = random_bytes(2048)
    for i, (part, data) in enumerate(rp[:-1]):
        if data[6:10] != bytes([i,0,96,1]) or data[10:18] != expected_return[i*8:i*8+8]:
            raise ValueError('Return packet sequence or payload mismatch')
    if rp[-1][1][6:10] != bytes([4,0,3,1]) or int.from_bytes(rp[-1][1][14:18],'little') != 256:
        raise ValueError('Return completion mismatch')
    windows = [(forward[start]['start'],fp[-1][0][-1]['end']),
               (forward[q]['start'],rp[-1][0][-1]['end'])]
    if windows[-1][1]+BIT >= len(raw):
        raise ValueError('No complete capture tail')
    if any(a <= e < b for a,b in windows for e in ferr+rerr):
        raise ValueError('UART framing error in measured window')
    fblock = high_intervals(raw,4)
    rblock = high_intervals(raw,3)
    payload = forward[data_start:data_end]
    rframes = [frame for part, data in rp for frame in part]
    result = dict(coverage_pass=True, forward_bytes=len(payload), return_wire_bytes=len(rframes),
        return_payload_bytes=2048, forward=gap_metrics(payload,fblock), reverse=gap_metrics(rframes,rblock),
        forward_local_elapsed_us=local[1][0],
        return_enqueue_us=int.from_bytes(rp[-1][1][10:14],'little'),
        return_request_to_completion_ms=(rframes[-1]['end']-forward[q]['start'])/RATE*1000,
        return_request_to_first_byte_ms=(rframes[0]['start']-forward[q+8]['end'])/RATE*1000,
        forward_starts_with_cts_high=sum(bool(int(raw[f['start']])&16) for f in payload),
        reverse_starts_with_cts_high=sum(bool(int(raw[f['start']])&8) for f in rframes),
        window_samples=windows, limits='Frame-end estimate has approximately one-sample uncertainty. '
        'CTS-low idle does not identify its software cause. No analogue-integrity claim.')
    return result,forward,reverse,windows


def main():
    p=argparse.ArgumentParser()
    p.add_argument('trace',type=Path)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    result=dict(acquisition_pass=False,coverage_pass=False,independent_decode_matches=False,
                trace_sha256=sha(a.trace),analysis_sha256=sha(__file__))
    try:
        with tempfile.TemporaryDirectory(dir=a.output) as tmp:
            rawpath=Path(tmp)/'logic.raw'
            with zipfile.ZipFile(a.trace) as archive,rawpath.open('wb') as stream:
                names,count=metadata(archive)
                for name in names:
                    with archive.open(name) as source:shutil.copyfileobj(source,stream,4_000_000)
            result.update(samples=count,sample_rate_hz=RATE,acquisition_pass=count==SAMPLES)
            raw=np.memmap(rawpath,dtype=np.uint8,mode='r')
            checked,forward,reverse,windows=analyze(raw)
            result.update(checked)
            # One comparison across both windows also checks any intervening
            # legal UART frames; separate probe extraction identifies payloads.
            for pin,frames in ((1,forward),(6,reverse)):
                independent_decode(a.trace,a.output,pin,frames,windows[0][0],windows[-1][1])
            result['independent_decode_matches']=True
            del raw
    except Exception as error:
        result['error']=str(error)
    (a.output/'analysis.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    return int(not all(result[k] for k in ('acquisition_pass','coverage_pass','independent_decode_matches')))


if __name__=='__main__':raise SystemExit(main())
