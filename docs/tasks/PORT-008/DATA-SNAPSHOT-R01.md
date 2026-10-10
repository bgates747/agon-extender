# PORT-008 — Inspect received data before echo

## Executive summary

The bounded check is complete. P4 retained bytes already differ from the expected
pattern before echo, and return output also disagrees with the directly observed
stored first byte. This is not solely an Agon sampling problem. No remedy yet;
review native RX publication, TX DMA/output and the newly reported harness
signal-integrity difference before another hardware run.

Author approved the next bounded investigation after the
[clock/handshake capture](PINWALK-R02.md): inspect P4-retained bytes before
echoing them, separating receive/storage corruption from transmit corruption.
Use the same existing ordinal fixture and full HDMI EDP base. No rewiring,
EMOS/mainboard VDP change, broader repair campaign or production promotion.

DS01 [x] — Add a private, bounded data-only endpoint snapshot after a matched
successful receipt and complete reciprocal UART restoration. Capture length,
direction, a whole-buffer FNV-1a32 fingerprint, and first/last 16 bytes. Emit one
USB console line per completed block, outside DMA/clock/handshake critical
sections. No counters, ISR logging, per-byte transport hooks, altered payload,
changed completion criteria or public service. Check endpoint lifecycle and
fingerprint against known host vectors; build/verify the full HDMI composition.

DS02 [x] — Install/readback-verify the identified P4 image. Preserve the exact
previous data-only image as rollback without another firmware backup. Establish
input readiness before invoking anything; verify fixture/startup over the
ordinary UART listener. Use fresh SD result/invocation paths.

DS03 [x] — Run exactly one existing 3456-byte forward/echo fixture, collecting
bounded raw POSIX USB output and the unchanged physical probe map. Compare the
P4 forward snapshot to the exact expected bytes/fingerprint, compare its reverse
snapshot for retained-buffer changes, and retain Agon's whole-echo result.
No uncertain payload replay. Do not infer wire or stored-buffer correctness
from callback status alone. Snapshotting changes the experimental composition;
retain identities and the prior uninstrumented failure as control evidence.

DS04 [x] — Retrieve evidence, verify original startup/input/listener recovery,
record attribution and remaining limits, then stop before implementing a remedy.
If RX storage is wrong, review RX/DMA/publication next; if the retained bytes
match, review TX/DMA/pad output next. A hash alone is not an exact byte dump;
first/last bytes provide direct bounded observations and a collision limit
remains for the fingerprint. No hardware acceptance or production claim.

Research reuses [data-only control](DATA-ONLY-CONTROL-R01.md),
[native payload contracts](NATIVE-PAYLOAD.md), and the pinned official references
there. No new MOS or wire API is introduced. `ParallelControl::takeCompleted`
requires UART phase and a matched completed receipt. `P4NativePayload::finish`
publishes RX bytes after stopping DMA and releasing pads. The private endpoint
owns retained storage until its next offer. Maintained code locations:
`p4_parallel_data_check.hpp`, `parallel_control.hpp`, `p4_native_payload.cpp`,
and `console_hardware.inc` under `vdp/video/extender/transport/`.

## Result — one completed run, integrity failure

Full HDMI P4 `port-008-data-r02-b2026-10-10-04-14-34Z`, app SHA256
`86f112f59d641de85c2061e94955223f080d9df9c38b0c94be93c91e208db6ce`,
installed and all four flash segments independently verified. Frozen source
comparison against the prior data-only image changes only the endpoint and
console snapshot publication. EMOS, mainboard VDP, mode, original startup and
MOSlet remain unchanged. Twelve host lifecycle/bounds/direction cases pass
under AddressSanitizer and UndefinedBehaviorSanitizer, including independent
known FNV-1a32 `hello` vector. LeakSanitizer was disabled because the host
sandbox uses ptrace; it is not claimed as tested.

The same 3456-byte ordinal fixture ran once. Agon reports status 0 and intact
guards for both directions, but reverse mismatch starts at byte0. These statuses
prove neither integrity nor strict qualification.

