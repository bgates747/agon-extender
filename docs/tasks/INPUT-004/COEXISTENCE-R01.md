# Keyboard and controller coexistence

Restore the F310 on the P4-PC onboard USB hub while retaining the working
keyboard on the directly wired full-speed USB port. The installed keyboard-only
selection enables one controller. Espressif supplies a focused dual-host change;
backport that change into generated build output and qualify both input clients.
Keep EMOS, mainboard VDP, startup and existing display behavior unchanged.

## Authority and bounded research

1. On 2026-10-30 the Author directs controller/keyboard coexistence. INPUT-004
   already owns this unfinished integration. This selects implementation and a
   bounded P4 deployment/input check; it does not resume rendering campaigns or
   the separate INPUT-005 application/EMOS deployment.
2. The current direct-FS P4 source is `fd212503e34eb19761d59bc919f68bdda02b3954`.
   Use that matched display/transport composition, not a different renderer at
   repository HEAD. The ignored bench record owns exact artifacts, devices,
   wiring, reservation, URLs and rollback. Preserve an independently verified
   incoming P4 image before changing app sectors.
3. Pinned ESP-IDF 5.5.5 `b774170ff46c393eeb5e495ea37936038d3f4f4f`
   `components/usb/usb_host.c` configures one PHY even though HCD and root-hub
   layers accept multiple peripheral bits. Setting map3 alone is insufficient.
   The [pinned guide](https://docs.espressif.com/projects/esp-idf/en/v5.5.5/esp32p4/api-reference/peripherals/usb_host.html)
   explicitly identifies the one-host limitation.
   **Corrected after physical failure:** HCD supports multiple peripherals,
   but the selected `components/usb/hub.c:570` selects one root port, preferring
   BIT1. The initial PHY-only backport therefore cannot service both devices.
   The lifecycle mock proved PHY cleanup only and did not exercise that hub.
4. Espressif [PR402](https://github.com/espressif/esp-usb/pull/402), commit
   `48b250fa36e92c64a37c333dc548c84cb48c6eac`, merged as
   `5d6ace9fbf86d00578bbc133e28306e8001ffca7`, adds per-port PHY handles,
   initialization and cleanup, map validation and default FIFO selection for
   dual hosts. It does not replace the USB report clients or require a new
   transport protocol. Adapt these changes to the pinned older source layout;
   do not replace the SDK or fake optional HAL capabilities.
5. The HS-capable port still needs the already reviewed FS/LS-only restriction
   for the onboard hub/F310. That existing HCD backport applies only to the
   HS-capable controller. The separate direct FS PHY retains normal low/full
   speed handling. Both ports use existing interrupt priority/default FIFO
   settings; no speculative custom FIFO or physical rewiring is selected.
6. Official MOS keyboard contracts remain unchanged. P4's existing HID client
   owns keyboard acquisition; its existing XInput client owns F310 acquisition.
   EMOS retains UART input admission and routing. Application controller APIs
   and physical USB acquisition remain distinct responsibilities.

## Implementation and validation gates

1. [x] Add a source-hash-pinned generated USB host derivative with correct
   per-port cleanup on second-PHY/HCD failure and uninstall. Preserve the SDK
   checkout; record upstream origin, adaptations and removal condition beside
   the recipe. Reject unreviewed source drift.
2. [x] Add explicit P4-PC/console dual-host build selection, excluding the
   keyboard-only direct-FS selection and requiring the existing HS FSLS remedy.
   Record map3 and the actual compiled host derivative in manifests/validator.
   Reset the onboard hub only for selections that actually service it.
3. [x] Apply the same bounded source change to the retained matched P4 source,
   preserve all display/transport/board/dependency inputs, and produce a fresh
   clean identified experimental build. Verify actual compile/archive/link
   selection and pre-v3 guards. Run relevant offline input/build checks.
4. [ ] Verify fresh bench state and actual CLI, read unchanged setup-only
   startup, retain rollback, then write only authorized P4 application sectors.
   Independently read back the app and untouched flash, initialize P4 before
   releasing/resetting Agon, and establish fresh input/actual CLI. Do not modify
   EMOS, mainboard VDP, SD startup or an unrelated application.
5. [ ] Verify direct keyboard HID admission and native F310 reports while both
   clients run. Stage the already matched controller viewer if needed; preserve
   its mode lifecycle. Actual physical key/controller exercise and visible
   smoothness require Author review. Ask in chat only for missing attachment or
   physical actions, preserving the keyboard-only rollback if coexistence fails.
6. [ ] Close all unnecessary readers/input sessions, leave a responsive CLI or
   explicitly identified review application, record exact final bytes/results
   and update current bench/task guides. Production/version promotion remains
   governed by later Author acceptance and agreed release identity.

This bounded continuation makes no simultaneous-device pass or byte-saving
claim before measurement. No controller checksum, generic packet tunnel, extra
EMOS diagnostic or application policy is introduced.

## Prepared candidate — before physical installation

Matched source `2d88a884e9d49c855a2dea774bbb6e2d3c7f01b9` builds cleanly as
`indexed-hdmi-r15-b2026-10-30-21-49-00Z`. Complete native validation and actual
source/archive/preprocessed selection review pass. Application is 1,779,152
bytes, SHA-256 `bb61ba8c6e73bfe3fccceee1a3ebfda073add39f6aceb601314261285e6296f2`.
The SDK/HID, board/display, partitions and dependency settings match the working
direct-FS baseline; only six reviewed source/build files differ. Build duration
is 529.58 host monotonic seconds, separate from later installation/review.

The generated lifecycle passes 17 fault-injection cases, including second-PHY,
HCD/upper-driver and allocation failures, complete uninstall, skip-PHY ownership,
map validation and dual/default FIFO selection. Existing USB keyboard/owner,
F310 decoder and build checks pass. [Portable evidence](COEXISTENCE-BUILD-R01.json)
records exact source and artifact identities. Actual compile/archive/ELF checks
prove the selected derivative is used; the SDK checkout stays untouched.

All installation/preflight helpers are prepared and pinned in ignored local
evidence. No physical bench reservation, reset, input injection or flash has
occurred. Fresh confirmation of Agon's foreground state and device attachments
precedes those helpers: historical prompt receipts cannot establish a current
idle application. Keyboard-only firmware remains installed; EMOS/mainboard
VDP/startup are unchanged. This is a candidate, not test-readiness or a physical pass.

## Physical initialization rejected and P4 restored — 2026-10-30

After the Author confirmed both devices connected and an idle Legacy MOS prompt,
actual CLI/startup checks passed. P4 application and full-flash readback matched;
all bytes outside the application sectors were unchanged before execution.
The candidate admitted the direct keyboard but did not demonstrate F310/hub
admission. Two `httpd` stack-overflow panics restarted P4 during readiness checks.
The decoded retained core confirms the task and panic; its crashed stack cannot
identify the offending handler. Do not infer a USB/electrical root cause from
that symptom. The installer retained Agon reset rather than releasing it into
this rejected candidate. Future installation checks must stop at the first
panic, stack-overflow indication or repeated startup before another status poll.

The agent explicitly restored the incoming keyboard-only P4 application and
every expanded application sector. Independent sector readback and full-device
verification pass. The fresh crash/NVS prefix was preserved; no EMOS, mainboard
VDP, startup or SD file was written. The restored exact P4 build, keyboard HID,
HTTP startup and five clean seconds pass. The controller viewer was never run.
[Installation evidence](COEXISTENCE-INSTALL-R01.json) records identities and limits.

Agon's fresh Extender input admission did not return after reset-hold release.
Both standing recovery steps were attempted: one Agon reset, then independently
verified restored P4 reset/initialization followed by one Agon reset. Neither
restored admission; both passive mainboard captures contain zero bytes. All
readers/workers/holds are closed or released. Physical mainboard reset and current
screen observation are required before dependent live checks. Steps4–6 remain
incomplete; there is no simultaneous-device pass or production promotion.

The Author subsequently reports a regular MOS prompt, Extender keyboard enabled
and physical typing working. The loaded flight simulator runs but finds no
controller. This is expected with the restored keyboard-only P4 selection, which
does not service the onboard controller hub; it does not establish a simulator
or EMOS regression. The agent made no EMOS or simulator change. Record this as
Author-observed recovery, separate from the failed automated handback. Current
foreground application must be confirmed before any further live intervention.

## Offline correction boundary

1. Replace the incomplete PHY-only adaptation with Espressif USB1.6.0 as one
   complete, exact archive-pinned component override. It contains the two-root
   hub, enumeration and public host changes together. Keep IDF5.5.5, its PHY/HAL,
   pre-v3 silicon guards, clocks, HID1.2.1, board/display and both input clients.
   The [official component contract](https://components.espressif.com/components/espressif/usb/versions/1.6.0/readme)
   supports overriding the built-in5.x library; its exact source is
   `630f1c4e61f71d62bb57ff1b840931da24c3329f`. Archive SHA-256 is
   `da5be2a2743ede3bd63e6c4046e381e24b16567ea8a7541b6f5d094abea5098b`.
2. Keep the public `fsls_only` field false: the pinned older HAL explicitly
   lacks that capability. Retain the existing HS-only root-reset assignment
   as a source-pinned derivative, and task-owned EP0 error reporting with bits
   that do not collide with the newer component's existing actions. Do not
   copy old LS probes or duplicate upstream cache fixes into the replacement.
3. Bound the HTTP-task remediation independently. Its current request stack
   is4096bytes and the controller status formatter reserves1600bytes before
   SDK/formatting calls. Review actual compiled frames and provide headroom;
   this does not prove the missing core stack's original call site. Keep the
   crash evidence and distinguish a mitigation from a measured physical fix.
4. Stop initialization observation on the first panic/stack-overflow/repeated
   startup before another readiness poll. Verify that behavior offline.
5. Produce and verify a fresh matched-source candidate offline. No additional
   physical action is selected while the Author may be running the simulator.
   Fresh foreground/attachment confirmation precedes a later installation.
