#!/usr/bin/env python3
"""Collect/validate R07 benchmark serial records and produce a comparison report."""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path
import statistics
import time

METHODS = ["cpu_signal", "cpu_linear", "ppa_linear", "reorder_ppa"]
CASES = [(320,32,32,"SRAM"),(512,32,32,"SRAM"),(320,32,32,"PSRAM"),
         (512,32,32,"PSRAM"),(320,240,0,"PSRAM"),(512,384,0,"PSRAM")]
FIELDS = ["case","method","sample","prepare_us","operation_us","publish_us","total_us","elapsed_cycles"]

def parse(raw, expected_build=None):
    records = [line.strip().split(",") for line in raw.splitlines() if line.startswith("BENCH_")]
    if any(r[0] in {"BENCH_ERROR", "BENCH_FAIL"} for r in records):
        raise ValueError("firmware reported a failure; raw evidence retained")
    begins = [i for i,r in enumerate(records) if r[0] == "BENCH_BEGIN"]
    if len(begins) != 1:
        raise ValueError("expected exactly one complete result batch")
    begin = records[begins[0]]
    if len(begin)!=7 or begin[3] not in {"fresh","stored"} or begin[4:]!=["6","4","32"]:
        raise ValueError("unsupported result schema")
    build, sequence = begin[1], int(begin[2])
    if sequence<=0 or not build.startswith("ppa-clut-benchmark-r01-b") or (expected_build and build!=expected_build):
        raise ValueError("unexpected build/sequence")
    if begin[3]=="fresh" and not any(len(r)==4 and r[:3]==["BENCH_STORED",build,str(sequence)] and int(r[3])>0 for r in records[:begins[0]]):
        raise ValueError("fresh result lacks durable storage acknowledgement")
    methods, cases, rows, done = {}, {}, {}, None
    for r in records[begins[0]+1:]:
        if done is not None and r[0]!="BENCH_READY":
            raise ValueError("record follows completion")
        if r[0]=="BENCH_METHOD":
            if len(r)!=3 or int(r[1]) in methods:
                raise ValueError("duplicate/malformed method")
            methods[int(r[1])] = r[2]
        elif r[0]=="BENCH_CASE":
            if len(r)!=6 or int(r[1]) in cases:
                raise ValueError("duplicate/malformed case")
            cases[int(r[1])] = (*map(int,r[2:5]),r[5])
        elif r[0]=="BENCH_ROW":
            if len(r)!=9:
                raise ValueError("malformed timing row")
            row = dict(zip(FIELDS,map(int,r[1:])))
            key = row["case"],row["method"],row["sample"]
            if key in rows or not (0<=key[0]<6 and 0<=key[1]<4 and 0<=key[2]<32):
                raise ValueError("duplicate/out-of-range timing row")
            if any(v<0 or v>0xffffffff for v in row.values()) or row["total_us"]<=0 or sum(row[k] for k in ["prepare_us","operation_us","publish_us"])!=row["total_us"]:
                raise ValueError("invalid timing arithmetic")
            rows[key] = row
        elif r[0]=="BENCH_DONE":
            if done is not None or len(r)!=5 or r[1:3]!=[build,str(sequence)] or r[4]!="768" or int(r[3])<=0:
                raise ValueError("invalid completion record")
            done = int(r[3])
        elif r[0] not in {"BENCH_READY"}:
            raise ValueError("unexpected record inside batch: " + r[0])
    if methods != dict(enumerate(METHODS)) or cases!=dict(enumerate(CASES)) or len(rows)!=768 or done is None:
        raise ValueError("incomplete or incompatible result batch")
    return {"schema_version":1,"build_id":build,"sequence":sequence,"kind":begin[3],
            "duration_us":done,"rows":[rows[k] for k in sorted(rows)]}

def summarize(data):
    groups = []
    for c in range(6):
        for m in range(4):
            rows = [r for r in data["rows"] if (r["case"],r["method"])==(c,m)]
            phases = {}
            for field in FIELDS[3:]:
                values = sorted(r[field] for r in rows)
                phases[field] = {"median":statistics.median(values),"p95":values[math.ceil(.95*len(values))-1],"worst":max(values)}
            groups.append({"case":c,"method":METHODS[m],"statistics":phases})
    return groups

