#!/usr/bin/env python3
"""Existing production presenter with <=30Hz credits; no firmware changes.

Run beside the canonical measure_video.py in the receiver's scripts directory.
Host timing is message arrival/WebGL submission, not physical display scanout.
"""
import argparse
from pathlib import Path
import measure_video as m
p=argparse.ArgumentParser();p.add_argument('--url',required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--seconds',type=float,default=120);p.add_argument('--browser-executable',default='/usr/bin/chromium');a=p.parse_args()
patch="""
  send(data) {
   if(data!=='frame')return super.send(data);
   if(this.__creditPending)throw Error('duplicate deferred credit');
   this.__creditPending=true;
   const emit=()=>{
    const now=performance.now(); const remain=34-(now-(this.__lastCredit ?? -Infinity));
    if(remain>0){setTimeout(emit,Math.ceil(remain));return;}
    this.__creditPending=false;
    if(this.readyState!==Original.OPEN)return;
    this.__lastCredit=performance.now();
    window.__videoObservation.requests.push({ms:this.__lastCredit});
    super.send(data);
   };emit();
  }
"""
m.OBSERVER=m.OBSERVER.replace('frames:[],closes:[]','requests:[],frames:[],closes:[]').replace('constructor(...args) {',patch+'\n  constructor(...args) {')
# FNV-1a entire pixel payload; equality is a diagnostic fingerprint, not proof
# of identical rendering state or of one game frame per received snapshot.
m.OBSERVER=m.OBSERVER.replace('const latest=observation.frames[observation.frames.length-1];','''const latest=observation.frames[observation.frames.length-1];
    let hash=2166136261;for(let i=32;i<a.length;i++)hash=Math.imul(hash^a[i],16777619)>>>0;
    latest.pixelHash=hash;
    latest.requestMs=observation.requests.at(-1)?.ms;''')
m.collect(a.url,a.seconds,a.output,'BENCH-003 paced repair diagnostic',browser_executable=a.browser_executable,signal_ready=True)
