# Retained-parser output-fault fixture feasibility record

- Status: Runtime fixture blocked; bounded source/composition guards implemented
- Date: 2026-09-01
- Owning task: [PORT-008](../../../PORT-008.md)
- Decision boundary: `PORT-008-D002`

## Outcome

The requested host fixture cannot currently instantiate the maintained P4
retained-parser closure without replacing the display and target behavior whose
observable result the fixture is meant to test. No substitute parser, fake
`Context`, copied packet encoder, or older emulator VDP was presented as the
real fixture.

This is an executable-seam blocker, not a finding that the production
`ExtenderVdpStream` fault latch is ineffective. The existing host suite executes
that production Stream and data-plane core. The new bounded guards described
below cover its behavior at every byte offset in the retained parser's
source-derived General Poll plus Mode Information write trace. They also cover
the local P018 advertised-read contract and P019 record-admission/quarantine
boundary. They do not run `VDUStreamProcessor`, the P4 display closure, or a
target binary.

## Maintained source contracts inspected

1. `vdp/video/vdu_stream_processor.h` constructs
   `inputStream` as `std::shared_ptr<Stream>(input)`. The parser therefore adopts
   and assumes deletion responsibility for the raw `Stream *`; a fixture must
   allocate the `ExtenderVdpStream` on the heap and must not delete it
   independently.
2. The same header's `writeByte()` calls `outputStream->write(b)` and ignores the
   return value. `send_packet()` writes the response code, length, and each
   payload byte through separate `writeByte()` calls.
3. `vdp/video/vdu_sys.h` consumes General Poll input bytes
   `23, 0, 0x80, echo`, emits `0x80, 1, echo`, sets `initialised`, and then has
   `wait_eZ80()` emit Mode Information. Mode Information is `0x86, 8` followed
   by little-endian canvas width and height, character width and height, colour
   depth, and video-mode number.
4. The local parser and packet functions are the official VDP v2.16.0
   implementations from commit `c7ac293d2aa81ddfa693390549bcd909069c8fc3`.
   The local diffs in `vdu_stream_processor.h`, `vdu_sys.h`, `vdu.h`, and
   `context.h` add P4 include/device guards; they do not alter the constructor,
   `writeByte()`, `send_packet()`, General Poll, startup-wait, or Mode
   Information functions described above.
5. The non-release P4 top level obtains a heap `ExtenderVdpStream` from
   `beginP4ParallelNonreleaseQualification()` and passes that pointer to the
   real `VDUStreamProcessor`. This target ownership composition is correct, but
   it does not make the parser executable on the host.

## Why a host fixture would be a substitute today

1. Constructing `VDUStreamProcessor` immediately constructs the real
   `Context`. Its header includes every retained VDU command family and
   `agon_screen.h`; there is no parser-only `Context` or display interface that
   a host test can bind.
2. With `AGON_EXTENDER_P4_BOOT`, that closure selects the project P4 Canvas,
   `P4DisplayController`, `P4FrameService`, and screen facade. The closure uses
   ESP-IDF heap, timer, FreeRTOS task, and semaphore APIs. The task-local host
   compatibility header supplies only the Arduino `Stream` surface needed by
   `ExtenderVdpStream`; it cannot instantiate the target display/runtime.
3. Defining `USERSPACE` does not solve the target-closure problem. The available
   emulator builds its own `vdp-quark` subtree and selects classic FabGL
   display, input, and audio paths. Even if the current parser files were
   substituted into that build, the resulting display observable would not be
   the maintained P4 target observable. Emulator changes would also require
   the separate human validation gate.
4. The current target-only `VisibleCaptureReturn` records bytes but exposes no
   fail-at-byte control. Adding such a control and a queue-injection entry point
   requires edits to the non-release target composition outside this bounded
   test-directory tranche, followed by a target execution.
5. `wait_eZ80()` branches on the real reset reason and uses global
   `initialised` and global context state. A repeatable fixture needs an
   authoritative cold-start/reset binding and a fresh runtime for each injected
   byte offset; a test-local reimplementation of those globals would not test
   the retained target startup path.

## Bounded evidence added now

1. `tests/test_retained_parser_source_contract.py` checks the maintained source
   structure for Stream adoption, ignored write results, byte-at-a-time packet
   output, General Poll ordering, startup Mode Information, packet codes and
   payload fields, and the non-release top-level ownership wiring.
