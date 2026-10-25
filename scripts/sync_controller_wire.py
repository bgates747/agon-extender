#!/usr/bin/env python3
"""Check or mechanically copy the canonical P4 controller carrier to EMOS.

No firmware build, installation or hardware access. P4's header owns the bytes;
the EMOS source copy is a generated input, never an independent ABI authority.
"""
import argparse
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--emos-source',type=Path,default=ROOT.parent/'agon-emos')
    p.add_argument('--write',action='store_true',help='Replace the generated EMOS copy; default checks only')
    args=p.parse_args()
    source=ROOT/'vdp/video/extender/input/controller/appliance_wire.h'
    target=args.emos_source/'src/emos_controller_wire.h'
    data=source.read_bytes()
    if args.write:target.write_bytes(data)
    if target.read_bytes()!=data:p.exit(1,'Controller carrier drift: regenerate with --write\n')
    print('Canonical P4/EMOS controller carrier bytes match')

if __name__=='__main__':main()
