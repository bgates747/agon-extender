# Pinwalk evidence checkpoint

The [result record](../../HW-002-2026-09-07-23-11-02Z.md) records the Author's
accepted PASS and the retained acquisition-length discrepancy.

`logic.sr`, acquisition log/exit status, original run parameters, tool hashes
and prepared-build manifest are byte-for-byte copies of the supplied local
run. The binary and generated build-identity header match the prepared-build
manifest. `capture-at-run.py` was recovered and verified against the exact
recorded acquisition-time source hash. The Pi helper and both retained
analysis sources also match `tool-hashes.json`. These are immutable evidence
copies; maintained fixture code lives in the owning task directory.

`capture-environment-public.txt` is an explicitly labeled projection of the
original environment record, omitting its machine-local USB bus location.
Its hash is therefore different from the private original. `SHA256SUMS`
belongs to this committed bundle, not the original acquisition directory.
The `.sr` archive contains only channel/rate metadata and logic samples.

`capture-integrity.json`, `pinwalk-analysis.json` and `post-capture-review.json`
were added during review. They retain the original incomplete-acquisition
verdict alongside passing pulse counts. `acceptance.yaml` records the later
Author disposition without rewriting those earlier reports.

To replay pulse analysis from this directory, use the project's Python:

```text
../../../../../../.venv/bin/python analyze_header_pinwalk.py logic.sr \
  --expect PC0:D1:1 --expect PC1:D6:2 --expect PC2:D3:3 --expect PC3:D4:4 \
  --expect PC4:D5:5 --expect PC5:D2:6 --expect PC6:D7:7 --expect PC7:D0:8
```

Do not execute the archived capture runners. The analysis sources are retained
from `agon-extender-legacy` under GPL-3.0-only; see the
[preserved license notice](../../../../../../docs/tasks/HW-002/pinwalk/LICENSE).
