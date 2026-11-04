# Eirene EMOS first hardware installation

## Executive summary

The Author explicitly requests flashing the isolated Eirene-based EMOS candidate.
Prepare an identified experimental build from the checked source, preserve exact
incoming rollback, install EMOS only and verify boot/input plus the complete ROM.
This is not promotion, broad qualification or permission to run applications.

1. Reconcile physical custody/FIFO and obtain a fresh Extender lease. The older
   paused VDPlet request needs its current owner's disposition. Defer the separate
   filter benchmark; do not silently run it or change its historical baseline.
2. Replace exploratory identity through source-owned build metadata only, keeping
   firmware behavior unchanged. Retain the original unversioned checked image.
   Use a clean task-branch source snapshot and separately admitted guarded build;
   execute all four mandatory linked checks. Record every byte/hash and version
   as experimental, without selecting a production release/tag.
3. Under custody verify actual CLI, route/modes, neutral input, idle jobs/listener,
   free serial/reset resources, current component provenance and unchanged safe
   startup. Preserve incoming EMOS through complete SAVE/GET comparison to its
   retained image, plus current listeners/startup. No reset into application RUN.
4. Stage/read back the identified image and exact rollback under `/extender`;
   keep evidence under `/agents/extender`. Never modify autoexec or unmount SD.
5. Invoke FLASH mos once at actual Legacy CLI with a proved passive printer
   mirror. Wait for automatic reboot and the exact new identity; no timed reset,
   repeated FLASH or uncertain replay. P4/native VDP remain unchanged.
6. Verify fresh neutral input, actual CLI and full131072-byte ROM SAVE/GET against
   image plus FF padding. Verify unchanged startup/listeners and selected route.
   Restore mirror off/visible cursor/CLI and close resources. No game, benchmark
   or async test invocation; leave the experimental image for Author review.
7. If normal access fails, follow the existing Agon-first reset order and keep
   operation evidence. If the candidate cannot operate, restore exact incoming
   EMOS using the maintained recovery protocol under this installation's rollback
   boundary; P4 firmware changes only if required by that explicitly reviewed
   recovery path, never as an unrelated deployment. Stop at unverified effects.
8. Record independent outcomes: staged, flash invoked, reboot observed, full ROM
   verified, CLI/input verified and acceptance still pending. Current production
   selection/tag remain unchanged. Preserve all source in the task branch.

## Installation result and self-assigned correction — 2026-11-04

The first identified experimental image was staged/read back, programmed once,
and automatically booted with its exact identity. The updater reported its own
successful programming check. Independent full-ROM SAVE/GET remains **pending**:
Extender keyboard admission fails, preventing CLI injection/listener entry.
One Agon reset, then one P4 reset followed by an Agon reset, each failed to
restore input. No uncertain FLASH replay, native/P4 firmware replacement,
autoexec edit, game or benchmark invocation occurred. Physical custody remains
with Extender while recovery is incomplete; do not hand this state to a consumer.

| Item | Exact result |
|---|---|
| First installed candidate | `agon-emos-eirene-r01-b2026-11-04-07-59-48Z` |
| Source commit | `b29e843fabeb6a753fb741dde680aa82938bde96` |
| Application / free ROM | 128159 / 2913 bytes |
| Application SHA256 | `57d03b9388448af983a076eeebc4c797ff7ce16ef2fd2c9e66db83511fe2c6ee` |
| Corrected prepared candidate | `agon-emos-eirene-r02-b2026-11-04-08-17-43Z` |
| Corrected source | `16ec1f78c7ead1f38378c5ee9bee4633bcb62c1d` |
| Corrected application / free ROM | 128159 / 2913 bytes |
| Corrected application SHA256 | `079873c01da8e3bf2fae8e11a582af1de2c96078c9c2a7539edbde95ad4f1d44` |
| Corrected padded full-ROM SHA256 | `f62eed7f6bab8c164dcfe5e700132d289d52352f19d955acccbe1cff81b5e893` |

### Cause and corrective implementation

Inherited Eirene RC2 `825eaf7` calls `__init_default_vectors` before clearing
BSS. Its RAM `__2nd_jump_table` is inside BSS; clearing it erases all48 default
entries. Main reinstalls active vectors, but UART1 stays zero. EMOS correctly
refuses to claim a non-default UART1 handler. Moving initialization immediately
after final BSS clearing fixes startup without weakening the ownership guard.
A fifth mandatory linked check proves that exact ordering and table placement.
It rejects the retained r01 image and accepts r02. The other four checks pass.
The r02 manifest's inherited scope string still says four checks; its actual
build log records all five. Do not rewrite the frozen manifest to hide this typo.

Guarded r02 build completed in6.046s, peak55.65C, no throttling or surviving owned
children. Its compile lease was released before analysis. This is build/check
evidence only; r02 is not yet installed or physically qualified.

### Recovery preparation and next boundary

