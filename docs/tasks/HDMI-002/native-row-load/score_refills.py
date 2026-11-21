"""Score one captured, stable native-mode window using software counters only."""
import argparse
import json
from pathlib import Path


def score(records):
    issues, failures = [], []
    result = {"physical_deadline": "unverified", "incomplete": issues, "failures": failures}
    markers = [r for r in records if "event" in r]
    if [r["event"] for r in markers] != ["start", "end"] or markers[0].get("arm") != "native":
        issues.append("Missing complete native window markers")
        return result
    result["host_elapsed_s"] = markers[-1]["elapsed_s"]
    if any("error" in r for r in records):
        issues.append("One or more requests failed")
    status = [r["data"] for r in records if r.get("path") == "/display/status" and "data" in r]
    if len(status) < 2 or any(s.get("available") is not True for s in status):
        issues.append("Missing display mode status")
    modes = {s.get("mode") for s in status}
    if len(modes) != 1 or None in modes:
        issues.append("Mode changed during the window")
    values = [r["data"] for r in records if r.get("path") == "/display/scanout" and "data" in r]
    if len(values) < 2:
        issues.append("Need at least two valid scanout samples")
        return result
    saved = [r["data"] for r in records if r.get("path") == "/display/scanout?last_fault=1" and "data" in r]
    if len(saved) < 2:
        issues.append("Missing opening or closing retained-fault register")
    else:
        # Free-heap gauges are taken while servicing each request and can
        # change for the same retained fault. The latched identity is stable.
        def identity(v):
            return (v.get("epoch"), v.get("fault"), v.get("fault_frame"), v.get("fault_block"))
        if any(s.get("fault") and identity(s) != identity(saved[0]) for s in saved[1:]):
            failures.append("New retained fault during the window")
    first, last = values[0], values[-1]
    epoch = first["epoch"]
    if any(v["fault"] or v["underruns"] or v["invalid"] or v["rejected"] for v in values):
        failures.append("Active epoch reports a fault, underrun, invalid or rejected slot")
    if epoch == 0 or any(v["epoch"] != epoch for v in values):
        issues.append("Need one active epoch; score mode transitions separately")
        return result
    result["epoch"], result["mode"] = epoch, next(iter(modes)) if len(modes) == 1 else None
    result["carrier"] = [first["width"], first["height"]]
    per_frame = {(684,384): 12, (848,480): 15}.get(tuple(result["carrier"]))
    if per_frame is None or any((v["width"],v["height"]) != tuple(result["carrier"]) for v in values):
        issues.append("Unexpected or changing carrier")
        return result
    delta = {k:last[k]-first[k] for k in ("frames", "blocks", "ready", "draw_wakes")}
    bins = [b-a for a,b in zip(first["refill_histogram_100us"],last["refill_histogram_100us"])]
    result["delta"], result["histogram_delta_100us"] = delta, bins
    if len(bins) != 17 or min(bins) < 0 or min(delta.values()) < 0:
        issues.append("Incomplete, wrapped or reset counters")
        return result
    if (min(delta.values()) == 0 or abs(delta["blocks"]-per_frame*delta["frames"]) >= per_frame
            or abs(delta["draw_wakes"]-delta["frames"]) > 1 or abs(delta["blocks"]-delta["ready"]) > 3):
        failures.append("Stalled frame/block/draw progress or inconsistent counts")
    if not sum(bins) or sum(bins) != delta["ready"]:
        issues.append("The observed histogram does not account for all accepted refills")
    def bound(frac):
        upto = 0
        for i,n in enumerate(bins):
            upto += n
            if upto >= sum(bins)*frac and n:
                return [100*i,100*(i+1)-1 if i < 16 else None]
        return None
    result["p99_bin_us"], result["p99_9_bin_us"] = bound(.99), bound(.999)
    result["epoch_max_refill_us"] = last["max_refill_us"]
    result["epoch_worst"] = last["worst"]
    result["epoch_max_queue"] = last["max_queue"]
    result["epoch_min_sw_lead_us"] = last["min_sw_lead_us"]
    result["epoch_min_draw_gap_us"] = last["min_draw_gap_us"]
    if last["max_refill_us"] > 1600:
        failures.append("Epoch refill exceeded 1600 us")
    if last["min_sw_lead_us"] == 0xffffffff or last["min_draw_gap_us"] == 0xffffffff:
        issues.append("Minimum lead or drawing gap has no observation")
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("observations", type=Path)
    args = p.parse_args()
    records = [json.loads(line) for line in args.observations.read_text().splitlines()]
    try:
        result = score(records)
    except (KeyError, TypeError, ValueError) as e:
        result = {"physical_deadline":"unverified", "incomplete":[f"Invalid observer schema: {e}"], "failures":[]}
    result["software"] = "failed" if result["failures"] else "incomplete" if result["incomplete"] else "observed within checks"
    print(json.dumps(result,indent=2))
    return 0 if result["software"] == "observed within checks" else 1


if __name__ == "__main__":
    raise SystemExit(main())
