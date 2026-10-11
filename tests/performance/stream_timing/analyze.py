#!/usr/bin/env python3
"""Validate complete paired captures and compare sender clocks. No board access."""
import argparse
import csv
import json
import io
from pathlib import Path
import re
import statistics
from payloads import LENGTHS, expected_buffer

ANSI=re.compile(r'\x1b\[[0-9;]*[A-Za-z]')
FIELDS=('wire_bytes','repeat','submit_prt','wire_prt','receipt_prt','reply_prt',
        'mos_ticks','flags','read_overhead','empty_drain_prt','vblank_prt','vblank_mos','divider','run_ticks')

def read_rows(text,route):
    raw=list(csv.DictReader(text.splitlines()))
    if len(raw)!=24:raise ValueError('expected all 24 rows including warm-ups')
    rows=[]
    for i,r in enumerate(raw):
        if r['route']!=route:raise ValueError('route mislabeled')
        row={k:int(r[k]) for k in FIELDS}
        if (row['wire_bytes'],row['repeat'])!=(LENGTHS[i//6],i%6):raise ValueError('missing/reordered sample')
        if row['flags'] or row['divider']!=256:raise ValueError('fault, overflow or wrong timer divisor')
        for k in ('submit_prt','wire_prt','receipt_prt','reply_prt','read_overhead','empty_drain_prt'):
            if not 0<=row[k]<65535:raise ValueError('timer outside single-pass range')
        if not 0<row['wire_prt']<=row['receipt_prt']<=row['reply_prt']:raise ValueError('drain/reply order invalid')
        if row['submit_prt']>row['receipt_prt']:raise ValueError('submission after receipt observation')
        if route=='excom' and row['wire_prt']!=row['receipt_prt']:raise ValueError('UART has no separate block receipt')
        if row['run_ticks']<=0:raise ValueError('missing durable run duration')
        if not 0<row['vblank_prt']<65535 or not 0<row['vblank_mos']<240:raise ValueError('invalid timer/VBlank cross-check')
        rows.append(row)
    return rows

def validate_dumps(text,rows):
    # P4 force_debug_log uses ESP_LOGI: every byte gets its own tagged line.
    # Strip only ANSI decoration, never arbitrary hex-looking log text.
    text=ANSI.sub('',text)
    header=re.compile(r'extender_vdp: vdu_sys_buffered: buffer 57600, (\d+) streams stored')
    byte=re.compile(r'extender_vdp: ([0-9A-Fa-f]{2})\s*$')
    dumps=[];current=None
    for line in text.splitlines():
        match=header.search(line)
        if match:
            if int(match[1])!=1:raise ValueError('target buffer has wrong block count')
            if current is not None:dumps.append(bytes(current))
            current=bytearray()
        elif current is not None and (match:=byte.search(line)):
            current.append(int(match[1],16))
    if current is not None:dumps.append(bytes(current))
    if len(dumps)!=len(rows):raise ValueError('missing/extra buffer dumps')
    for i,(dump,row) in enumerate(zip(dumps,rows)):
        if dump!=expected_buffer(row['wire_bytes']):raise ValueError(f'buffer bytes differ or capture truncated at sample {i}')
    return dict(samples=len(dumps),verified_bytes=sum(map(len,dumps)))

def compare(uart,parallel):
    result=[]
    for n in LENGTHS:
        variants={}
        for name,rows in [('uart',uart),('parallel',parallel)]:
            samples=[r for r in rows if r['wire_bytes']==n and r['repeat']!=0]
            metrics={}
            for k in ('submit_prt','wire_prt','receipt_prt','reply_prt'):
                ticks=[r[k] for r in samples]
                median=statistics.median(ticks)
                metrics[k]=dict(median_ticks=median,min_ticks=min(ticks),max_ticks=max(ticks),
                    median_us=median*256/18.432,median_equivalent_cycles=median*256,
                    equivalent_cycles_per_wire_byte=median*256/n)
            variants[name]=metrics
        # A zero UART duration means timer resolution is inadequate, never inf.
        changes={}
        for key in ('submit_prt','wire_prt','reply_prt'):
            baseline=variants['uart'][key]['median_ticks']
            if baseline<=0:raise ValueError('UART baseline below timer resolution')
            changes[key]=100*(variants['parallel'][key]['median_ticks']/baseline-1)
        result.append(dict(wire_bytes=n,variants=variants,parallel_elapsed_change_percent=changes))
    return sorted(result,key=lambda r:r['parallel_elapsed_change_percent']['wire_prt'],reverse=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('excom-results','excom-usb','exext-results','exext-usb','output'):
        p.add_argument('--'+name,type=Path,required=True,**({} if name=='output' else {'nargs':'+'}))
    a=p.parse_args()
    if a.output.exists():p.error('output must be fresh')
    def combine(paths):
        records=[r for path in paths for r in csv.DictReader(path.read_text().splitlines())]
        if not records:raise ValueError('empty results')
        out=io.StringIO();writer=csv.DictWriter(out,fieldnames=records[0]);writer.writeheader();writer.writerows(records)
        return out.getvalue()
    uart=read_rows(combine(a.excom_results),'excom');parallel=read_rows(combine(a.exext_results),'exext')
    integrity=dict(uart=validate_dumps('\n'.join(p.read_text(errors='replace') for p in a.excom_usb),uart),
                   parallel=validate_dumps('\n'.join(p.read_text(errors='replace') for p in a.exext_usb),parallel))
    comparison=compare(uart,parallel)
    a.output.mkdir(parents=True)
    controls={route:[{key:r[key] for key in ('wire_bytes','read_overhead','empty_drain_prt','vblank_prt','vblank_mos','run_ticks')} for r in rows if r['repeat']==0]
              for route,rows in [('uart',uart),('parallel',parallel)]}
    (a.output/'results.json').write_text(json.dumps(dict(integrity=integrity,controls=controls,comparison=comparison),indent=2)+'\n')
    lines=['# Matched stream timing results','',
        'Worst sender wire-drain slowdown first. Positive percentages mean parallel took longer; UART is the baseline. Five samples per cell; warm-ups excluded.',
        '', '| Wire bytes | UART submit µs | Parallel submit µs | UART wire-drain µs | Parallel wire-drain µs | Elapsed change |',
        '|---:|---:|---:|---:|---:|---:|']
    for row in comparison:
        u=row['variants']['uart'];v=row['variants']['parallel']
        lines.append(f"| {row['wire_bytes']} | {u['submit_prt']['median_us']:.1f} | {v['submit_prt']['median_us']:.1f} | {u['wire_prt']['median_us']:.1f} | {v['wire_prt']['median_us']:.1f} | {row['parallel_elapsed_change_percent']['wire_prt']:+.1f}% |")
    lines+=['','Full ranges, equivalent cycles and cycles/byte are in results.json. Physical drain is a software observation after the final edge/empty indication and includes observation overhead and possible interrupt preemption.',
        '', '| Wire bytes | UART ordered reply µs | Parallel ordered reply µs | Elapsed change | Parallel block-completion µs |',
        '|---:|---:|---:|---:|---:|']
    for row in comparison:
        u=row['variants']['uart'];v=row['variants']['parallel']
        lines.append(f"| {row['wire_bytes']} | {u['reply_prt']['median_us']:.1f} | {v['reply_prt']['median_us']:.1f} | {row['parallel_elapsed_change_percent']['reply_prt']:+.1f}% | {v['receipt_prt']['median_us']:.1f} |")
    lines+=['','The reply confirms synchronous buffer processing and includes the seven-byte query and reverse traffic. It is not HDMI FPS, renderer completion, raw bus bandwidth or retired CPU instructions. M03−M02 covers the last block tail/receipt, not all earlier handovers. No dominant-cause claim follows automatically.','']
    (a.output/'RESULTS.md').write_text('\n'.join(lines))
    print(json.dumps(integrity))
if __name__=='__main__':main()