def report(data):
    groups = summarize(data)
    lookup = {(g["case"],g["method"]):g["statistics"]["total_us"] for g in groups}
    # Worst relative complete-path PPA p95 first, including mandatory lane reorder.
    ranking = sorted(range(6),key=lambda c:lookup[c,"reorder_ppa"]["p95"]/lookup[c,"cpu_signal"]["p95"],reverse=True)
    lines = ["# CPU versus indexed PPA expansion", "", f"Build `{data['build_id']}`; run {data['sequence']} ({data['kind']}).",
             f"Firmware workload/check duration: {data['duration_us']/1e6:.3f} s; excludes result storage and serial emission.", "",
             "32 samples per method/case. Values are total elapsed microseconds, shown as median / p95 / worst. Worst complete-path PPA-to-CPU p95 ratio first.", "",
             "| Workload / destination | Old CPU signal | Linear CPU control | Linear PPA | Reorder + PPA | PPA p95 improvement | Complete-path p95 improvement |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    def fmt(s):
        return f"{s['median']:.1f} / {s['p95']} / {s['worst']}"
    for c in ranking:
        w,h,_,region = CASES[c]
        base = lookup[c,"cpu_signal"]["p95"]
        improvement = lambda method:100*(base-lookup[c,method]["p95"])/base
        lines.append(f"| {w}×{h} / {region} | " + " | ".join(fmt(lookup[c,m]) for m in METHODS) + f" | {improvement('ppa_linear'):+.1f}% | {improvement('reorder_ppa'):+.1f}% |")
    lines += ["", "Improvement = 100 × (old CPU p95 − candidate p95) / old CPU p95; positive means faster. Linear PPA assumes a changed framebuffer layout. Reorder + PPA includes adapting the old signal layout.", "",
              "Source is PSRAM; CPU conversion includes output publication and PPA includes driver cache work plus blocking completion. No HDMI scanout, sprites, game, browser or other concurrent workload runs. Elapsed cycle counts include waiting/preemption and are not CPU-busy measurements.", "",
              "| Workload / destination | Old CPU worst / budget | Reorder + PPA worst / budget | Budget context |", "|---|---:|---:|---|"]
    for c in ranking:
        w,h,_,region = CASES[c]
        budget = 1600 if h==32 else 1e6/60
        lines.append(f"| {w}×{h} / {region} | {100*lookup[c,'cpu_signal']['worst']/budget:.1f}% | {100*lookup[c,'reorder_ppa']['worst']/budget:.1f}% | {budget:.1f} µs {'strip guard' if h==32 else '60 Hz frame'} |")
    lines += ["", "Budget percentages are context only, not output/gameplay qualification. Timer resolution is one microsecond; CPU configured at 360 MHz, PSRAM at 200 MHz, dynamic power management disabled. Detailed phase distributions and raw cycles are in results.json and samples.csv.", ""]
    return "\n".join(lines)

def write_outputs(directory, raw, expected_build=None):
    (directory / "serial.log").write_text(raw)
    data = parse(raw,expected_build)
    data["summary"] = summarize(data)
    (directory / "results.json").write_text(json.dumps(data,indent=2)+"\n")
    with (directory / "samples.csv").open("w",newline="") as f:
        writer = csv.DictWriter(f,fieldnames=FIELDS)
        writer.writeheader();writer.writerows(data["rows"])
    (directory / "RESULTS.md").write_text(report(data))
    return data

def main():
    p = argparse.ArgumentParser(description=__doc__)
    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument("--input",type=Path)
    source.add_argument("--port",help="explicit local USB console; no discovery/reset")
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--build-id")
    p.add_argument("--dump",action="store_true",help="request saved NVS result using d; never reset/rerun")
    p.add_argument("--timeout",type=float,default=180,help="capture deadline only, seconds; never reset on expiry")
    args = p.parse_args()
    if args.output.exists() or args.timeout<=0:
        p.error("choose a fresh output directory and a positive deadline")
    args.output.mkdir(parents=True)
    raw = ""
    try:
        if args.input:
            raw = args.input.read_text()
        else:
            import serial
            # Set control lines before open: never assert automatic reset lines.
            connection = serial.Serial(port=None,baudrate=115200,timeout=.2)
            connection.dtr=False;connection.rts=False;connection.port=args.port
            connection.open()
            try:
                if args.dump:
                    connection.write(b"d");connection.flush()
                deadline = time.monotonic()+args.timeout
                while time.monotonic()<deadline:
                    raw += connection.readline().decode("utf-8",errors="replace")
                    (args.output / "serial.log").write_text(raw)
                    if any(line.startswith(("BENCH_DONE,","BENCH_FAIL,","BENCH_ERROR,")) for line in raw.split("\n")[:-1]):
                        break
                else:
                    raise ValueError("capture deadline expired; device left untouched")
            finally:
                connection.close()
        data = write_outputs(args.output,raw,args.build_id)
        print(f"Validated {len(data['rows'])} samples; {args.output / 'RESULTS.md'}")
    except (ValueError,OSError) as e:
        (args.output / "serial.log").write_text(raw)
        (args.output / "FAILURE.txt").write_text(str(e)+"\n")
        print(f"FAILED: {e}")
        return 1
    return 0

if __name__=="__main__":
    raise SystemExit(main())
