# Firmware qualification authority

## Executive summary

This directory owns formal qualification of an exact installed P4/EMOS pair.
The native HDMI and browser-video profiles have explicit output oracles; neither
can silently skip the other's checks. The runner never writes `/autoexec.txt`,
flashes firmware or launches a test through reset. Host-only preparation is
available while the bench is occupied. The [combined native release preflight](../docs/tasks/RELEASE-001/BENCH-PREPARATION-R01.json)
records verified live staging and CLI handback. The
[first native full invocation](../docs/tasks/RELEASE-001/QUALIFICATION-R01.json)
stopped at the post-reset actual-CLI gate: 1/25 checks, remaining cases blocked.
Readiness and recovery do not establish physical qualification.

## Qualification policy

1. Preserve verified installation evidence for both exact images. The offline
   `installation.py` adapter checks the artifact against the independent full
   readback, build manifest and complete source archive/inventory. For P4 it also
   compares the full preimage outside the application erase sectors. EMOS can
   honestly identify an archived patch; its base commit alone is not its source.
   These schema-2 receipts prove retained installation, not the current board.
2. Before hardware invocation, the operator establishes exclusive bench access,
   a verified idle **Legacy** CLI with admitted neutral input, current paired
   identities, the commissioned reset bridge, required directories and the
   accepted Legacy spoken-cue files. The current physical recipe supports only
   single-buffered entry modes. It fails for double-buffered entries rather than
   silently substitute a mode or claim that a final swap makes future typing live.
3. One complete `run.py` invocation must pass all 25 automated checks across
   three mandatory cases, restore both saved modes and the entry Legacy route,
   preserve startup byte-for-byte, verify temporary support-file cleanup and
   complete its spoken/visible notification. Startup is read-only evidence.
4. The Author then completes all manual cases declared by the output profile.
   `review.py` binds those actual observations to the exact complete run and its
   summary hash. Automated success is labelled `awaiting-author-review`; a
   targeted `--case` run cannot qualify firmware. Feature acceptance already
   recorded remains evidence, not a substituted full-suite pass.

Builds, host simulations, retained installation proof and physical observations
remain distinct. No zero-hardware command reports hardware qualification. The
separate `offline.py` source suite is a development gate, not a replacement for
this installed-pair run. Historical task fixtures are evidence, not launchers.

## Required physical coverage

| Case | Checks | Common coverage |
|---|---:|---|
| Integrated P4/EMOS smoke | 13 | Browser assets/reset bridge, actual CLI/readmission, Legacy/ExCom, text/display status, profile output oracle, checksum-free SD round trip, cleanup and ordinary boot |
| Mode transaction | 7 | Committed modes 8→20→8, profile-specific second sequence, normal boot/handback |
| Raw SD API | 5 | Separately pinned fixture, verified staging, unique completion token plus later MOS prompt, guarded write/read/restore, unchanged startup |

| Output profile | Output and mode oracles | Required Author review |
|---|---|---|
| `browser-video` | Three fresh decoded WebSocket frames; second 8→20→8 sequence retains a video connection and checks decoded geometry | Representative loaded assets, mode switch and visible clean exit |
| `native-hdmi` | Valid carrier/DMA clock and advancing frame-complete count with zero fault counters; second 96→20→96 sequence requires fresh rendered text/prompt and DMA progress at every edge; no `/video` request | Loaded assets/mode switch/exit, plus physical aspect, centering, colours and motion in representative standard20/wide96 modes |

HDMI counters prove scanout progress and fault status, not the pixels on a
monitor. Late/over-budget counters are retained diagnostic measurements; DMA
fault, underrun, block/sequence/cache/overlap errors fail the automated check.
Keep keyboard and controller attached for the bounded combined-build review;
credit the existing accepted controller exercise. This is not the full rendering
or performance campaign and does not qualify every mode/controller or hotplug.

The raw-sector case is destructive within a narrowly guarded region: the app
requires an MBR proving sector2 precedes the first partition, retains its preimage,
then restores through MOS's independent C dispatch and verifies every byte. Its
local buffer CRC summaries are SD test oracles, not processor-link checksums.
The Pi launches LOAD/RUN explicitly after confirmed native mode20 (512×384) or
browser mode3 (640×240), followed by monitor settling. It
waits for the app's unique post-I/O completion token followed by a MOS prompt
before starting the result listener. Missing completion, changed boot identity
or unverified restoration blocks input, notification and subsequent cases; no
reset or retry is inferred from a timeout.

## Offline preparation

Use the repository virtualenv and fresh output paths:

```sh
.venv/bin/python qualification/installation.py \
  --spec /absolute/path/to/installation-spec.json \
  --output /absolute/path/to/retained-installation.json

.venv/bin/python qualification/build_fixtures.py \
  --emos-source /absolute/path/to/agon-emos \
  --toolchain /absolute/path/to/agondev \
  --output /absolute/path/to/fresh-fixture-build

.venv/bin/python qualification/run.py \
  --config /absolute/path/to/private-config.json \
  --flash-receipt /absolute/path/to/p4-retained-installation.json \
  --flash-receipt /absolute/path/to/emos-retained-installation.json \
  --fixtures /absolute/path/to/fresh-fixture-build/fixtures.json \
  --check-only
```

`installation-p4.example.json` and `installation-emos.example.json` show the
portable input shapes. The installation specification names the exact component/build, artifact,
independent readback, installation evidence and source archive/inventory/build
manifest, with hashes for every input. P4 additionally names its preimage,
application offset and erase range; dirty EMOS source additionally names its
patch and archive prefix. All paths stay in ignored machine-local records.
`installation.py --help` and the active release's retained local specifications
provide the concrete inputs. Revalidation checks those bytes again when the
runner loads a receipt; it never stamps a patch as clean or rebuilds firmware.

