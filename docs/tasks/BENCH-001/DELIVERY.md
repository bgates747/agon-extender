# BENCH-001 resident telemetry and driving candidate

Machine delivery recorded,2026-09-13. The four practice blocks and
post-driving ROM/SD recovery audit and final native v2 integration are complete
within their separately identified runtime scopes. This document does
not mark the continuing RALLY-22 goal complete or authorize any commit/push.

## What runs where

EMOS owns the resident copied-snapshot service and its existing UART1/VBlank
interrupts. It serializes telemetry with ordinary keyboard/SD transport and
keeps all application pointers out of the ISR. P4 validates complete framed
CRC snapshots and publishes one latest value. The PC controller reads those
snapshots, predicts safe lanes/speeds and sends ordinary held-key transitions.
Rally runs its manual physics, with built-in demo/autosteer disabled. This is
telemetry-driven control, not camera vision or a trained machine-learning model.

AgonArcade rally-bench adds optional telemetry and the speed-linked sine engine
tone to the preserved pre-Golem production lineage. The Author heard the tone
and asked to leave it unchanged, then muted the speakers. The Author visually
accepted earlier driving and called a lap good; the final steering/grip
comparison remains machine evidence rather than blanket human acceptance.

## Identified driving images

| Component | Candidate | SHA256 |
| --- | --- | --- |
| EMOS bench composition |v0.1.16-b2026-09-13-07-31-36Z,130071bytes |1da8330462eed54317e5889cf3f09cb1abaca8b478f7d92b88a3a1d74c9fc70c |
| Experimental Rally |steering.bin,135899bytes |20fde9ace4aa56298c5648985a6f3fa0eccdd6c50d527c62045c393c421e37c1 |
| Previous traffic/policy experiment |traffic.bin,135723bytes |7cd631b1792fc73f55ca61031fd09992d1095acea4077c20199212b3f80d7dbf |
| Preserved accepted product |rally-production binary |e14e5c0f155a4f035e925b1da5971e8f7202fe47c7147e24a5726ef937d4fe5f |

The physical driving evidence used P4 uart-excom-console-r17-b2026-09-13-07-32-09Z.
Later Extender backlog experiments use separately recorded candidates;
HARDWARE.local.md owns the current installed identity. The driving build/flash bundle
contains independent flash verification, boot/native-USB evidence and a full
previous2MiB prefix. EMOS's installed build string was read directly from ROM.
The experimental Rally upload had complete staged and activated readbacks;
current source/input/binary hashes still match that bundle. Exact local paths,
network/device identities, complete source archives and original JSONL streams
belong in ignored agents/bench-001 and HARDWARE.local.md.

The root autoexec performs the guarded, already-consumed EMOS install then
starts quiet sdserve with Extender keyboard. No new flash happens on subsequent
ordinary reboot. Accepted production app/data and onboard VDP were untouched
by driving/controller changes. Do not rerun an old installation script as a
routine launcher. Before/after startup copies and older candidate binaries are
retained. The small standalone UARTFLOW diagnostic is omitted only in this
explicit bench-telemetry EMOS composition to fit128KiB; normal EMOS keeps it
and omits telemetry. This is not a shipped general feature-removal decision.

## Driving controls and observations

New options steer1/steer2/steer3 select the real per-rendered-frame held-key
step. Default is2;±21 range and all five reflected views remain. The host reads
byte78 and handles the changed reachable-angle parity when step2 clips at±21.
The Author's final priority ranks collision/road risk, then safe passing
progress on either side, then centre preference. A nearby-car guard prevents
cutting in before the passed opponent has cleared.

At180% grip, one- and two-tick90-second trials each made31passes and10clean laps
with no contact/kerb/grass samples. Both made14left/17right passes by interpolated
crossing position and automatically quit. Centre occupancy within±16world units
was76.2%/75.5%. Best laps8.043/8.108s differ by less than the133–167ms crossing
uncertainty; no definitive lap-time superiority is claimed.

