# Consumer admission investigation: sequencing findings

A host command-sequencing hazard is identified, and existing MOS `EXEC`
sequencing passes a bounded live ROM-save/listener handback check. The consumer's
original timeout is not conclusively reproduced. The separate post-reset input
failure remains unexplained; no P4 or EMOS patch is justified by these results.

## Saved consumer sequence

| Event | Retained observation | Meaning |
|---|---|---|
| Foreground listener transfers | Startup/listener download and explicit EXIT pass | Useful new staged transfer path worked |
| `SAVE` then host types listener | Next command submission starts3.643888355s after SAVE typing starts; no MOS-completion check between them | Host waits for P4 key emission, not foreground command return |
| Saved ROM | Later retrieved as exact128KiB84da2c5a without repeating SAVE | SAVE completed; this does not prove its following command was intact |
| First ordinary reset | Input epoch changes; readyfalse through deadline | Boundary occurred; actual input admission not proved |
| Paired recovery | Clean P4 initialization then ordinary Agon reset restores actualCLI/ROM read | Recovery succeeds; no diagnosis of prior P4 state |
| Post-install ordinary recovery | One100ms pulse admits input in9.792s;97 mainboard capture bytes | Distinct from first recovery; native warning alone is not P4-worker evidence |

Saved source: Golem's `entry.py` sends SAVE and immediately calls its listener
helper; its `ops.py` finishes a key command after P4 emission and cancellation.
Stock MOSv3.0.2, clean official commit
`8336409351ee5314e02801a7b72a4f1bb5282519`, stores latest key state/count and
its editor waits for a new event. It does not buffer complete subsequent CLI
lines during a SAVE. Official contracts are
[Keyboard input](../../../../../agon-docs/docs/mos/Keyboard.md) and
[sysvars](../../../../../agon-docs/docs/mos/API.md); implementation detail is
[the editor](../../../../../agon-mos/src/mos_editor.c) and
[key publication](../../../../../agon-mos/src/vdp_protocol.asm).
The host sequencing hazard is established from source, while attributing this
particular timeout to overwritten keys remains an inference without the original
CLI trace. Golem owns consumer-helper changes; Extender reports the exact
correction rather than modifying the consumer project.

## Existing correction and bounded live validation

`scripts/flash_firmware_commit.py` already stages an independent command file
containing SAVE then explicit foreground listener startup and invokes EXEC once.
Reuse that ordering alone, not the helper's flash/reset operations. MOS then
starts the listener only after SAVE returns. A listener HELLO plus exact ROM
retrieval establishes useful handback; a timer or emitted Enter does not.

Under the Author's repair/testing authorization, Extender runs one such independent
EXEC with new support/evidence paths, on the exact restored native mainboard and
installed P4r27/EMOSv27. Maintained joined-control mainboard USB capture and a
verified printer-mirror sentinel record command order. P4 USB remains unopened.
The batch reaches listener startup, and the new staged client retrieves131072B
matching full EMOS SHA256
`84da2c5ac3cebb1c470bab201f797a936296a6bfc33b6ebdbcf5d1dd3a1d1d79`.
Fresh-session EXIT, unchanged startup/listener, mirror-off, visible/flashing
cursor commands, input/controller readiness, idle staged job and ownerless USB
ports pass. No firmware, video mode, startup, wiring, PCM or reset is changed.
The capture is instrumentation, not a performance comparison. Raw traces,
command/state journals and byte evidence are indexed in the machine-local bench
record. This is one successful sequence, not proof that all command/reset cases
are fixed or that a failing control has been reproduced.

## Input status limits and remaining diagnosis

The exact installed P4 snapshot confirms layout clears readiness and advances
the input epoch; ordered poll plus drained TX commits readiness. A five-second
TX-stall branch awaits new admission; a separate latched failure stops the UART
worker until P4 reset. Neither branch is identified in Golem's original event
without corresponding P4 markers. The status reason is the first termination
reason of its session: an explicit host cancellation can leave reason1 through
later layout/transport boundaries. It is not a fresh transport-fault register.
A changed epoch, reason1 and HTTP availability therefore cannot discriminate
those branches. Do not replace firmware merely on that evidence.

B10-R03 retains the separate unexplained reset issue. Next discriminating work
must correlate actual P4 worker state with mainboard boot/admission and preserve
known observer behavior; no forced PCM replay, speculative new diagnostics,
startup edit or firmware patch is selected by this report.
