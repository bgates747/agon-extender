#!/usr/bin/env python3
"""Offline four-timestamp clock bounds. Never changes clocks or sends traffic.

Input rows [a_send, b_receive, b_send, a_receive] use integer nanoseconds on two
independent monotonic clocks, converted from native units BEFORE this analysis.
Error bounds cover each timestamp's quantization/read uncertainty. A drift
prior is mandatory: these are feasibility bounds under an affine clock model,
not an accuracy guarantee or a statistical confidence interval.
"""
import argparse
import json
import math
from pathlib import Path


def bounds(rows, *, error_a_ns, error_b_ns, max_drift_ppm):
    if not rows or len(rows) > 1024:
        raise ValueError('Require 1..1024 four-timestamp exchanges')
    if any(isinstance(v, bool) or not isinstance(v, int) or v < 0
           for row in rows for v in row) or any(len(row) != 4 for row in rows):
        raise ValueError('Timestamps must be nonnegative integer nanoseconds in four columns')
    for v in (error_a_ns, error_b_ns, max_drift_ppm):
        if not math.isfinite(v) or v < 0:
            raise ValueError('Timestamp errors and drift prior must be finite and nonnegative')
    if max_drift_ppm >= 1_000_000:
        raise ValueError('Drift prior must keep clock rate positive')
    if any(a4 < a1 or b3 < b2 for a1, b2, b3, a4 in rows):
        raise ValueError('Reversed exchange or unhandled timer wrap/reset')
    # Subtract integer origins BEFORE floating point; long uptimes retain ns.
    anchor_a = (min(r[0] for r in rows)+max(r[3] for r in rows))//2
    anchor_b = rows[0][1]
    lower = [(b3-anchor_b-error_b_ns, a4-anchor_a+error_a_ns)
             for a1, b2, b3, a4 in rows]
    upper = [(b2-anchor_b+error_b_ns, a1-anchor_a-error_a_ns)
             for a1, b2, b3, a4 in rows]
    rate_min, rate_max = 1-max_drift_ppm/1e6, 1+max_drift_ppm/1e6
    # For every lower/upper pair: c-rate*x <= d-rate*y. Intersect
    # their constraints on rate. No assumption of symmetric network delay.
    for c, x in lower:
        for d, y in upper:
            coefficient, limit = y-x, d-c
            if coefficient > 0:
                rate_max = min(rate_max, limit/coefficient)
            elif coefficient < 0:
                rate_min = max(rate_min, limit/coefficient)
            elif limit < 0:
                raise ValueError('No feasible clock model within timestamp error bounds')
    if rate_min > rate_max:
        raise ValueError('No feasible affine clock model within drift prior/error bounds')
    # Conservative enclosing interval. Retaining rate/offset correlation would
    # tighten it, but must never turn network asymmetry into false precision.
    offset_min = max(min(c-rate_min*x, c-rate_max*x) for c, x in lower)
    offset_max = min(max(d-rate_min*y, d-rate_max*y) for d, y in upper)
    residual = []
    for a1, b2, b3, a4 in rows:
        residual.append(dict(min_ns=max(0, (a4-a1)-2*error_a_ns-
                                       (b3-b2+2*error_b_ns)/rate_min),
                             max_ns=max(0, (a4-a1)+2*error_a_ns-
                                       max(0, b3-b2-2*error_b_ns)/rate_max)))
    return dict(model='B = anchor_b + offset + rate * (A - anchor_a)',
                anchor_a_ns=anchor_a, anchor_b_ns=anchor_b,
                offset_min_ns=offset_min, offset_max_ns=offset_max,
                offset_width_ns=offset_max-offset_min,
                rate_min=rate_min, rate_max=rate_max,
                drift_min_ppm=(rate_min-1)*1e6, drift_max_ppm=(rate_max-1)*1e6,
                error_a_ns=error_a_ns, error_b_ns=error_b_ns,
                prior_max_drift_ppm=max_drift_ppm, exchanges=len(rows),
                minimum_residual_round_trip_ns=min(r['min_ns'] for r in residual),
                scope='Conservative clock feasibility bounds; affine model, nonnegative paths, stated errors/prior')


def map_interval(model, a_ns):
    """Conservative B interval for one exact A timestamp, in ns."""
    delta = a_ns-model['anchor_a_ns']
    terms = [delta*model['rate_min'], delta*model['rate_max']]
    return (model['anchor_b_ns']+model['offset_min_ns']+min(terms),
            model['anchor_b_ns']+model['offset_max_ns']+max(terms))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path, help='JSON list of four-timestamp rows')
    parser.add_argument('--error-a-ns', type=int, required=True)
    parser.add_argument('--error-b-ns', type=int, required=True)
    parser.add_argument('--max-drift-ppm', type=float, required=True)
    args = parser.parse_args()
    try:
        result = bounds(json.loads(args.input.read_text()), error_a_ns=args.error_a_ns,
                        error_b_ns=args.error_b_ns, max_drift_ppm=args.max_drift_ppm)
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(1, str(exc)+'\n')
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
