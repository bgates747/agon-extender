# Focused browser typing hardware ready

The Author reported a successful EMOS flash. Its consumed SD payload matches
the frozen v0.1.9 candidate; this is not an independent eZ80 flash-memory
readback. Same-build EMBOOT and the identified BTYPE candidate are installed
with the test-only autoexec. The card is safely unmounted and all rollback
images remain intact.

The paired P4 candidate was written and independently verified. Startup shows
its exact candidate identity, expected 1152000/8N1 UART wiring and the HTTP
service ready after DHCP. No browser key exchange was performed by the agent.
The private deployment logs retain device identity, flash/verify commands and
full startup output. This record retains a sanitized excerpt.

Insert the SD into Agon and reset once. Refresh the browser page, Connect,
then Capture keyboard. The operator checks editing, focus loss/reacquisition,
repeat and Escape/MOS return using the r01 sheet. No analyzer capture is
required for this interactive step. Physical typing is still pending.
