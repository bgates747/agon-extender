#!/usr/bin/env python3
"""Inject loss/reorder/corruption into decoded real evidence; no hardware I/O."""
import argparse
from pathlib import Path
import shutil
import tempfile
from unittest.mock import patch
import zipfile
import numpy as np
import analyze_wire as oracle

p=argparse.ArgumentParser()
p.add_argument('trace',type=Path)
a=p.parse_args()
with tempfile.TemporaryDirectory() as tmp:
    path=Path(tmp)/'raw'
    with zipfile.ZipFile(a.trace) as archive,path.open('wb') as stream:
        names,count=oracle.metadata(archive)
        for name in names:
            with archive.open(name) as source:shutil.copyfileobj(source,stream)
    raw=np.memmap(path,dtype=np.uint8,mode='r')
    forward,ferr=oracle.decode(raw,1)
    reverse,rerr=oracle.decode(raw,6)
    index=oracle.locate(forward,oracle.request(1,2,65535))+17
    request=oracle.locate(forward,oracle.request(4,4,256))
    begin=forward[request]['start']
    end=forward[request+9]['start']
    packets=oracle.probe_packets(reverse,begin,end)
    reverse_index=next(i for i,f in enumerate(reverse) if f is packets[0][0][0])
    for case in ('forward loss','forward extra','forward corrupt','reverse loss',
                 'reverse reorder','reverse corrupt','reverse completion missing','framing'):
        f=list(forward);r=list(reverse);fe=list(ferr);re=list(rerr)
        if case=='forward loss':del f[index+99]
        elif case=='forward extra':f.insert(index+99,f[index+99])
        elif case=='forward corrupt':f[index+99]=dict(f[index+99],byte=f[index+99]['byte']^1)
        elif case=='reverse loss':del r[reverse_index+10]
        elif case=='reverse reorder':r[reverse_index:reverse_index+36]=r[reverse_index+18:reverse_index+36]+r[reverse_index:reverse_index+18]
        elif case=='reverse corrupt':r[reverse_index+10]=dict(r[reverse_index+10],byte=r[reverse_index+10]['byte']^1)
        elif case=='reverse completion missing':del r[reverse_index+4608:reverse_index+4626]
        else:fe.append(f[index]['start'])
        with patch.object(oracle,'decode',side_effect=lambda raw,pin:(f,fe) if pin==1 else (r,re)):
            try:oracle.analyze(raw)
            except ValueError:print('Rejected:',case)
            else:raise AssertionError('Oracle accepted '+case)
    del raw
