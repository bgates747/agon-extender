# PORT-008 LC03-B — Fixed-count RX qualification

The renewed repair hour made partial progress: physical forward transfers of
one and two bytes now pass, but the 255-byte case fails reproducibly under
independent hardware edge proof. The full paired suite remains incomplete.
A separate warm-reset ambiguity was reproduced; a proposed correction failed
another reset phase and was preserved, then removed from maintained source.
Keyboard access and the original startup are restored. Production and mainboard
VDP are unchanged. The next useful check is an independent CLOCK/VALID trace,
not relaxed acceptance or arbitrary filtering.

The Author authorized 2026-10-10 01:26:35–02:26:35 UTC. This record follows the
frozen [earlier repair](LIVE-QUALIFICATION-BLOCK-R03.md). Exact identities,
artifact/evidence hashes and handback are in the [receipt](LIVE-QUALIFICATION-BLOCK-R04.json).
Only the private parallel qualification pair was deployed.

## RX mechanism and research

1. The exact passing PRX-06 receiver was recovered from legacy commit
   `4626fcc`; its SHA256 matches the retained fixture manifest:
   `0e0f76c0b252ebba0f61ebd74390ec086e95a163b1ba32c4c57e294a1a0969c5`.
   It used external clock, eight-bit data, falling-edge/LSB reception,
   active-low VALID, fixed 1024-byte EOF and `free_clk=true`. This proves that
   configuration at 1024 bytes, not every small record size.
2. Pinned IDF5.5.5 (`b774170ff46c393eeb5e495ea37936038d3f4f4f`)
   `components/esp_driver_parlio/src/parlio_rx.c:228–234` selects RX_FULL EOF
   for positive `eof_data_len` (bytes), versus EN_INACTIVE at zero. RX now
   selects exact admitted byte-count EOF and `free_clk=true`, retaining actual
   DMA callback identity and exact length.
3. A fixed EOF alone cannot reject extra clocks or prove VALID ended. Two
   independent P4 PCNT units count N falling CLOCK edges while VALID is low
   and two VALID edges from initial to final high. P4 freezes/rechecks CLOCK
   first while VALID counting remains live, then freezes/rechecks VALID.
   Both directions retain the 2,000 ms capture bound, matched UART completion
   and completed cleanup before publication. P4 provides four PCNT units;
   this private RX path uses two. GPIO interrupt pulse sampling is not proof.
4. P4 LL `components/hal/esp32p4/include/hal/parlio_ll.h:346–352` documents
   two AHB/core clock cycles for asynchronous FIFO reset synchronization.
   The passing predecessor supplied inactive clocks before payload. The r09
   fixed-EOF image still timed out, so EMOS now supplies sixteen inactive
   clocks **forward only**, before enabling Port C output or asserting VALID.
   Reverse must not preclock: P4 TX lacks VALID gating and would consume data.
   Sixteen is an empirical diagnostic choice, not a proved hardware minimum
   or established explanation for the missing callback. The existing sixteen
   inactive end clocks remain.
5. Source review found no minimum four-byte or 64-byte receive record.
   P4 LL accepts bit lengths divisible by eight; IDF explicitly stages buffers
   shorter than their DMA alignment and retains exact descriptor lengths.
   DMA burst size is a maximum, not a source-stated record minimum. Hardware
   small-record behavior still requires the physical fixture.

## Software checks

| Check | Passing cases | Scope |
|---|---:|---|
| PCNT VALID / gated CLOCK | 70 | Exact counts, inactive clocks, pending VALID, wrap/ISR delay, stop races, faults |
| Actual P4 native leaf | 209 | Both directions, small/boundary lengths, callbacks, two-counter freeze race, cleanup |
| Actual P4 block coordinator | 315 | Native operation and release/status orchestration |
| Paired EMOS/P4 coordinator | 82 ordinary +111 private | Actual owners with modeled SDK/register boundaries |
| Linked actual eZ80 instruction execution | 124 | Forward-only preamble, exact bytes/tail, registers, IFF, READY loss and guard refusal |

These are correctness checks, not electrical or throughput measurements. Full
identified P4 build validation and EMOS firmware guards remain mandatory. The
new preamble moves the unchanged forward Port C DDR write under a new local
assembly label; the link inventory was updated to that exact owner, retaining
its register-write count and all caller/interrupt checks.

## Installation and physical outcome

