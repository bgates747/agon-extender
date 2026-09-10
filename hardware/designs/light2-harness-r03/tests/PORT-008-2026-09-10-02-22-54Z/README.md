# First ordinary ExCom console accepted

The Author accepts this as a major project milestone: ordinary ExCom operation
with native USB keyboard input and retained EDP browser output, using the
existing UART-only harness. EMOS remains the owner of activation and ordinary
VDU routing. Browser input and parallel transport were not required.

The P4 log records successful PREPARE/COMMIT, LEAVE, and another PREPARE/COMMIT.
There is one startup and no recorded panic or console fault. This, together
with the Author's working-console observation, closes N002's reproducible
activation crash after the retained mode/context initialization correction.
The log was stopped gracefully and preserved without resetting either board.

Significant browser display latency remains visible. Current full-frame RGB888
snapshots are deliberately limited to five per second. Performance improvement
and wider retained VDP fidelity remain subsequent work; they do not negate this
accepted functional milestone. N001's native reference rendering issue remains
separate. Individual unreported editing checks and a second Legacy return are
not implied by acceptance of this run.

`result.yaml` records exact identities, observed transitions, acceptance and
limits. `observations.txt` contains control/startup lines and final counters.
The full private capture is hash-bound in the result and retained locally.
Firmware identities remain candidates; no version or registry status is changed.

## Additional Author gameplay observation

The Author clarified that this session also included playing Nurples with
EDP rendering on the P4 and native USB keyboard input. Apart from the browser's
five-fps presentation, the game looked great by the Author's visual assessment.
This extends the milestone beyond CLI output to a real game's graphics and
input through the retained VDP implementation and EMOS-owned UART transport.
It is an operator gameplay observation, not a frame-by-frame comparison or
a claim of complete VDP compatibility; the exact game binary was not captured
in this run's manifest. Firmware and capture identities remain unchanged.
