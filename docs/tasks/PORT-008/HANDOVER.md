# PORT-008 — Shared-pin handover candidate

## Executive summary

The private EMOS and EDP sequencers now express a complete setup/return
handshake using the existing READY/CLOCK/VALID wires. Their adapters remain
simulated: ordinary UART, ISR, boot and keyboard code are unchanged. This is
development evidence for F02c1, not electrical qualification or enabled ExExt.
The next increment must connect real admission, UART suspension and reset
fences before any GPIO activation.

## Ownership and sources

EMOS owns CLOCK/VALID and requests each transaction. P4 owns READY. Port C's
eight lanes carry the selected direction only after the handover. The mode
coordinator must validate an ExExt admission with matching session, sequence,
direction and exact length before calling either `begin` function. No UART
opcode is assigned or parser changed by this increment. Neither sequencer
owns or publishes payload integrity/completion to applications.

| Implementation | Role |
|---|---|
| Sibling `agon-emos/src/emos_parallel_handover.c` and `.h` | Four-byte EMOS state; transition function requests completed-adapter operations, holds CLOCK/VALID phase levels |
| `vdp/video/extender/transport/p4_parallel_handover.cpp` and `.hpp` | P4 counterpart, holding READY phase levels |
| `tests/parallel_handover_test.cpp` and `.py` | Executes both maintained implementations together with delayed adapters and output-enable checks |
| Sibling `agon-emos/tests/uart_put_cpu/src/bin/parallel_handover.rs` | Executes the actual wrapper-linked EMOS instructions, including its C ABI |

Hardware references are unchanged: official `agon-docs/docs/GPIO.md`, the
Zilog register contract already retained in the development précis, and the
[current P4-PC harness](../../../hardware/designs/light2-p4pc-harness-draft/README.md).
CLOCK's physical pull-down and VALID/READY pull-ups agree with reset levels.
No reference checkout was changed. No new pins, wires or ICs are requested.

## Normal entry

All values are logic levels. Rows describe held phases, not timed pulses.
The adapter must acknowledge completing its operation before its sequencer
advances. During setup PARLIO is disarmed; setup CLOCK changes are not bytes.

| Phase | CLOCK | VALID_N | READY_N | Driver permission / action |
|---|---:|---:|---:|---|
| UART | 0 | 1 | 1 | EMOS PC0/PC2; P4 PC1/PC3; the other data lanes input |
| Drain | 0 | 1 | 1 | Both serializers fenced against new output; drain existing packets and shift registers |
| EMOS release request | 0 | 0 | 1 | EMOS has released all eight pads; P4 must finish draining/releasing |
| P4 release acknowledgement | 0 | 0 | 0 | Both endpoints' data pads input |
| EMOS acknowledges | 0 | 1 | 0 | Neither endpoint drives data |
| P4 clears acknowledgement | 0 | 1 | 1 | Neither endpoint drives data |
| EMOS grants arming | 1 | 1 | 1 | P4 may arm receiver, or drive the reverse block; EMOS remains input |
| P4 ready | 1 | 1 | 0 | P4 arming complete; EMOS may arm its selected direction and start the block |
| Payload | toggles | 0 | 0 | Exactly one eight-bit output owner; EMOS generates byte clocks |

This extra READY high phase separates pad release from payload readiness.
Task polling must not miss an unacknowledged pulse. Within payload, the prior
block cores still require latched VALID edges and final-byte hold; the phase
sequencer does not replace those details.

P4 rechecks CLOCK high/VALID high before publishing an asynchronous arming
completion. EMOS reset can withdraw that grant while the adapter is arming.
Without the recheck, READY low could falsely acknowledge released pads to
the rebooted EMOS while P4 was actually driving all eight lanes. A negative
control removing the guard reproduces opposing UART/parallel output enables
in the paired test; retaining the guard passes the reset sweep.

## Return and recovery

| Phase | CLOCK | VALID_N | READY_N | Required preceding completion |
|---|---:|---:|---:|---|
| Block stopped | 1 | 1 | 1 | P4 has stopped DMA and disabled its data outputs; EMOS block runner has returned |
| EMOS released | 0 | 1 | 1 | EMOS disabled all data outputs; P4 observes this before proceeding |
| Fresh release request | 0 | 0 | 1 | EMOS observed READY high after its own release |
| Fresh release acknowledgement | 0 | 0 | 0 | P4 acknowledges release for this return phase |
| EMOS UART restored | 0 | 1 | 0 | EMOS restores only PC0/PC2 UART/RTS outputs; P4 data outputs remain disabled |
| P4 UART restored | 0 | 1 | 1 | P4 restores only PC1/PC3 UART/RTS outputs; queued traffic can resume |