1. Prepare a disposable, **RAM-only** MOSlet using official
   `agon-docs/docs/mos/API.md` mos_setintvector14h and executable-header/loader
   contracts from `agon-docs/docs/mos/Executables.md` and current EMOS
   `src/emos.c:emos_run_utility`. The generated binding uses the retained exact
   r01 ROM build string, startup bytes, default-handler bytes and UART1 slot.
2. The utility refuses a different ROM, enabled UART1, DLAB state or unknown
   vector owner. On the matching dormant zero slot, it asks MOS to restore only
   UART1's default handler; it preserves other vectors and writes no flash.
   [Assembly source](recovery-r01/irqfix.asm) and [link layout](recovery-r01/linker.ld)
   remain task-local. It is not a production utility or generic ownership bypass.
3. Prepared utility:441 bytes, SHA256
   `11b75886e3b01b8ba51e264ca885a0db2b9a4482f5bbd9a7e16798baae0b4f1d`.
   It assembles/links with a valid MOS/ADL header and fits the MOSlet region.
   Guarded build1.030s, peak52.35C, no throttling/owned children; lease released.
   No physical execution or emulator qualification is claimed.
4. Physical SD access and a reviewed temporary boot shim are still required.
   Proposed shim executes only `EMOS irqfix01`, then `EXEC /autoexec.txt`, so the
   original startup can admit keyboard input. It never launches a test or FLASH.
   Preserve/refuse any existing `!boot.obey`; do not overwrite unknown files.
   The Author must approve this recovery-only startup interception before staging.
   `/autoexec.txt` remains byte-for-byte unchanged. Leave cards mounted.
5. Once input works, the host must verify actual CLI, remove the temporary boot
   shim through the foreground listener, then install r02 using the ordinary
   single-FLASH path. Complete independent full-ROM comparison and input/listener
   verification. Archive/remove the disposable utility afterward. A later reset
   must execute the original normal startup without any recovery action.
6. Current P4-PC ZDI recovery is not commissioned: the historical DevKit GPIO46
   recovery mapping conflicts with current parallel D7. Do not assume historical
   recovery leads are present or swap P4 firmware using the DevKit recipe.

Private receipts retain entry-ROM backup and exact rollback, staged image
readbacks, passive FLASH/boot capture, both failed reset-recovery observations,
source/build manifests and guards. UART/Eirene owner was notified through durable
mail and immediate steering. Production selection and tags remain unchanged.

### Independent source review

UART/Eirene owner mail `2026-11-04_03-22-18_agon-mos_emos001-irq-startup-source-review-one`
confirms the same BSS/table ordering in upstream and RC2. Both preserved-RAM
and cold-boot paths need the move. The reviewed helper preserves AF/interrupt
mask and the hard-reset flag remains balanced. This is inherited startup code,
not an OTIRX/callback/RC2-trimming defect. UART0-only checks did not inspect unused
IRQ defaults. The peer performed no new build or target operation, and its
source review does not qualify r02 on hardware or authorize extra work.

### SD recovery staging completed; physical return pending

The Author mounted the Olimex SD on Oryx. Card identity and exact startup,
canonical/private listeners, incoming rollback and original staged r01 image
were verified before writes. Automatic approval review rejected the first
combined staging action because SD access was not explicit approval of the boot
interception; that rejected call executed nothing. Unaffected inert payloads
were then copied and independently read back. The Author explicitly approved
the temporary recovery boot script through the requested high-priority question
notification, after which it was installed and read back once.

The mounted card now contains `/emos/irqfix01.bin`, the exact padded r02 image
under `/extender/install/emos-eirene-recovery-r01/`, a support manifest, proposed
script text and a byte-identical original startup copy. Root `!boot.obey` is:

```text
EMOS irqfix01
EXEC /autoexec.txt
```

Its35 bytes hash to
`052249db95059cc7ad2500403b15c6d48df0549ed94185e90801213d7b84c66f`.
`/autoexec.txt` remains108 bytes/SHA9e97ceae5489e1b6330c6a2f207d95c6566c60cac304d65e7aad54b610a5b423.
Writes synchronized; the card remains mounted. No utility invocation, reset,
FLASH or firmware verification occurred during staging. Physical return to
Agon and restored power are the next Author action. After the single repair
boot, remove the temporary shim before the ordinary corrected-image FLASH.

### First approved repair boot did not restore input

The Author returned the card to the fully powered Olimex without resetting or
power cycling. Extender asserted its live lease, verified no active listener/job
and free serial devices, then issued exactly one Agon reset. A fresh input epoch
appeared, but admission remained false through the40-second bound. The host
stopped before CLI injection, a second reset or any corrected-image FLASH.

The Author reports “error executing the boot obey.” Exact line/error and whether
the utility executed or refused are still unresolved; do not claim a successful
RAM repair from the fresh epoch alone. Preserve the temporary script and current
ROM while obtaining that text. P4/native firmware and autoexec remain unchanged.
Private receipts: `agents/emos001/flash-r01/repair-boot-r01/`.

