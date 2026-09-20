# Mode transition reproduction — 2026-09-20

Author authorizes a bounded check of QUAL-003-I006 on the installed key-query
candidate. First compare CLI-selected modes 8 and 20 with continuous production
browser streaming, then with no video observer. Observe actual frame header
sizes, browser canvas dimensions and P4 display status separately. This initial
control uses ordinary EMOS CLI VDU commands, not a new eZ80 fixture; no new
firmware, build identity, startup edit or game modification. Preserve initial
mode and restore a usable ExCom prompt with neutral input; close the observer.

If the simple control passes, inspect the historical Nurples trigger and retained
failure evidence before claiming resolution. No old firmware reflash merely to
reproduce history. Any code correction requires an evidenced cause and bounded
contract update. A pass on idle CLI transitions alone does not close the issue.

The simple CLI control passed. Continue with the exact retained cadence60.bin
from the historical failure, hash-verified against its archived source artifact,
streaming on then off. Its existing internal mode switches are the behavior
under investigation, an explicit exception to startup-only test-mode selection;
do not create or modify a fixture to introduce them. Host orchestration and
receipts use separate /test/mt-* files, leave autoexec byte-identical, save the
existing benchmark/telemetry regions, and return through the maintained SD
service. Bound each run to 150 seconds; timeout stops rather than resets.

First game run produced all 1,800 records, no VDU faults, about 144 seconds of
application intervals; the 150-second whole-run bound was insufficient with
loading/exit/retrieval. Normal Escape and CLI recovery required no reset. Use a
210-second bound for the no-video comparison based on that measured runtime.
Record the timing discrepancy separately; do not expand into performance repair.
