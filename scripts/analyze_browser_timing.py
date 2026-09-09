#!/usr/bin/env python3
"""Analyze an after-run browser/P4 timing download without clock synchronization.

Only isolated printable echoes qualify for UART/frame association. Frame latency
uses the first received snapshot composed after drawing flush and before another
VDU unit: a guaranteed-containing frame, not necessarily the earliest such frame.
Browser presentation is WebGL submission, not measured monitor scanout.
"""
import argparse
import csv
import io
import json
import statistics
from pathlib import Path


def analyze(report):
    browser=report['rows']
    raw=report.get('p4') or ''
    p4=[]
    for row in csv.DictReader(io.StringIO('\n'.join(x for x in raw.splitlines() if not x.startswith('#')))):
        p4.append({k:(v if k=='event' else int(v)) for k,v in row.items()})
    data={name:[] for name in ('browser_event_to_ack_ms','browser_send_to_ack_ms',
          'p4_admission_to_uart_submit_ms','p4_uart_submit_to_echo_ms',
          'p4_echo_to_flush_ms','p4_snapshot_compose_ms','p4_video_send_ms',
          'browser_receive_to_submit_ms','browser_event_to_guaranteed_frame_ms')}
    sent={(r['sid'],r['ordinal']):r for r in browser if r['event']=='key_send'}
    events={r['event_id']:r for r in browser if r['event']=='key_event'}
    for ack in (r for r in browser if r['event']=='key_ack'):
        source=sent.get((ack['sid'],ack['ordinal']))
        if not source: continue
        data['browser_send_to_ack_ms'].append(ack['ms']-source['ms'])
        event=events.get(source.get('event_id'))
        if event: data['browser_event_to_ack_ms'].append(ack['ms']-event['ms'])
    received={(r['sid'],r['seq']):r for r in browser if r['event']=='frame_received'}
    presented={(r['sid'],r['seq']):r for r in browser if r['event']=='frame_submitted'}
    for key,r in presented.items():
        if key in received: data['browser_receive_to_submit_ms'].append(r['ms']-received[key]['ms'])
    snapshots=[r for r in p4 if r['event']=='snapshot']
    for r in snapshots: data['p4_snapshot_compose_ms'].append((r['b']-r['a'])/1000)
    starts={}
    messages={}
    pending=None
    tx=[]
    video_sessions={}
    video_sends=[]
    for r in p4:
        if r['event']=='video_open': video_sessions[r['a']]=r['id']
        if r['event']=='video_send_start':
            starts[(r['id'],r['a'])]=r
            video_sends.append((r,video_sessions.get(r['a'])))
        if r['event']=='video_send_end':
            start=starts.pop((r['id'],r['a']),None)
            if start: data['p4_video_send_ms'].append((r['us']-start['us'])/1000)
        if r['event']=='key_message': messages[(r['id'],r['a'])]=r
        if r['event']=='key_dequeue': pending=(r['id'],r['a'])
        if r['event']=='key_pop' and r['b']==0: pending=None
        if r['event']=='uart_submit':
            # Retained packet: 81 04 ASCII modifiers VK down. Other UART output
            # is admission/settings/General Poll and cannot be an echoed key.
            if r['a']==6 and r['b']&0xffff==0x0481 and (r['c']>>8)&255==1:
                char=(r['b']>>16)&255
                tx.append((r,pending,char));pending=None
    vdu=[r for r in p4 if r['event']=='vdu_received']
    flushes=[r for r in p4 if r['event']=='draw_flush_done']
    associations=[]
    unpaired=0
    for i,(request,key,char) in enumerate(tx):
        if not key or not 32<=char<=126: unpaired+=1;continue
        bs=sent.get(key);event=events.get(bs.get('event_id')) if bs else None
        msg=messages.get(key)
        limit=tx[i+1][0]['us'] if i+1<len(tx) else float('inf')
        candidates=[r for r in vdu if request['us']<=r['us']<limit and r['b']==1 and r['a']==char]
        # Other visible/control text before this echo is ambiguous (banner,
        # backspace, wrap or multiple queued keys). Never guess a correspondence.
        preceding=[r for r in vdu if request['us']<=r['us']<limit and r['a']&255!=23]
        if not event or not msg or len(candidates)!=1 or len(preceding)!=1:
            unpaired+=1;continue
        echo=candidates[0]
        data['p4_admission_to_uart_submit_ms'].append((request['us']-msg['us'])/1000)
        data['p4_uart_submit_to_echo_ms'].append((echo['us']-request['us'])/1000)
        flush=next((r for r in flushes if echo['us']<=r['us']<limit),None)
        if not flush: continue
        data['p4_echo_to_flush_ms'].append((flush['us']-echo['us'])/1000)
        next_drawing=next((r['us'] for r in vdu if r['us']>flush['us'] and r['a']&255!=23),float('inf'))
        frames={r['id'] for r in snapshots if r['a']>flush['us'] and r['b']<next_drawing}
        shown=[presented[(sid,r['id']&0xffffffff)] for r,sid in video_sends
               if r['id'] in frames and (sid,r['id']&0xffffffff) in presented]
        shown=[r for r in shown if r['ms']>=event['ms']]
        if shown:
            first=min(shown,key=lambda r:r['ms'])
            data['browser_event_to_guaranteed_frame_ms'].append(first['ms']-event['ms'])
            associations.append({'event_id':event['event_id'],'ascii':char,'frame_sequence':first['seq'],
                                 'bound':'first recorded presented frame guaranteed to contain flushed drawing; may overestimate earliest visibility'})
    def summary(values):
        return {'n':len(values),'median_ms':round(statistics.median(values),3) if values else None,
                'max_ms':round(max(values),3) if values else None}
    return {'schema':1,'intervals':{k:summary(v) for k,v in data.items()},
            'isolated_frame_associations':associations,'unpaired_or_nonprintable_keys':unpaired,
            'browser_overwritten':report.get('overwritten'),
            'p4_metadata':[s for s in raw.splitlines() if s.startswith('#')],
            'browser_lifecycle':[r for r in browser if any(x in r['event'] for x in ('close','release','blur','visibility'))],
            'p4_lifecycle':[r for r in p4 if any(x in r['event'] for x in ('close','error','budget','revoke','failure','stop','reject'))],
            'limits':['UART submit is a driver call boundary, not physical first/last-bit measurement.',
                      'No cross-clock subtraction or exact one-way Ethernet timing.',
                      'Missing/overwritten/ambiguous matches are not zero latency.',
                      'P4 cost counters include record lock/clock overhead; they do not measure every instrumentation cost.']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('download',type=Path)
    args=parser.parse_args()
    print(json.dumps(analyze(json.loads(args.download.read_text())),indent=2))
if __name__=='__main__':main()