### Photo resolves first repair boot; recovery r02 preparation

The Author's photo confirms `UART1 default restored in RAM; no flash written`,
then KEYINPUT busy and errors at `/autoexec.txt` line2 / `!boot.obey` line2.
Thus the r01 utility executed successfully. The failure is the already-failed
EMOS boot connection: `emos_init()` calls `emos_parallel_boot_connect()` before
OBEY startup, and that connection could not claim UART1 while its vector was
zero. Its deliberate fence/grant0 remains after the later vector-only repair.
`open_UART1()` correctly rejects that missing admission. Do not weaken it.

Prepare a new separately retained recovery r02 utility. It keeps exact-r01 ROM
and dormant-UART/vector checks, restores the vector through MOS14h, then calls
that ROM's **EMOS-owned startup** fence/connect routines and checks the resulting
normal grant2. The utility must not write grant/state/transport registers itself
or bypass UART admission. These private calls are confined to this disposable,
exact-ROM, exclusive boot-recovery operation; they are not application APIs or
supported consumer entry points. Keep the original441-byte utility/evidence
unchanged. Bind both startup entry points and owning state symbols to this ROM.
Refuse active keyboard/console/UART owners. Reuse the already approved temporary
boot file unchanged. A further card update/repair boot is necessary, not an
uncertain replay of the old attempt. The corrected firmware already places IRQ
initialization before its first EMOS handshake; this issue does not require a
second firmware workaround or weakening either ownership guard.

Recovery r02 assembled/linked:589 bytes SHA256
`fe8171cec960978876f19b0259284d7252318d081478c2c5ad78c8e876fb0827`.
Linked bytes prove one owner start/connect/allowed sequence requiring grant2.
Native guarded build1.028s/peak50.7C, no throttle or remaining owned process;
compile slot released. Not yet on SD or physically executed. Next required
Author action is moving Olimex SD back to Oryx for this utility replacement.
The already approved35-byte boot file remains unchanged.

### Recovery r02 SD update verified

The Author remounted the Olimex SD on Oryx. Its volume identity and unchanged
boot/startup/listeners/corrected-ROM hashes were checked first. Only the active
repair utility was replaced with589-byte recovery r02/SHAfe8171ce; the original
441-byte utility was preserved under `/agents/extender/backups/firmware/`.
Full readback matches; writes synced; card remains mounted. The approved boot
script and autoexec are unchanged. A new inert support manifest records r02.
No reset or utility invocation occurred; await physical card return before
executing the prepared one-shot repair-boot-r02 helper.

## Corrected installation completed — 2026-11-04

The Author returned the card with both boards still powered. One explicitly
controlled recovery-r02 Agon reset restored fresh neutral Extender input and
actual CLI/listener entry. EMOS's normal startup owner completed the handshake;
no admission guard was bypassed. The temporary root boot script was archived
and its absence independently checked before updating firmware.

At recovered CLI, complete independent SAVE/GET of the first installed r01 ROM
matched its exact131072-byte prepared ROM. This closes that earlier readback
gap; its behavioral failure remains preserved. The host also reread and compared
the corrected image, incoming rollback, unchanged autoexec and both listeners.

Extender invoked exactly one corrected-image FLASH at a verified Legacy prompt
with proved passive print capture. The updater completed128pages and its own
programming check, then automatically rebooted with exact r02 identity and
`Keyboard input: extender`. The root recovery script was already absent: this
is the corrected firmware's normal startup, not utility-assisted admission.

A fresh actual CLI/listener exchange and full131072-byte ROM SAVE/GET match
`agon-emos-eirene-r02-b2026-11-04-08-17-43Z`, source
`16ec1f78c7ead1f38378c5ee9bee4633bcb62c1d`, exactly. Full-ROM SHA256:
`f62eed7f6bab8c164dcfe5e700132d289d52352f19d955acccbe1cff81b5e893`.
Application128159 bytes/SHA079873c01da8e3bf2fae8e11a582af1de2c96078c9c2a7539edbde95ad4f1d44;
free ROM2913 bytes,759 more than the incoming identified carrier.

The disposable utility was archived from `/emos/irqfix01.bin` into the support
directory and read back exactly. Autoexec108B/SHA9e97, canonical listener/SHA0566
and private listener/SHAf60f remain unchanged. Native mode0 is verified via the
new image's sysvars. Final listener offline, staged job idle, admitted neutral
input, no held keys, free serial devices and visible/flashing-cursor controls
sent. No optical cursor claim, game, async test, benchmark or suite invocation.
P4/native VDP firmware were not flashed. The later firmware boot required no
manual reset, P4 reset or replay.

This completes the requested experimental installation and recovery. It is not
Author feature acceptance, full compatibility/async qualification or production
promotion. Keep the old carrier rollback and informative r01 failure. Extender
retains custody pending Author review; queued consumers have no grant yet.
Private receipts are under `agents/emos001/flash-r01/{repair-boot-r02,prepare-r02,flash-r02,verify-r02}/`.