| Observation | Expected | P4 / captured result | Meaning |
|---|---|---|---|
| Whole-buffer FNV-1a32 before echo | `40f2c165` | `12bdae25` | At least one retained RX byte already differs |
| Whole-buffer FNV-1a32 after echo | `40f2c165` | `12bdae25` | Same fingerprint; no observed intervening storage change |
| First/last 16 stored bytes, both snapshots | All `ff` | All `ff` | Direct bounded stored-byte agreement |
| First return byte D7 | High, since stored byte is `ff` | Low for the entire 138-sample byte cycle | Return output disagrees with stored first byte |
| Payload clocks, forward / reverse | 3456 / 3456 | 3456 / 3456 | No missing/extra qualified clocks in this run |
| READY high at payload clock edges |0 /0 |0 /0 | Receiver-ready observed throughout |
| Observed forward data 2/4/5/6/7 | No mismatch | No mismatch | Five observed bits match at both analyzed sample positions |
| Observed reverse data 2/4/5/6 | No mismatch | No mismatch | D7 remains the observed return fault |

At one microsecond after rising CLOCK, reverse D7 has 590 mismatching samples,
first byte 0 through last byte 728. At two analyzer ticks after falling CLOCK,
400 mismatches extend to byte 832. These are two sampling positions in one
trace; differing counts show intra-cycle changes, not separate runs. Sampling
is nominal 24 MHz, uncalibrated. Unprobed data 0/1/3 and analogue behavior remain
unresolved. The received-buffer mismatch could arise during acquisition, DMA
visibility or CPU publication; this test does not locate its earliest point.
The additional first-byte discrepancy requires reviewing TX DMA visibility,
configuration and pad output rather than assuming RX corruption explains all
return errors. Equal hashes cannot prove identical full buffers; unequal hashes
do prove a difference under the checked algorithm. No wiring defect is declared.

Acquisition passed: 480 million samples/20 nominal seconds; exact extent verified.
USB collection plus capture/retrieval took 26.17 host seconds, separate from
firmware build/install/preflight. Full capture archived and extraction hash
verified. Raw USB open/close did not change input epoch; no collector errors.
One Agon preparation reset after installation; no reset/replay during the run.
Original 38-byte startup readback matches, listener exited, input ready/neutral
with held 0/pending 0. Bench idle; current snapshot image remains installed.

Fresh SD invocation `/extender/install/p8walk03.txt` and result
`/agents/extender/results/P8W03.CSV` are consumed evidence, not retry targets.
Ignored local `agents/port008-live-qualification/data-snapshot-r01` retains
source/build manifests, host test, flash verification, USB log, CSV, complete
24MHz trace, reproducible analysis and result/handback records. Previous
[uninstrumented capture](PINWALK-R02.md) remains the control. Production unchanged.

## Author-reported harness difference — 2026-10-10

The earlier DevKit arrangement placed Agon header contacts directly on the
breadboard, with short, aligned routes and approximately 200–220 ohm series
resistors between data-line endpoints. The Author recalls both nominal values;
exact resistor value is not independently verified here. The current P4-PC
sits off the breadboard, uses leads roughly twice as long, and has no such
data-line series resistors. Preserve the separate pull-resistor requirements;
series damping and pull resistors serve different purposes. These are operator
observations, not measured cable lengths or analogue qualification.

Signal integrity is therefore an unresolved competing explanation, alongside
native DMA visibility/publication and output configuration. Correct digital
clock counts and stable samples at the Agon header do not establish voltage
margins or clean edges at the P4 receiver. A wrong retained RX buffer does not
by itself establish a software fault; a wrong return wire does not distinguish
P4 drive/configuration from electrical behavior. The first-byte discrepancy
remains real, but causal attribution is open.

Possible discriminating controls for Author review: preserve one firmware/fixture
pair and change only series damping or lead length, one variable at a time;
alternatively inspect waveforms at the receiving endpoint with an oscilloscope.
Neither rewiring, resistor installation, additional tests nor new equipment
use is authorized by recording this observation. No further bench operation.