The timed programme keeps four15-minute blocks at200/180/160/140% grip. Debugging
and deployment are excluded; preceding practice is separately archived. Every
trial preserves controller/trial source hashes, raw wire payloads and input
choices, then releases input, holds Escape0.7s and verifies telemetry cessation.
Physical takeover ends control; cleanup does not force reacquisition. A new
trial starts afresh from the EMOS prompt. Results/plot tooling is
scripts/report_rally_learning.py and scripts/plot_rally_learning.py. Final
aggregate evidence in PRACTICE.md distinguishes steering/reserve changes from
grip effects: 3600.066 seconds,399 clean laps,1108 passes,zero contact entries
or grass observations. Six early kerb observations remain in the record.

## Limits and informative failures

The real-eZ80 headless v1 run passed40seconds with404road observations. The v2
headless run rejected stale telemetry; an explicitly labelled350ms diagnostic
then recorded36grass samples and failed driving acceptance. That retained native
UART model lacks TX-empty interrupt demand, so it exercises VBlank/RX drains
rather than the physical transmitter interrupt path. No emulator/ISR change
was made for those original runs. Physical passing evidence is separate.

The later HEADLESS-CLOSEOUT.md records a faithful, explicit opt-in correction
in mos-agondev TEST-002, with independent register/byte-clock tests and default
runtime source preserved. The unchanged final Rally/controller now passes a
40.066-second native run at the current300ms bound:660 manual road observations,
four clean laps,12 passes,zero kerb/grass/contact, later guest key release and
ordinary Escape exit. The old runtime's current-candidate failure is retained
alongside both new passing runs. This is not physical baud/FPS qualification
or a change to the installed game, EMOS, P4 or onboard VDP.

Early local delayed/uneven cadence cases caught forecast and cut-in defects.
A shortened horizon moved the failure to another case and was rejected. The
current immediate-plus-delayed forecast and clearance guard passed six actual-
Motion cases for each selected low-grip/steering configuration. These finite
checks and a clean practice hour do not prove universal avoidance of arbitrary
future traffic. Opponent-to-opponent collision remains possible in the original
six-car bench field; RALLY-21 owns its replacement, not this demonstration.

Healthy physical HTTP variation caused early120ms-request/200ms-observation
cutoff stops. Active requests now allow200ms under a separate300ms observation
bound, with age checked again after keyboard status. Cleanup has a one-second
request bound; uncertain mutations are resolved only from exact journalled
bytes. Preserved early runs distinguish setup, deliberate Author interruption,
timeout and recovery from a gameplay failure.

Observed telemetry cadence and interpolated lap crossings are not measurements
of VDP completion or accepted production FPS. No direct camera/video feedback,
raw UART bit-rate capture, universal controller proof or new human graphics
acceptance is claimed. The unrelated existing light2-harness-r02 connectivity
hash mismatch still prevents an aggregate registry-validator pass; individual
artifact/template/VDP-source checks pass. Do not repair that historical record
silently or use it to discard this task's source/evidence.

Human emulator validation and explicit commit approval remain separate gates.
All current draft changes stay uncommitted, including preceding REMOTE-002 work
and other agents' preserved changes. RALLY-22 continues with a complete stock-
VDP game candidate, then the Extender video-throughput/faithful-command port
queue. Golem and paused RALLY-20 optimization remain outside this delivery.

## Post-practice recovery audit

Full131072-byte installed ROM download has SHA256
1cd65eac21780a8a7c82e14209737c38796e24f32300524e58a93e5c44e096d8;
its130071-byte image prefix matches the selected EMOS16 image above. The
root startup and accepted/experimental Rally binaries retain their expected
hashes. A63-byte marker passed both staged and activated SD readback. sdserve
then exited to the EMOS prompt. No reset, flash or accepted-app/startup change
was made. Private closeout-2026-09-13-09-38-24Z retains exact journals/readbacks.