| Component | Installed identity | Verification / limit |
|---|---|---|
| P4 private browser probe | `port-008-probe-r10-b2026-10-10-01-45-13Z` | Four flash segments independently verified; not HDMI or production |
| EMOS private probe | `agon-emos-v0.1.24-b2026-10-10-01-48-39Z` | Complete 128 KiB ROM readback matches; 131,017 image bytes / 55 free |
| Diagnostic MOSlet | Unchanged `parprobe.bin`, 10,750 bytes | Full SD readback matches retained build |
| Startup | Original 38 bytes | Restored and full readback verified after each failed attempt |

Two fresh-session suite invocations each passed the first two cases and stopped
at the third. The remaining 17 cases, including every reverse case, did not run.
The 255-byte result was provisional and rejected; no successful P4 completion
receipt or CRC is claimed for it. Each failure was followed by a separate reset
and evidence collection, with no automatic replay of an uncertain block.

| Forward length | First run | Second run | Agon elapsed, nominal 120 Hz ticks |
|---|---|---|---|
| 255 bytes | Rejected, status 35 | Rejected, status 35 | 604 / 604 |
| 1 byte | Pass, matching receipt/CRC | Pass, matching receipt/CRC | 6 / 6 |
| 2 bytes | Pass, matching receipt/CRC | Pass, matching receipt/CRC | 6 / 4 |

Failures are listed first. MOS ticks are uncalibrated and include the complete
service/handshake; these small records do not establish sustained payload
throughput. P4 complete-service receipts for one/two bytes were 22,606/22,809 µs
in the first run and 21,584/21,711 µs in the second. Their scope differs from the
MOS tick interval and they must not be presented as native link transfer time.

A stable-UART preflight reset separately failed at boot phase 2 before invoking
the fixture; it is retained as informative warm-reset evidence. Recovery from
that held phase restored input. Final nonmutating handback checks verify ready,
neutral keyboard input, no held/pending keys, offline SD service and no pending
job after the USB collector closed. No test, transfer, collector, build, reset or
flash remains active. The installed pair above is retained; LC03-B/F03 remain
open and production selection is unchanged.

Local informative bundles: `lc03i` (fixed-count candidate without preclocks),
`lc03j` (identified preclock pair and first run), `lc03k` (independent confirmation
and final handback), and `lc03l` (uninstalled rejected boot candidate), under
ignored `agents/port008-live-qualification`. These are evidence, not executable
retry or installation instructions.


## F03 warm-reset ambiguity — reproduced, remedy proposed

A warm Agon reset from stable UART can leave P4 in `recoveryClear` (phase2),
READY high and EMOS at C0/V1. A separate Agon reset from that held phase can
complete the handshake, but this is a recovery workaround, not fault
qualification. The missing fresh reset indication is independent of the
native payload EOF repair.

A bounded model compiled the actual EMOS/P4 boot pad adapters and handover
cores, with only SDK/register boundaries faked. ASan/UBSan passed. It reproduced
EMOS at UART while P4 remained fenced in phase2 across 7,000 logical
millisecond poll timestamps, without a P4 restore or overlapping data drivers.
The model, source hashes and timestamped receipt are retained under ignored
`agents/port008-live-qualification/warm-reset-model-r04`; no physical timing is
claimed. Existing adapter tests include an artificial EMOS timeout/retry, which
can conceal this held state and does not represent an already-granted EMOS
startup UART session.

1. Stable UART and the EMOS boot fence both advertise C0/V1 with READY high.
   EMOS therefore consumes the old READY high as release acknowledgement and
   requests C0/V0 before P4 can observe a distinct reset announcement.
2. P4 detects C0/V0, fences its pads and drives its initial READY-low announcement.
   EMOS consumes that low as the acknowledgement of its request, restores UART
   and raises VALID before P4 observes the intervening request level.
3. P4 consumes C0/V1 and enters phase2 with READY high. EMOS consumes that high
   as peer completion and grants UART. Neither endpoint now generates the
   transition the other requires. Periodic handshake rewinds or elapsed-time
   UART grants would reuse levels and do not supply fresh reciprocal proof.
4. Proposed boot-only contract: EMOS first releases Port C and advertises C1/V1;
   P4 observes that distinct live-control loss, fences and holds READY low;
   EMOS must observe that low before advertising C0/V1. The existing P4
   READY-high release acknowledgement, EMOS C0/V0 request, P4 READY-low
   acknowledgement and reciprocal UART restore then follow. Ordinary block
   return must retain its separate established sequence. Implementation and
   validation remain open; no such firmware change is installed.
5. Required regressions must start from a genuinely live pair, reset only EMOS,
   vary endpoint polling and pause each endpoint across every new transition,
   and prohibit automatic retries from masking a stall. Also cover cold boot,
   P4-only reset, missing/stuck peer, ordinary block return and restore faults.

## New 255-byte edge-count failure — unresolved

