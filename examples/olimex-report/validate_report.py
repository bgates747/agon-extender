"""Semantic validator for the OLXRPT offline example."""
import json
from pathlib import Path
import sys

archive, witness, path, token = sys.argv[1:]
expected = f"OLXR1 {token}\nReport lifecycle example\n".encode("ascii")
accepted = Path(archive).read_bytes() == expected
print(json.dumps({"accepted": accepted,
                  "reason": "example payload matches" if accepted else "example payload differs"}))
