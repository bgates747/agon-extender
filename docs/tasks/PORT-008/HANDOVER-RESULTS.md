# PORT-008 F02c1 — Handover development results

## Executive summary

The private EMOS/P4 ownership sequencers pass paired simulated-wire checks
and target compilation. The linked EMOS code also passes instruction-emulator
checks. Unequal endpoint delays exposed a reset-during-arming race; the corrected
P4 code cancels that arming operation before acknowledging readiness. Removing
the guard reproduces opposing output drivers in the model.

The bench was not accessed. No UART/ISR/startup path invokes this code, and no
ExExt activation or production promotion is implied. F02c1 is complete;
F02c2 next owns actual admission, UART suspension and boot/interrupt integration.

## Results

| Check | Result | What it establishes |
|---|---|---|
| Paired ownership sequencers | 5,208 cases pass | Both directions, unequal adapter/task delays, repeated blocks, release failures, missing peers, reset/cancel at every step, quiescence withheld until shift-register/packet boundary, queued input ordering |
| Negative control, arming guard removed | Fails as expected | Harness detects EMOS UART mask `0x05` opposing P4 parallel mask `0xFF` after EMOS reset during delayed P4 arming |
| Compiled eZ80 sequencer | 16,392 cases pass | Host/target transition agreement, init/begin/cancel, C ABI, IX/SP/IFF and memory guards; each call returns within the bounded instruction check |
| Existing paired reverse block cores | 48 cases pass | Prior byte/edge/bounds/failure behavior unchanged |
| Existing reverse core in new linked image | 38 cases pass | Earlier receive behavior survives relinking |
| Existing EMOS parallel checks | 9 tests pass | Existing forward binding, lifecycle and UART ownership guards retained |
| P4 profile checks | 11 tests pass | Maintained profile selection constraints retained |
| Complete EMOS wrapper `firmware-check` | Pass | Required firmware, UART divisor, parallel, keyboard, console, ABI and VDU guards |
| Native P4-PC console/browser build | Pass, followed by corrected-unit incremental rebuild and maintained validation | Actual target compilation and manifest/action/pin checks; no runtime invocation |

The linked EMOS image is **129,626 bytes**, an increase of **430 bytes** over
the preceding reverse-core checkpoint, leaving **1,446 bytes** below the
131,072-byte image limit. This includes dormant development code. It is not
a new accepted firmware or a throughput measurement.

## Useful findings

FIND-01 — A single READY level cannot distinguish the preceding block from a
fresh handover. The candidate uses held release/acknowledgement phases and a
fresh return round trip before restoring UART outputs.

FIND-02 — EMOS can reset while P4's asynchronous arm operation is pending.
P4 must recheck the original CLOCK/VALID grant before publishing readiness.
The retained negative control demonstrates why the guard is necessary.

FIND-03 — After a successful block, EMOS can request return before P4 samples
the intermediate released VALID-high level. In that specifically post-block
state, P4 accepts CLOCK-low/VALID-low directly: its own pads are already
released. Requiring the intermediate sample caused a timeout under unequal
delays. The fresh request is still acknowledged and held.

FIND-04 — Reset during admission can lose the phase/session distinction.
The modeled deadline cancels and repeats recovery rather than publishing a
successful payload. The eventual UART status must match the current
session/sequence/direction/length; GPIO levels alone cannot provide identity.

## Reproduction and evidence

Run from Extender:

```sh
.venv/bin/python tests/parallel_handover_test.py
.venv/bin/python tests/parallel_reverse_test.py
```

Set `HANDOVER_VECTORS` to a host output filename to retain all 8,192 EMOS
transition vectors. With a canonical wrapper-built EMOS image and its `nm.txt`,
run from the EMOS checkout:

```sh
cargo run --offline --release --manifest-path tests/uart_put_cpu/Cargo.toml \
  --bin parallel_handover -- IMAGE_DIRECTORY HOST_VECTOR_FILE
```

[Machine-readable evidence](HANDOVER-RESULT.json) records source hashes,
source-head identities, final artifacts, check results and local-log hashes.
[Timed reruns](HANDOVER-DURATIONS.json) record UTC start/end and host-monotonic
elapsed seconds for the final host and cached instruction checks. These are
host test durations, not calibrated eZ80 or link performance measurements.
Ignored `agents/port008-handover` retains builds, vectors, the negative control
and logs. The initial complete P4 wrapper build preceded the final arming
correction. Its manifest is explicitly retained as `initial-build-manifest.json`;
the corrected source was rebuilt through ESP-IDF and revalidated using the
maintained validator. `incremental-check.json` records those final artifact
hashes and the verified source snapshot. Neither is a production selection.

The ownership harness models adapters and payload progress. Actual UART
registers, ISR arrival, peripheral teardown, GPIO timing and electrical
contention remain untested. Keyboard evidence uses the existing queue in a
simulated suspension; no real keyboard-latency claim. The CPU harness executes
linked instructions rather than a full-system Fab boot. All new changes remain
uncommitted for Author review; unrelated EMOS application-peer work is untouched.
