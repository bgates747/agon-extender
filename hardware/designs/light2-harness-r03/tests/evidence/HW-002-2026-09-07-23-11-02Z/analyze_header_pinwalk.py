#!/usr/bin/env python3
"""Validate selected channels from the generic eZ80 header pinwalk."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from analyze_la_capture import load_capture, transitions

def count_falling(samples: bytes, bit: int) -> int:
    values=[(sample>>bit)&1 for sample in samples]
    return len(transitions(values,1,0))

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument("capture",type=Path)
    parser.add_argument("--expect",action="append",default=[],metavar="SIGNAL:CHANNEL:PULSES"); parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    if not args.expect: parser.error("at least one --expect is required")
    rate,samples,probes=load_capture(args.capture); results=[]; errors=[]; used=set()
    for spec in args.expect:
        try: signal,channel,count=spec.split(":"); expected=int(count)
        except ValueError: parser.error(f"invalid expectation: {spec}")
        channel=channel.upper()
        if channel not in probes: parser.error(f"capture lacks {channel}")
        if channel in used: parser.error(f"channel repeated: {channel}")
        used.add(channel)
        observed=count_falling(samples,probes[channel]); passed=observed==expected
        if not passed: errors.append(f"{signal} on {channel}: observed {observed} pulses, expected {expected}")
        results.append({"signal":signal,"channel":channel,"expected_pulses":expected,"observed_pulses":observed,"status":"PASS" if passed else "FAIL"})
    report={"status":"PASS" if not errors else "FAIL","sample_rate_hz":rate,"sample_count":len(samples),"signals":results,"errors":errors}
    if args.output: args.output.write_text(json.dumps(report,indent=2)+"\n")
    for item in results: print(f"{item['status']}: {item['signal']}={item['channel']} pulses={item['observed_pulses']}")
    return 0 if not errors else 1
if __name__ == "__main__": raise SystemExit(main())
