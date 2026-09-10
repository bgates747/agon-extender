#!/usr/bin/env python3
"""Validate a saved benchmark CSV and compare coarse Legacy/ExCom timings."""
import argparse
import csv
import io
from pathlib import Path
from statistics import median

ENTRIES = ('byte', 'count', 'delimiter', 'cli-putch')
PAYLOADS = ('null', 'points')


def read_results(path):
    text = Path(path).read_text()
    rows = list(csv.DictReader(io.StringIO('\n'.join(x for x in text.splitlines() if not x.startswith('#')))))
    trace = '# mode=trace;' in text
    expected = 1 if trace else 48
    if not text.splitlines()[-1].startswith(f'# complete;rows={expected};status=0;legacy_return=0'):
        raise ValueError('Missing successful final record; retain as failed/incomplete evidence')
    if len(rows) != expected:
        raise ValueError(f'Expected {expected} rows, found {len(rows)}')
    keys = set()
    for i, r in enumerate(rows, 1):
        key = (int(r['repeat']), r['route'], r['entry'], r['payload'])
        if key in keys or r['entry'] not in ENTRIES or r['payload'] not in PAYLOADS:
            raise ValueError('Duplicate or unknown case')
        keys.add(key)
        for field, value in dict(row=i, chunks=512, bytes=32768, send_status=0,
                                 reply_status=0, mode=0, width=640, height=480, colours=16, valid=1).items():
            if int(r[field]) != value:
                raise ValueError(f'Row {i}: invalid {field}={r[field]}')
        for field in ('pixel_r','pixel_g','pixel_b'):
            if int(r[field]) != (255 if r['payload']=='points' else 0):
                raise ValueError(f'Row {i}: wrong pixel')
        for field, start, end in (('send_ticks','t0','t1'),('tail_ticks','t1','t2'),('total_ticks','t0','t2')):
            if int(r[field]) != (int(r[end])-int(r[start])) & 0xffffff:
                raise ValueError(f'Row {i}: inconsistent timestamp arithmetic')
        if int(r['send_ticks']) <= 0:
            raise ValueError(f'Row {i}: stopped/unresolved clock')
        if 'first_reply_status' in r:
            for prefix in ('setup',''):
                status_key='setup_first_status' if prefix else 'first_reply_status'
                ticks_key='setup_reply_ticks' if prefix else 'reply_wait_ticks'
                if int(r[status_key]) not in (0,15) or not 0<=int(r[ticks_key])<=600:
                    raise ValueError(f'Row {i}: invalid completion observation')
            if int(r['reply_wait_ticks'])>int(r['tail_ticks']):
                raise ValueError(f'Row {i}: reply interval exceeds tail')
    expected_keys = {(n,route,entry,payload) for n in range(1,4) for route in ('legacy','excom')
                     for entry in ENTRIES for payload in PAYLOADS}
    if not trace and keys != expected_keys:
        raise ValueError('Incomplete paired matrix')
    if trace and next(iter(keys))[:2] != (1,'excom'):
        raise ValueError('Trace must be one ExCom row')
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv', type=Path)
    args = parser.parse_args()
    rows = read_results(args.csv)
    print(f'Valid saved benchmark: {len(rows)} rows. Nominal 120 clock units/s, 16.67 ms resolution.')
    if 'first_reply_status' in rows[0]:
        for key,label in (('setup_first_status','setup'),('first_reply_status','measured completion')):
            missed=sum(int(r[key])==15 for r in rows)
            print(f'Ordinary MOS wait expired on {missed} {label} queries; final replies met the five-second measurement bound.')
    if len(rows)==1:
        print(rows[0])
        return
    print('Entry/payload       Legacy send ticks  ExCom send ticks  ExCom/Legacy  Complete ticks L/E')
    for entry in ENTRIES:
        for payload in PAYLOADS:
            groups = [[r for r in rows if (r['route'],r['entry'],r['payload'])==(route,entry,payload)]
                      for route in ('legacy','excom')]
            send = [[int(r['send_ticks']) for r in group] for group in groups]
            complete = [median(int(r['total_ticks']) for r in group) for group in groups]
            labels = [f'{median(values):g} [{min(values)}..{max(values)}]' for values in send]
            print(f'{entry+"/"+payload:19} {labels[0]:18} {labels[1]:17} '
                  f'{median(send[1])/median(send[0]):.2f}x          {complete[0]:g}/{complete[1]:g}')
    print('Times include caller/UART waits; CLI also includes parsing. Completion is not browser presentation.')


if __name__ == '__main__':
    main()
