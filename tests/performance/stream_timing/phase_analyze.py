#!/usr/bin/env python3
"""Offline phase interpretation; elapsed nested scopes are never added twice."""
import csv,json,statistics
from pathlib import Path
BLOCK=('reserve_begin','reserve_end','offer_begin','coordinate_begin','park_end','payload_begin','payload_end','unpark_end','completion_begin','completion_end')
INTERVALS=tuple(zip(BLOCK,BLOCK[1:]))
US=256/18.432

def sample(row,records,sites):
    n=int(row['wire_bytes']);repeat=int(row['repeat']);reply=int(row['reply_prt'])
    if int(row['flags']) or row['route']!='exext' or int(row['divider'])!=256:raise ValueError('fault/route/divider')
    if not 0<int(row['receipt_prt'])<=reply<65535 or not 0<=int(row['submit_prt'])<=int(row['receipt_prt']):raise ValueError('endpoint ordering/saturation')
    if int(row['wire_prt'])!=0:raise ValueError('phase composition does not measure M02')
    if not 0<len(records)<=512:raise ValueError('missing/overflow trace')
    events=[];last=0
    for i,r in enumerate(records):
        if (int(r['wire_bytes']),int(r['repeat']),int(r['index']))!=(n,repeat,i):raise ValueError('missing/reordered/foreign trace record')
        raw=int(r['raw_prt']);t=65535-raw
        if not 0<raw<=65535 or not last<=t<=reply:raise ValueError('trace timer saturation/order')
        last=t;pc=str(int(r['return_pc']))
        if pc not in sites:raise ValueError('unknown callsite')
        events.append(dict(name=sites[pc],ticks=t,length=int(r['offer_bytes']),reverse=int(r['reverse'])))
    blocks=[];active=[];scopes={};inclusive={k:0 for k in ('service','poll','publish')}
    for e in events:
        name=e['name']
        if name in BLOCK:
            if name!=BLOCK[len(active)]:raise ValueError('incomplete/reordered block phases')
            active.append(e)
            if name==BLOCK[-1]:
                begin=active[2];length=begin['length'];reverse=begin['reverse']
                if not 1<=length<=4096 or reverse not in (0,1):raise ValueError('invalid admitted offer')
                if any(x['length']!=length or x['reverse']!=reverse for x in active[2:]):raise ValueError('offer changes during block')
                intervals={a+'__'+b:y['ticks']-x['ticks'] for (a,b),x,y in zip(INTERVALS,active,active[1:])}
                blocks.append(dict(length=length,reverse=reverse,begin=active[0]['ticks'],end=e['ticks'],interval_ticks=intervals))
                active=[]
        else:
            prefix,edge=name.rsplit('_',1)
            if prefix not in inclusive:raise ValueError('unknown phase scope')
            if edge=='begin':
                if prefix in scopes:raise ValueError('nested same scope')
                scopes[prefix]=e['ticks']
            elif edge=='end':
                if prefix not in scopes:raise ValueError('unmatched scope end')
                inclusive[prefix]+=e['ticks']-scopes.pop(prefix)
            else:raise ValueError('invalid phase edge')
    if active or scopes:raise ValueError('unfinished block/scope')
    forward=sum(b['length'] for b in blocks if not b['reverse'])
    if forward!=n+7:raise ValueError('forward stream/query bytes not conserved')
    if not any(b['reverse'] for b in blocks):raise ValueError('missing return block')
    total=sum(b['end']-b['begin'] for b in blocks)
    if total>reply:raise ValueError('overlapping block intervals')
    return dict(wire_bytes=n,repeat=repeat,blocks=blocks,inclusive_scope_ticks=inclusive,
                block_total_ticks=total,outside_block_ticks=reply-total,reply_ticks=reply,
                phase_totals_ticks={a+'__'+b:sum(x['interval_ticks'][a+'__'+b] for x in blocks) for a,b in INTERVALS})

def aggregate(samples):
    result=[]
    for n in sorted({s['wire_bytes'] for s in samples}):
        rows=[s for s in samples if s['wire_bytes']==n and s['repeat']!=0]
        if len(rows)!=5 or {r['repeat'] for r in rows}!={1,2,3,4,5}:raise ValueError('five original comparison indices required')
        def metric(values):
            return dict(median_us=statistics.median(values)*US,min_us=min(values)*US,max_us=max(values)*US)
        result.append(dict(wire_bytes=n,reply=metric([s['reply_ticks'] for s in rows]),
          phases={k:dict(**metric([s['phase_totals_ticks'][k] for s in rows]),median_share_reply_percent=statistics.median([100*s['phase_totals_ticks'][k]/s['reply_ticks'] for s in rows])) for k in rows[0]['phase_totals_ticks']},
          outside_blocks=metric([s['outside_block_ticks'] for s in rows]),
          inclusive_scopes={k:metric([s['inclusive_scope_ticks'][k] for s in rows]) for k in ('service','poll','publish')}))
    return result
