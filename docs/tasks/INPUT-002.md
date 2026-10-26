# INPUT-002 — Deterministic controller traffic and latency attribution

The controller now works, but the Author observes excessive delay. A repeatable
Oryx packet source will let us measure host scheduling and P4 acknowledgement
separately from EMOS delivery, application polling and visible drawing. Clock
alignment must report its uncertainty before we use cross-processor timestamps
as one-way latency measurements.

## State and authorization

On 2026-10-26 the Author authorized a small Oryx background application generating
deterministic timed packets, followed by the largest useful unattended tranche
of the proposed latency investigation. The Author required this task and a
commit/push before implementation. This task extends [INPUT-001](INPUT-001.md);
it does not replace that task's transport, admission or acceptance contract.

The controller viewer was reported working by the Author after the corrected
installation. No calibrated end-to-end latency result exists. The bench last
belonged to an independent human wireframe comparison; its availability must
be coordinated before controller traffic or application invocation.

## Scope and ownership

1. The Oryx Python source generates repeatable axis trajectories and optional
   ordered button transitions through the existing host-to-P4 controller UDP
   protocol. It does not synthesize Linux input events or require the F310.
2. The Oryx source records monotonic intended deadlines, actual sends, datagram
   identities and ACK receipt times. The Pi coordinates bounded campaigns and
   retains provenance, start/end duration, completion and failure results.
3. The P4 receiver admits one source through its existing HTTP interface, stores
   latest axes and ordered transitions, and acknowledges reception. Existing
   ACKs prove P4 storage, not EMOS consumption or visible output.
4. Extender MOS continues to own processor transport and application access.
   The eZ80 application uses the supported gateway, never raw UART/register
   access. Mainboard VDP and normal startup remain unchanged.
5. The investigation distinguishes Oryx scheduling, network/P4 acknowledgement,
   P4-to-EMOS delivery, application sampling and presentation. It reports
   non-comparable scopes separately, including rates versus latency.

## Bounded research précis

1. [LAN controller contract](../protocols/controller-lan.md) and
   `scripts/controller_udp.py` own the admitted sender and packet codec. Existing
   STATE/ACK datagram sequences permit host round-trip correlation. Existing
   ACKs contain no P4 timestamp, so they cannot establish clock offset or
   one-way Oryx-to-P4 latency. An HTTP status observation is not a packet-arrival
   timestamp.
2. [EMOS controller contract](../protocols/controller-emos.md) and
   `tests/fixtures/controller/` own the gateway/viewer. The viewer requests at
   most every two raw MOS clock units and redraws every six: nominally 60 and
   20 Hz in mode 20. A 20 Hz redraw can add up to 50 ms before visible output.
   Source inspection and measurements must distinguish that from transport lag.
3. P4 receiver implementation is under `vdp/video/extender/input/controller/`.
   The exact installed composition is identified in the ignored bench record;
   compare it with maintained source before attributing behavior to installed
   firmware. Inspect task/socket scheduling and cache age at each boundary.
4. Consult official `../../agon-docs` before eZ80 API/timer changes, then
   read-only `../../agon-mos` or `../../agon-vdp` where implementation matters.
   [Game timing](../testing/game-timing.md) and
   [render timing](../testing/render-load.md) retain PRT1 ownership and wrap
   constraints. The nominal MOS clock is not a fine timestamp: it advances
   two units per physical VBlank, not once every 1/120 second independently.