The private r10 P4 image with the forward-only EMOS preamble completed forward
records of one and two bytes. Two independent fresh-session attempts then
rejected the 255-byte forward record with these P4 observations:

| Attempt | Actual DMA callbacks | DMA bytes | Qualified CLOCK count | VALID edge count |
|---|---:|---:|---:|---:|
| First | 1 | 255 | 256 | 4 |
| Second | 1 | 255 | 256 | 10 |

These are PCNT observations, not an independent electrical trace proving extra
physical transitions. The exact DMA callback length does not establish that
the CLOCK/VALID proof succeeded. The additional counts correctly prevent
publication of a completed block receipt.

1. A bounded review of the EMOS native wrapper and coordinator found no second
   native invocation or post-leaf control write explaining these counts. The
   wrapper leaves the handover control flags at C1/V1, and the block exclusion
   flag remains set through the operation. No overlapping SD pin assignment was
   identified in this review. These negative findings do not establish signal
   integrity at either endpoint.
2. Review of the pinned IDF PCNT driver and P4 counter adapter found no scalar
   arithmetic path that adds one to 255 or changes two VALID edges into four
   or ten. A new PCNT unit stops and clears its hardware count and clears its
   interrupt status; the adapter clears again and checks initial zero/high.
   `pcnt_unit_get_count()` returns the hardware count plus the accumulated
   overflow count. With the configured high limit of 32767, high-limit ISR and
   pending-interrupt compensation add 32767, not one or two. This review did
   not identify a stale-unit, channel-lifecycle or overflow explanation.
3. The unresolved distinction is between additional transitions reaching the
   P4 inputs and an input/peripheral sampling artifact. The next discriminating
   check should send a deterministic known 255-byte pattern and capture CLOCK
   and VALID at both the EMOS outputs and P4 inputs, comparing falling CLOCK
   edges while VALID is low and VALID transitions with the two PCNT counts and
   actual DMA callback. It must also check received bytes against that pattern.
   Preserve exact count and callback rejection; do not relax the proof or add
   an arbitrary glitch filter without measured evidence and focused regression.

Source scope: EMOS `src/emos_parallel_native.c` and
`src/emos_parallel_coordinator.c`; P4
`vdp/video/extender/transport/p4_valid_counter.hpp`; pinned IDF
`components/esp_driver_pcnt/src/pulse_cnt.c` (unit allocation, clear/count read
and interrupt accumulation). No hardware trace or corrective filter experiment
was performed by this source review.


### Fresh-boot candidate rejected after reset-during-ACK regression

A bounded candidate made the EMOS boot fence hold C1/V1 until READY low,
returning WAIT without changing controls while the old READY high remained.
The EMOS portion passed 740 paired adapter cases, including warm reset from a
live pair with P4 polling delayed up to 2,000 logical milliseconds. A matching
P4 boot-only candidate then restarted its released fence on CLOCK high in later
recovery phases. The compiled EMOS candidate was 131,035 bytes, with 37 ROM bytes
free; it was not deployed.

A stronger actual-adapter regression then reset EMOS while P4 held its old
READY-low acknowledgement in phase3. EMOS consumed that stale low and lowered
CLOCK before P4 polled. P4 therefore never observed the new C1 indication,
accepted C0/V1 as old restore proof, and ultimately left EMOS at UART while P4
remained fenced in phase2 for 7,000 logical millisecond timestamps. ASan/UBSan
passed; this is a deterministic scheduling counterexample, not a GPIO timing
measurement. A level-only initial low is insufficient fresh epoch proof.

The rejected source/test snapshots, exact candidate patch, source hashes and
counterexample receipt remain under ignored
`agents/port008-live-qualification/warm-reset-fresh-candidate`. Only the four
candidate files authored in this attempt were restored to their preceding
contents: EMOS boot adapter and exact instruction test; P4 boot adapter and
paired adapter test. Earlier payload/boot repairs and the original failing
warm-reset reproduction remain intact. The installed r10/preclock pair remains
the physical candidate; no rejected boot image was flashed. A complete fresh
transition protocol and all-phase asynchronous-reset tests remain F03 work.

## Next trace readiness

A host-only check at 02:25 UTC found the installed `sigrok-cli` and one
eight-channel `fx2lafw` physical logic analyzer. No acquisition was performed.
Its current lead mapping to EMOS CLOCK/VALID outputs and P4 CLOCK/VALID inputs
is not verified; historical UART analyzer maps must not be reused by assumption.
Verify that mapping before the next deterministic 255-byte capture. The current
repair authorization ends at 02:26:35 UTC; a further execution window remains
a separate Author decision.
