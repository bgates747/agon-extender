#!/usr/bin/env python3
"""Read-only probe for the BENCH-019 Extender VDP firmware."""

import argparse
import json
from urllib.request import urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_url", help="The bench's existing Extender HTTP origin")
    args = parser.parse_args()
    status_url = args.base_url.rstrip("/") + "/display/status"

    for digit, expected in ((3, 9), (5, 25)):
        with urlopen(f"{status_url}?bench019={digit}", timeout=5) as response:
            result = json.load(response)
        if result != {"bench019_p4": expected}:
            raise SystemExit(f"P4 FAIL input={digit} expected={expected} got={result!r}")
        print(f"P4 PASS input={digit} value={expected}", flush=True)


if __name__ == "__main__":
    main()
