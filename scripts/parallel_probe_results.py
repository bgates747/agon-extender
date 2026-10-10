#!/usr/bin/env python3
"""Match PORT-008 private MOSlet CSV to P4 USB receipts; no bench operations."""
import argparse
import binascii
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import zlib

RECEIPT = re.compile(
    r"Parallel probe descriptor=([0-9a-f]{32}) direction=([01]) length=(\d+) "
    r"crc=([0-9a-f]{8}) first=([0-9a-f]{2}) last=([0-9a-f]{2}) "
    r"guards=([01]) pattern=(na|[01]) elapsed_us=(\d+)$")
SIZES = (1, 2, 255, 256, 4096)


def pattern(n, seed):
    return bytes(((i * 73) ^ ((i >> 3) * 29) ^ (i >> 8) ^ seed) & 255
                 for i in range(n))


def compare(agon_text, p4_text):
    rows = list(csv.DictReader(io.StringIO("\n".join(
        line for line in agon_text.splitlines() if not line.startswith("#")))))
    begin = re.findall(r"^# start_mos_ticks=(\d+); nominal120_Hz_not_calibrated$", agon_text, re.M)
    end = re.findall(r"^# end_mos_ticks=(\d+); total_mos_ticks=(\d+); passed=20/20$", agon_text, re.M)
    if len(rows) != 20 or len(begin) != 1 or len(end) != 1:
        raise ValueError("missing twenty-row successful Agon run and durable start/end")
    if (int(end[0][0]) - int(begin[0])) & 0xFFFFFFFF != int(end[0][1]):
        raise ValueError("inconsistent Agon run duration")
    receipts = {}
    for line in p4_text.splitlines():
        if "Parallel probe descriptor=" not in line:
            continue
        match = RECEIPT.search(line)
        if not match:
            raise ValueError("malformed P4 receipt")
        values = match.groups()
        if values[0] in receipts:
            raise ValueError("duplicate P4 receipt")
        receipts[values[0]] = values
    if len(receipts) != 20:
        raise ValueError("missing twenty distinct P4 receipts")
    checked = []
    sessions = set()
    for index, row in enumerate(rows):
        round_, position = divmod(index, 10)
        direction, j = divmod(position, 5)
        n = SIZES[j]
        d = bytes.fromhex(row["descriptor"])
        if (len(d) != 16 or d[:4] != b"EX\x02\x02" or not any(d[4:8]) or
                d[8:10] != b"\x01\x00" or int.from_bytes(d[10:12], "little") != n or
                d[12:14] != bytes((direction, 0)) or
                d[14:] != binascii.crc_hqx(d[:14], 0xFFFF).to_bytes(2, "little")):
            raise ValueError("invalid retained offer descriptor")
        if d[4:8] in sessions:
            raise ValueError("reused qualification session identity")
        sessions.add(d[4:8])
        if (int(row["row"]) != index + 1 or int(row["direction"]) != direction or
                int(row["length"]) != n or row["guards"] != "1" or
                row["pattern"] != "1" or row["service_status"] != "0"):
            raise ValueError("failed or out-of-order Agon case")
        seed = (d[4] ^ d[5] ^ d[6] ^ d[7] ^ d[8] ^ d[9] ^ 0xD3
                if direction else (17 + round_ * 109 + j * 11) & 255)
        data = pattern(n, seed)
        expected = (f"{zlib.crc32(data):08x}", f"{data[0]:02x}", f"{data[-1]:02x}")
        peer = receipts.pop(row["descriptor"], None)
        if (peer is None or int(peer[1]) != direction or int(peer[2]) != n or
                tuple(peer[3:6]) != expected or tuple(row[k] for k in ("crc", "first", "last")) != expected or
                peer[6] != "1" or peer[7] != ("1" if direction else "na")):
            raise ValueError("endpoint integrity or descriptor mismatch")
        checked.append({"row": index + 1, "direction": direction, "bytes": n,
                        "agon_service_mos_ticks": int(row["elapsed_mos_ticks"]),
                        "p4_offer_to_receipt_us": int(peer[8]), "crc32": expected[0]})
    return {"passed": True, "cases": checked, "total_agon_mos_ticks": int(end[0][1]),
            "timing_scope": "Agon nominal120Hz uncalibrated ticks; P4 offer-to-receipt microseconds. Neither is link-only throughput."}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--agon-csv", required=True, type=Path)
    p.add_argument("--p4-log", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    a = p.parse_args()
    result = compare(a.agon_csv.read_text(), a.p4_log.read_text())
    result["sources"] = [{"name": f.name, "sha256": hashlib.sha256(f.read_bytes()).hexdigest()}
                         for f in (a.agon_csv, a.p4_log)]
    a.output.write_text(json.dumps(result, indent=2) + "\n")
    print("Passed20 matched two-way endpoint cases; physical scope depends on the supplied run.")


if __name__ == "__main__":
    main()
