#!/usr/bin/env python3
"""Check or mechanically copy the canonical controller carrier definitions.

No firmware build, installation or hardware access. P4's header owns the bytes;
the EMOS copy and standalone public include embed generated definitions,
never independent ABI authorities.
"""
import argparse
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--emos-source',type=Path,default=ROOT.parent/'agon-emos')
    p.add_argument('--write',action='store_true',help='Replace generated EMOS/public-header copies; default checks only')
    args=p.parse_args()
    source=ROOT/'vdp/video/extender/input/controller/appliance_wire.h'
    target=args.emos_source/'src/emos_controller_wire.h'
    data=source.read_bytes()
    if args.write:target.write_bytes(data)
    if target.read_bytes()!=data:p.exit(1,'Controller carrier drift: regenerate with --write\n')
    public=ROOT/'include/agon/controller.hpp'
    begin=b'// BEGIN mechanically copied appliance_wire.h\n'
    end=b'// END mechanically copied appliance_wire.h'
    body=public.read_bytes()
    if body.count(begin)!=1 or body.count(end)!=1:p.exit(1,'Missing public controller wire markers\n')
    prefix,tail=body.split(begin)
    embedded,suffix=tail.split(end)
    if args.write:public.write_bytes(prefix+begin+data+end+suffix)
    elif embedded!=data:p.exit(1,'Public controller carrier drift: regenerate with --write\n')
    print('Canonical P4/EMOS/public controller carrier bytes match')

if __name__=='__main__':main()
