# BENCH-019 cold rehearsal r02 stopped at the mainboard programmer

The new chat checkout and verified SD staging passed. The mainboard installer
lost the serial connection before it reported a write. The fresh operator
stopped, alerted Smith and kept its reservation. All later physical phases
remain unrun. This run leaves the procedure in draft.

| Phase | Actual outcome |
| --- | --- |
| Reservation | Request accepted at 22:27:33 EST, acknowledgment at 22:27:56, slot open at 22:28:20. Ordinary direct chat exchange. |
| Staging | Parent exit 0 after 157.5 s. Verified the fixture and four EMOS support files, preserved the previous result, and closed the foreground listener. |
| Mainboard install | Parent exit 1 after 5.3 s with the worker and group joined. The programmer verified the ESP32 MAC, the live partition table and the app0 selector. The next invocation returned esptool exit 2 during connection, with no erase or write progress and no app readback. Actual classic ESP32 boot and app state after the stop are unverified. |
| Remaining phases | P4 and EMOS writes, fixture invocation, collection, production handback and check-in were not reached. The cold operator retained sole custody. |

The operator used the documented phase commands. The remaining inherited
discovery included local hardware and legacy custody references and a mailbox
read. The operator did not write a local bench helper. The successful ordinary
slot-open does not exercise the deferred FIFO cases.
[Durable operator log](../../../agents/bench019/rehearsal-r02/OPERATOR-LOG.md) ·
[Original programmer failure](../../../agents/bench019/rehearsal-r02/operator-run/install-mainboard/write.log)

## Programmer correction

The frozen r02 code at `60dd9f10` ran each esptool command in its own
process. The last successful command read OTA metadata and then closed the
serial connection. The separate write process attempted to connect with
`no_reset` and got no serial response. Espressif’s local esptool 4.12
implementation also exits its stub when invoked with `--after no_reset`.
The evidence shows that this sequence failed across a connection boundary.
The exact electrical or loader condition at the failed reopen is unknown.

The follow-up uses one connection and stub for the live layout and selector
reads, application write and independent readback. It retains the commissioned
esptool 4.12 environment, records the dispatch boundary, and limits the write
to the confirmed app0 range. It disables the library's automatic write replay.
Offline tests cover the single-loader sequence and the refusal to write a
mismatched layout. Hardware qualification is still required.

An authorized recovery can first verify the retained production app and return
to ordinary CLI using the commissioned route. Reconcile the pending firmware
record from actual evidence before resuming the rehearsal. Keep this failed
attempt and its original process receipts. Follow the draft's stop rule while
Smith's direction is pending.

## Smith-authorized mainboard retry

Smith reset Agon through the ordinary P4 web reset route, confirmed a working
MOS prompt and Extender keyboard, and authorized one mainboard reattempt in
the cold operator's chat. The continuation uses the same manifest, config,
operator and evidence root, with the phase `retry-mainboard`. It requires the
original named failure and joined worker, retains that pending-write record's
provenance, and verifies the full prior production application extent before
allowing the candidate write. The retry has its own evidence and a distinct
parent receipt. A successful retry permits the next listed phase,
`install-p4`. A retry failure stops under the same rule.

The authorized mainboard retry passed in 88.9 s. The loader read the exact
prior production extent, independently matched all 1,130,496 bytes of the
candidate write, and the commissioned Agon restart returned to a working MOS
CLI. The original failure receipt is retained.
[Mainboard retry](../../../agents/bench019/rehearsal-r02/operator-run/retry-mainboard/independent-verification.json)

The next phase connected to the P4, matched its live partition table and
app0 selector, then stopped before entering esptool's write routine. The
adapter had made an unknown flash-size ID fatal, although the commissioned
esptool 4.12 `keep` path retains the programmer defaults in that case.
The follow-up restores that behavior within the verified app0 bounds and
records write intent separately from actual dispatch to esptool. The original
worker joined with exit 1 after 1.0 s. Its final P4 boot state remains
unverified. The operator sent Smith the question alert and retained custody.
EMOS, fixture invocation, and production handback remain pending.
[P4 programmer log](../../../agents/bench019/rehearsal-r02/operator-run/install-p4/programmer.log)

After Smith directs recovery and the P4 has returned to a working CLI, an
explicitly authorized P4 reattempt can use `retry-p4` with the same arguments
and evidence root. It requires the original joined failure and verifies the
entire prior production extent before it calls the candidate write.
