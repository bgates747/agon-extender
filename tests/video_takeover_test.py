"""Shared adapter regression entry point; real translation units, fake IDF only.

The consolidated harness preserves short-write/failed-stop and takeover cases
and adds actual raw fragmentation, credit, stop/restart and provider failures.
"""
from pathlib import Path
import subprocess
ROOT = Path(__file__).resolve().parents[1]

def main():
    subprocess.run(["bash", str(ROOT / "tests/network/run_http_video.sh")], check=True)

if __name__ == "__main__":
    main()