2. `tests/p4_data_plane_tests.cpp` drives the real production
   `ExtenderVdpStream` and `P4ParallelDataPlane` with the source-derived 13-byte
   General Poll plus startup Mode Information shape and representative fixed-
   mode payload values. In a fresh fixture for each offset it makes that one-
   byte output call fail, requires the exact accepted prefix, requires
   `kOutputShortWrite`, and proves the data-plane owner does not arm or assert
   `READY_N` after the fault. It does not claim those representative payload
   values were emitted by a parser run.
3. These two guards are compositional. They can expose a source-boundary drift
   or a downstream false-green, but neither proves that the real parser emitted
   the trace, that the target linker consumed a declared object, that a target
   display changed, or that EMOS observed or rejected readiness.
4. Focused host interleavings prove that `available()` or `peek()` reserves
   exactly one real queued byte for the retained parser. A fault before any
   advertisement blocks all reads; a fault after advertisement permits that
   one byte and then restores the normal `-1` sentinel. This corrects P018
   without allowing a faulted parser to drain the remaining queue.
5. The record admission check and cancellation store share one sequentially
   consistent atomic order. If cancellation wins, no queue-head publication is
   admitted. If the record wins, its later head store may complete, but Stream
   fault gating quarantines it and post-commit fault/cancel/lease checks prevent
   `kRecordQueued`. This corrects P019 without a blocking spin between the
   higher-priority parser and ingress service task.

## Required runtime fixture

The blocker is removed only by a fixture that executes the maintained P4
parser/display closure rather than reconstructing it. A target-native
non-release fixture is the smallest credible route unless an independently
accepted host binding for the P4 runtime is created later.

1. The fixture initializes the actual target display in one fixed safe mode,
   supplies an authoritative non-software-reset startup condition, creates the
   production SPSC queue/fault/cancellation objects, heap-allocates the
   production `ExtenderVdpStream`, and gives that exact pointer to
   `VDUStreamProcessor`.
2. A qualification-only injector places exact General Poll bytes
   `23, 0, 0x80, 1` into the production SPSC queue. The real parser executes
   `wait_eZ80()`. A no-fault baseline must capture exactly the three-byte Poll
   response followed by the ten-byte Mode Information response derived from
   the initialized display state.
3. The same baseline next queues a safe explicit mode command and a visible
   sequence, for example `22, 0, 12, 'A'`. The real parser must emit the second
   Mode Information packet, consume the complete sequence, and produce a
   frozen cursor/context observation plus a stable logical-frame or RGB888
   snapshot hash. The owning display qualification must select and freeze the
   exact observable; this record does not invent its value.
4. A fresh target runtime repeats the sequence for every global output-byte
   offset: three General Poll bytes, ten startup Mode Information bytes, and
   ten explicit-mode Mode Information bytes. The qualification capture accepts
   the exact prefix and returns zero for the selected one-byte write.
5. Every fault run must report `kOutputShortWrite`, publish cancellation, stop
   admitting new parser input, release `READY_N` and the forward direction,
   produce no later return-channel write, and never report a post-fault
   `kRecordQueued`. A byte already advertised to the retained parser remains
   consumable exactly once. A complete record whose admission edge won before
   the fault may remain quarantined in the queue but may not be reported as
   post-fault success. The fixture must record that reserved byte, the exact
   unconsumed queue suffix, and the deterministic parser/display checkpoint
   appropriate to whether the fault occurred before or during the explicit
   mode command.
6. “No false readiness” at this D002 boundary means the P4 ingress owner admits
   no further record and releases its physical readiness/direction controls.
   The fixture cannot claim EMOS readiness, response delivery, MOS sysvar
   effects, activation confirmation, or formal-mode rejection; those remain
   outside the forward-only composition.
7. Target logs must identify the selected mode, expected byte trace, injected
   offset, accepted prefix, fault, cancellation observation, control release,
   queue remainder, and display oracle. The normal run and all fault offsets
   fail closed on a missing field or timeout.

## Removal condition and authorization boundary

The immediate blocker is resolved when either:

1. an authorized target-only qualification seam can inject SPSC input and one
   capture failure offset while executing the existing retained parser and P4
   display objects; or
2. an accepted host P4 runtime binds those same maintained target semantics
   without replacing `Context`, the display facade, frame service, or parser
   globals.

The first option is recommended because it changes only non-release
qualification code. It still requires separate approval for implementation
outside this directory and for any flash, reset, deployment, or hardware run.
Until then, PORT-008 must not cite the bounded guards as completion of the real
retained-parser output-fault fixture.