5. Clock alignment follows the four-timestamp exchange described by
   [RFC 5905](https://www.rfc-editor.org/rfc/rfc5905.html). Fit monotonic offset
   and drift without setting any participant's clock. Report timer resolution,
   responder processing, residual round trip, path-asymmetry bounds and drift
   uncertainty. P4's [ESP timer](https://docs.espressif.com/projects/esp-idf/en/latest/esp32p4/api-reference/system/esp_timer.html)
   has microsecond resolution; that is not microsecond synchronization accuracy.
   Chaining Oryx–P4 and P4–eZ80 mappings adds uncertainty.

## Work items and validation

1. Implement a finite, explicitly invoked Oryx source with a deterministic
   schedule. Skip missed slots instead of sending catch-up bursts. Default to
   axes-only traffic so an idle EMOS consumer cannot fill the P4 edge queue.
   Expose rate, duration, pattern and timeout explicitly; preserve the admitted
   source's exclusivity and fail on rejected admission or stale ACKs.
2. Reuse the existing packet codec. Record sequence/deadline/send/ACK events,
   missed deadlines, source state and effective cadence. Reject impossible or
   mismatched ACKs. Handle signals with bounded shutdown and explicit close;
   never automatically reconnect, restart or take over another source.
3. Add proportionate deterministic tests for pattern repeatability, missed-slot
   behavior, admission/fault/timeout handling and ACK correlation. Exercise a
   local UDP/HTTP receiver for transport semantics and timing plumbing. Do not
   label the local receiver as physical P4 evidence.
4. Deploy a fingerprinted source package to Oryx without replacing the physical
   sender or user input services. Run finite host-only/loopback measurements,
   retain logs and summarize median, p95 and worst timing in milliseconds.
   Write a reproducible background launch/stop recipe; no boot service/autostart.
5. Review the exact installed receiver/viewer sources and identify measurable
   scheduling limits. After exclusive bench availability is established,
   compare the same deterministic traffic at selected rates against existing
   P4 firmware, restoring source ownership afterward. Do not reset, flash or
   run an Agon application merely to obtain these host/P4 ACK measurements.
6. Implement and test offline clock-fit/uncertainty analysis where useful.
   Specify the smallest timestamp probes needed for the remaining processor
   boundaries. Existing packet formats must not be silently extended. EMOS
   has only 270 resident ROM bytes free in the latest installed build; prefer
   bounded application-owned diagnostics over resident growth. Firmware/API
   changes require a concrete reviewed design and identified candidate before
   deployment; no new deployed version is inferred from this task.
7. Update this task, current controller guidance and the dated development log
   with findings, exact source identities, test scopes, retained evidence and
   remaining gates. Keep raw machine endpoints and device identities ignored.

## Decisions and execution boundaries

| ID | Decision | State / reason |
|---|---|---|
| I2-D01 | Reuse admitted UDP controller traffic; start axes-only | Selected implementation choice; isolates latency without unconsumed button overflow |
| I2-D02 | Use monotonic timestamps and report uncertainty; do not set clocks | Selected investigation method; wall-clock synchronization is unnecessary |
| I2-D03 | Finite explicit background runs, no service/autostart or automatic takeover | Selected implementation choice; preserves source and bench ownership |
| I2-D04 | Further timestamp probe layout and eZ80 timebase | Unresolved until installed-source review and initial measurements; propose the smallest justified extension |
| I2-D05 | Prepare a priority4 UDP worker as a bounded scheduling control | Experimental source choice under investigation authority; preserves eight-packet budget/2ms block and all wire formats; build only until deployment identity is agreed |

Follow the [test lifecycle](../procedures/test-appliances.md) and
[execution protocol](../procedures/test-execution.md). Never edit `/autoexec.txt`.
No CRC or substitute software checksum is added to E/VDP–EMOS traffic. Do not
claim end-to-end or photon latency from ACKs. Do not disturb another application's
bench reservation, replace mainboard VDP, silently upgrade selected production,
or leave an indefinite synthetic controller source running after a campaign.

## Results

The task and preceding owned dirt were committed/pushed before implementation
in Extender `b96c8d52` and EMOS `1dafee0`; installed P4 source `27d93dcc` was
also published on its retained branch. The finite source/campaign and offline
clock-bound analyzer are implemented. Forty-one host/core checks pass, with
fourteen new probe/clock checks also passing on Oryx. Local socket controls and
bounded Oryx/Pi-to-P4 campaigns completed; no Agon application was invoked.

[First results](INPUT-002/RESULTS-2026-10-26.md) identify substantial delay/loss
before EMOS. The exact P4 blocking/scheduling point remains unproven. A minimal
priority4 source control is committed against the installed P4 composition.
The canonical indexed-PPA builder requires an approved `indexed-hdmi` revision
even for compilation and refuses the unversioned sentinel. Its build therefore
awaits the Author's version decision; no target build or flash is claimed.
No new firmware identity, flash, production selection or downstream timing
claim is implied. Remaining work is the identified P4 scheduling comparison,
then justified timestamp probes and EMOS/application/presentation attribution.