The fixture builder copies exact source inputs to its own output, builds a fresh
QSTATE mode-query/restoration app and the maintained EMOS raw-SD fixture, and
records source/binary hashes. Old startup-writing binaries/sources are refused.
The fixture source is independent of the older installed EMOS source snapshot;
its documented MOS API compatibility is reviewed separately. It never deploys.

`--check-only` validates receipts, source closure, fixture inputs, output profile
and case plan without constructing a live session or contacting either board.
It explicitly reports `hardware_ready:false`. No human-review emulator is started.

## Later hardware invocation and handback

Read the [operation protocols](../docs/procedures/README.md) and local bench
record first. Copy `config.example.json` to an ignored private record and select
`output_profile` explicitly. Verify the installed browser reset bridge's actual
actuator; the canonical run does not assume the historical Pi GPIO pulse works.
The legacy `reset_config`/flasher fields remain in the shared config for other
owner tools; this runner's resets use the configured bridge and fresh boot plus
an actual listener/read/EXIT handback.

After fresh input admission, the runner allows `reset_settle_seconds` (default2,
range2–30) for the reviewed normal startup before typing its first CLI command.
Admission can precede startup's remaining LOAD commands. This allowance is not
CLI proof: the following listener/read/EXIT must still succeed. Fixture LOAD/RUN
commands execute together in a separate MOS batch, never as early host keystrokes.

Only after the physical preflight above, replace `--check-only` with
`--bench-ready` in the command. That flag records the operator's completed
preflight; it does not perform or authorize firmware deployment. Do not supply
it while the bench is occupied or foreground/identities/reset are unresolved.
The runner then verifies current full EMOS ROM bytes, deploys/readbacks its own
unique support files, saves both modes, and invokes the cases explicitly.
Normal reset cannot launch or resume any test.

QSTATE uses supported MOS mode queries, bounded waits and ordinary file APIs.
The Pi waits for a listener queued *after* QSTATE returns; keyboard acceptance
alone does not prove completion. The Pi preselects P4 modes only when needed and
waits at least one second after committed status, including restoration.
At terminal notification, the runner verifies that the accepted player preserved
entry modes; it does not clear the new cue with a mode repair. The cue command
file must use the checksum-free fast listener and must not change modes/startup.

The durable summary records paired identities including source-archive
provenance, individual results, start/end and host-monotonic durations,
restoration and notification. Case durations include staging/retrieval and are
not rendering timings. Preparation, cases, restoration and notification have
separate accounting; there is no calibrated ETA for this revised native suite.
Retained historical durations are not reset or collection deadlines.

For actual Author observations, write a schema-1 review document containing
`author_statement` and `cases`, with one `status:"pass"`/`observations` entry for
every declared manual case. Never prefill passes. Bind it after the full run:

```sh
.venv/bin/python qualification/review.py \
  --run /absolute/path/to/completed-run \
  --review /absolute/path/to/actual-author-review.json
```

The new `author-review.json` retains the summary hash; it does not rewrite the
original evidence or update production selection/tagging.

## Separate performance work

`performance.py` retains its historical analysis/build helpers. Its old physical
coordinator and direct case entry point are disabled because they rewrote startup
and launched through reset. They must be migrated before hardware reuse. This
migration and another performance campaign are not v0.2.1 qualification gates.
Broad graphics/pixel studies remain separately scoped historical evidence.

## Native mode3 limitation found during qualification

The second native attempt passed all25 API/mode case checks, then failed complete
handback with a contained scanout abort. Its frame counters place that abort
around the raw fixture's mode3 clear, before raw I/O; exact causal scope remains
under investigation. Refill1746µs exceeded the unchanged1600µs guard and stopped
scanout. The actual sector preimage was restored and independently verified.

Native raw-SD output now uses mode20, within the declared representative profile;
its run token and prompt fit that display. Browser mode3 remains unchanged.
This does not qualify native mode3 or resolve its display fault. All sector
oracles, 25 required checks, DMA fault counters and timing guards remain enforced.
The release task and HDMI-002 retain the separate mode3 defect. Any release
acceptance must include this known limitation; no all-mode claim is supported.

The fresh complete native r03 run succeeds25/25 with verified restoration,
notification and cleanup; its [portable result](../docs/tasks/RELEASE-001/QUALIFICATION-R03.json)
records exact identities and phase timings. The measured total is about342 host
monotonic seconds for this configuration, including preparation and notification;
allow approximately six minutes for a comparable run. This is one successful
observation, not a calibrated duration or reset/collection deadline. Actual
Author visual review and mode3 limitation acceptance remain release gates.

Cursor cleanup explicitly restores text output, visibility and flashing on both
displays, and again at the terminal CLI after notification. The original r03
receipt predates this cursor-only host correction. The Author's later mode3
observation is stable, confirmed by advancing DMA and zero faults (maximum
refill934µs); the earlier abort's precise trigger remains unresolved. Do not
interpret that failure as mode3 consistently failing.

Later [display-only mode3 isolation](../docs/tasks/HDMI-002/MODE3-ISOLATION-R02.json)
passes six controls entering from0/20, then reproduces a1932µs abort on96→3
before clear/text. This strengthens the transition diagnosis without proving
the source cause. The guard remains1600µs; no raw SD or firmware change occurs.
Default entry modes/Legacy CLI and support cleanup are verified after standing
recovery. Frozen r03 results remain separate from this failed extra diagnostic.