In the post-block state P4 accepts CLOCK low/VALID low directly. EMOS may
observe the already-high READY and move from its released level to the fresh
request before the P4 task runs again. Requiring P4 to sample the intermediate
VALID high caused an avoidable timeout under unequal task delays. Accepting
the request is safe specifically here because P4 has already stopped and
released its data outputs; it is not a global interpretation of those levels.

On cancellation the local sequencer first requests stopping/releasing its
adapter. **It does not change the control level to advertise a release that
has not completed.** P4 then holds READY low as a recovery announcement until
EMOS reports CLOCK low/VALID high. P4 raises READY and both endpoints perform
the fresh release round trip above. A release failure holds the endpoint
fenced. There is no fixed delay after which either CPU assumes ownership.

On reset the reset CPU's physical output enables must first become inputs,
not merely its RAM state. EMOS starts with CLOCK low/VALID high and requests
release; P4 requests release and announces recovery as above. Tests reset one
endpoint while retaining the other's exact state. If reset occurs during
entry, old admission can be indistinguishable from the start of recovery;
the phase deadline cancels that admission and forces another handshake.
That is allowed recovery latency, not successful payload delivery. The future
resumed-UART status must match the fresh transaction; GPIO levels cannot carry
a session/sequence identity. Neither current UART boot path uses these fences
yet, which prevents physical activation of this candidate.

## Adapter requirements for F02c2/F02c3

| Requested action | Completion the real owner must supply |
|---|---|
| Fence/drain | Freeze new serializer submissions, retain queued input, complete any existing packet; software TX queue empty **and** UART shift register empty, RX parser at a complete packet boundary |
| Release | Stop/abort the owned peripheral, stop the block clock if local, mask all competing UART/RTS/ISR writers, explicitly disable all eight pad outputs |
| Arm | Direction and descriptor validated; exact bounded buffer retained; selected peripheral armed; opposing endpoint has acknowledged release |
| Run | Invoke the existing bounded block runner; it owns byte CLOCK/VALID and block READY while running |
| Restore | Only the UART subset is enabled, after reciprocal release; preserve keyboard parser/state and queued press/release order on normal suspension |
| Live | Resume serializer submissions; validate the matching transaction result before publishing success |

Completion bits are operation-local. Clear old acknowledgements on every new
operation **and on cancellation**, even if the action enum is the same. An
adapter must not publish `released` after merely requesting DMA stop. EMOS
must hold its existing atomic lifecycle/writer lock; these transition functions
are single-owner routines, not locks. Short atomic mux/ISR transitions must
preserve IFF; the block must remain interruptible. `QUIET` cannot be fabricated
by clearing a queue or flushing UART RX. Reading eZ80 LSR acknowledges error
bits, so the eventual drain adapter must preserve that sampled error outcome.

The caller supplies a per-phase elapsed deadline and stalled-clock fuse,
and invokes cancellation on failure. These functions contain no blocking
wait and do not define physical timing. If cleanup cannot complete, stay
fenced; recovery does not imply resubmitting a failed block. Ordinary UART
startup and all competing writers must be audited before these adapters are
connected. A normal pause preserves keys; a CPU reset cannot promise to retain
the reset CPU's RAM queue.

## Verification scope

The paired harness tests both directions with zero/one/three-step EMOS adapter
delays and independently zero/one/three/nine-step P4 adapter delays, repeated
transfers, withheld shift-register/packet-boundary quiescence, absent peers,
nested admission refusal, failed
release, and reset/cancel of either endpoint at each step of a successful
exchange. Every modeled output-enable change asserts non-overlapping ownership.
It also exercises the existing `UsbKeyQueue` through suspension and resumption,
preserving press/release order. This is adapter-contract evidence; the actual
console loop and UART ISR have not been modified or simulated in full. Payload
progress is modeled in this sequencer harness; the earlier real block cores
have their separate retained paired tests. This is not an integrated peripheral
or complete ExExt emulator.

The linked CPU test compares 8,192 host-generated transition vectors under
each interrupt-enable state, plus explicit init/begin/cancel checks. It checks
memory guards, bounded instruction return, IX/SP/IFF and actual byte-return
ABI. IY is caller-clobbered in the existing AgonDev C ABI, as recorded in EMOS
INTEG-014 E07. These vectors check host/target agreement; independent behavior
comes from the paired harness, not from treating identical C as two oracles.

Neither test establishes GPIO settling, PARLIO alignment, peripheral abort
behavior, electrical fault tolerance, throughput or real keyboard latency.
Run results and exact artifact hashes are retained in the adjacent
[handover results](HANDOVER-RESULTS.md).
