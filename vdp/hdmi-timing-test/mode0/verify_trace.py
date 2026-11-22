#!/usr/bin/env python3
"""Verify one mode 0 live USB transcript offline. Exit 0 PASS, 1 FAIL, 2 INCOMPLETE."""
import argparse
import hashlib
import json
from pathlib import Path


TOP = "58204ce0d40cd2a2426ca942edbc4309ba2d18d211bb744dc6fdde07b247a353"
BOTTOM = "40c930d3e3ee215618e5260d51a3216c2a5201f93805217c6047a099c4b7128d"
VALID, LAST, IOC = 1 << 31, 1 << 30, 1 << 26
FRAME_DONE, BLOCK_DONE = 1 << 31, 1 << 30
ROW_BYTES = 848 * 3
MASK32 = (1 << 32) - 1
CHANNEL_ERRORS = 0x823f5fe0 | (1 << 13)  # M0_BUS_ERRORS plus invalid LLI


class FailedTrial(Exception):
    pass


def require(condition, message):
    if not condition:
        raise FailedTrial(message)


def verify(trace):
    lines = trace.decode("ascii", errors="replace").splitlines()
    if lines.count("MODE0_LIVE begin") != 1:
        raise ValueError("Expected exactly one live invocation")
    lines = lines[lines.index("MODE0_LIVE begin") + 1:]
    ends = [i for i, line in enumerate(lines) if line.startswith("MODE0_END ")]
    if len(ends) > 1:
        raise ValueError("Multiple trial endings")
    end = lines[ends[0]] if ends else None
    if ends:
        lines = lines[:ends[0]]
    results = [json.loads(line.removeprefix("MODE0_RESULT ")) for line in lines
               if line.startswith("MODE0_RESULT ")]
    if not results and end and end != "MODE0_END err=ESP_OK reference_ready=1":
        raise FailedTrial(end)
    if len(results) != 1:
        raise ValueError("Missing or duplicate MODE0_RESULT")
    result = results[0]
    require(result["fault"] == "none", f'Driver fault: {result["fault"]}')
    if not ends:
        raise ValueError("Missing trial ending and reference readiness")
    require(end == "MODE0_END err=ESP_OK reference_ready=1", end)
    for field in ("primed", "started", "in_irq", "fills", "published", "frame_ok",
                  "live_stopped", "reference_restored"):
        require(result[field] == 1, f"Expected {field}=1")
    require(result["underruns"] == 0 and not result["raw"] & CHANNEL_ERRORS and
            result["raw"] & 2, "Missing final DMA completion or DMA/bridge error")

    llis, slots = {}, {}
    for line in lines:
        if line.startswith("MODE0_LLI "):
            snap = json.loads(line.removeprefix("MODE0_LLI "))
            key = snap["when"], snap["index"]
            if key in llis:
                raise ValueError(f"Duplicate descriptor record {key}")
            llis[key] = snap
        elif line.startswith("MODE0_SLOT "):
            _, name, payload = line.split()
            if name in slots:
                raise ValueError(f"Duplicate slot record {name}")
            slots[name] = bytes.fromhex(payload)
    armed = [llis["armed", i] for i in range(3)]
    frozen = [llis["frozen", i] for i in range(3)]
    retired, pending = llis["retire", 0], llis["before_refill", 2]
    if len(llis) != 8 or set(slots) != {"before", "after"}:
        raise ValueError("Unexpected descriptor set or missing row bytes")

    slot, middle = armed[0]["source"], armed[1]["source"]
    require(0 < slot <= (1 << 32) - 2560 and slot % 128 == 0 and
            0 < middle <= (1 << 32) - 478 * ROW_BYTES and middle % 8 == 0 and
            (slot + 2560 <= middle or middle + 478 * ROW_BYTES <= slot),
            "Invalid or overlapping DMA sources")
    marks = [IOC | VALID, VALID, LAST]
    for i, (source, words) in enumerate(((slot, 318), (middle, 152004), (slot, 318))):
        a, f = armed[i], frozen[i]
        require(a["source"] == f["source"] == source and
                a["block_size"] == f["block_size"] == words - 1,
                f"Source address or extent mismatch for descriptor {i}")
        require(a["control"] & (IOC | VALID | LAST) == marks[i] and a["status"] == a["count"] == 0,
                f"Descriptor {i} was not freshly armed")
        require(f["control"] == a["control"] & ~VALID, f"Descriptor {i} failed to retire")
    require(all(pending[k] == armed[2][k] for k in ("source", "block_size", "control", "status", "count")),
            "Replacement was already available before first store")
    require(all(retired[k] == frozen[0][k] for k in ("source", "block_size", "control", "status", "count"))
            and retired["status"] & (FRAME_DONE | BLOCK_DONE) == BLOCK_DONE,
            "Missing unchanged first-reader retirement")
    require(frozen[2]["status"] & (FRAME_DONE | BLOCK_DONE) == FRAME_DONE | BLOCK_DONE,
            "Replacement did not finish the frame")

    for name, expected in (("before", TOP), ("after", BOTTOM)):
        if len(slots[name]) != ROW_BYTES:
            raise ValueError(f"Incomplete {name} row")
        require(hashlib.sha256(slots[name]).hexdigest() == expected, f"Wrong {name} row bytes")
    entry = result["irq_entry"]
    stamps = [result[k] for k in ("retired_at", "first_store_at", "published_at", "frame_at")]
    require(all(type(x) is int and 0 <= x <= MASK32 for x in [entry, *stamps]), "Invalid cycle counter")
    retire, store, publish, finish = [(x - entry) & MASK32 for x in stamps]
    require(0 < retire < store < publish < finish < (1 << 31), "Handoff timestamps out of order")
    require(result["cpu_mhz"] == 360 and result["refill_cycles"] == publish and
            result["refill_us"] == (publish * 1000 // 360) / 1000, "Inconsistent refill timing")
    return {"slot_address": hex(slot), "frames": 1, "interrupt_refills": 1,
            "first_row_sha256": TOP, "last_row_sha256": BOTTOM,
            "refill_cycles": publish, "refill_us": publish / 360}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace", type=Path, help="Raw capture including MODE0_LIVE and MODE0_END")
    args = parser.parse_args()
    try:
        trace = args.trace.read_bytes()
        result = {"verdict": "PASS", **verify(trace)}
        status = 0
    except FailedTrial as error:
        result, status = {"verdict": "FAIL", "reason": str(error)}, 1
    except (ValueError, KeyError, TypeError, OSError) as error:
        result, status = {"verdict": "INCOMPLETE", "reason": str(error)}, 2
    print(json.dumps(result))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
