# Bounded listener MOSlet build/check — 2026-09-21

## Executive summary

The unchanged listener now passes bounded physical MOSlet checks under provisional
EMOS v0.1.18. The initial attempt exposed two local exclusions: the generic
service gateway rejected MOSlet requests, and ext.sdlink excluded MOSlet buffers.
The narrow correction admits MOSlet memory only for resident ext.sdlink. Other
providers retain the exclusion. Historical initial findings below are retained.

## Build and findings

M05-01 [x] Existing listener retained. Review Jeroen's C/assembly eZ80 utility,
C++ VDP code and C/C++ host tooling before adding new functionality, with attribution
and licensing checked. The VDP half owns its external USB serial connection.

M05-02 [x] Build isolated source from agon-emos26ba8776 with ordinary service logic
unchanged; only identity and link configuration differ. See [manifest](MOSLET-BUILD.json).
RAM_START0xB0000; RAM_SIZE0x8000;18987-byte executable; static end0xB5333;
stack/heap upper bound0xB8000. Remaining11469bytes is unmeasured runtime headroom.
AgonDev CRT saves/restores incoming stack/registers; no whole-memory proof inferred.

M05-03 [x] Stage under experimental `/mos/sdmtest.bin`, leaving original
`/extender/sdserve.bin` and all firmware intact. CLI invokes test as a MOSlet.
Service never announces online; existing EMOS source `src/emos_sdlink.c::range`
requires address>=0x040000 and address<0x0B0000, with complete ranges contained
there. Both request and input buffers now reside above that exclusive ceiling.
The source therefore predicts FR_INVALID_PARAMETER at admission. No transfer pass
is claimed for the MOSlet. Normal MOSlet name/path lookup and relocation alone
cannot overcome this range policy.

M05-04 [x] Physical MOSlet returns to CLI;4096-byte application sentinel at
0x040000 survives exactly across invocation/exit. Original ordinary listener then
passes1024-byte upload/download and unchanged-startup readback. Original loaded
q4draw fixture restored without running it; keyboard ready/neutral. Unusable test
alias removed from `/mos`; build and evidence retained locally. This is not a
full application-space, stack high-water or MOSlet-transfer qualification.

M05-05 [x] Follow-up: narrowly admit valid MOSlet RAM in ext.sdlink, retain MOS
reserved-memory and overflow rejection, test boundary addresses and fresh physical
transfer/exit. This requires an EMOS candidate and its deployment, deliberately
outside the requested quick build/check. Do not work around it by placing buffers
in a loaded application's RAM. Keep shared runtime/caller-state review in scope.

The test filename is temporary: current self-write protection reserves basename
sdserve.bin, so the test alias is not an appropriate production installation.
Never target that alias while running it. A successful future install must retain
the canonical protected basename and validate moslet-path selection.

## Authorized provisional correction

Author now authorizes the bounded EMOS correction and physical test. EMOS
v0.1.18 admits MOSlet-resident requests exclusively for ext.sdlink and expands
its checked caller range through B7FFF, rejecting overflow and MOS RAM. Other
providers retain the module-space exclusion. Boundary sanitizer tests and all
maintained firmware link checks pass. Registry r100 uses standing preapproval.
Installed v0.1.17 ROM was read back and retained before deployment; ordinary
source baseline matches the candidate parent. Physical results follow.

## Provisional physical pass

1. Candidate `agon-emos-v0.1.18-b2026-09-21-05-03-49Z` was installed once through
   the existing FLASH utility. The updater rebooted automatically; no timed reset
   was used. Entire 128 KiB ROM readback matches the padded candidate exactly.
2. `/mos/sdserve.bin` contains the unchanged MOSlet build described above. Invoke
   `sdserve /` at the Legacy MOS prompt with Extender keyboard selected. Original
   `/extender/sdserve.bin` remains available. The temporary alias was renamed.
3. MOSlet upload, independent stage/active-file readbacks, and download passed
   for a 1024-byte binary payload. Self-overwrite of `/mos/sdserve.bin` was rejected.
4. Host EXIT returned to MOS; a second MOSlet invocation passed. A 4096-byte
   sentinel at 0x40000 survived byte-for-byte. Startup was unchanged. The prior
   q4draw fixture was reloaded without execution; terminal state is the MOS prompt.
5. Boundary sanitizer checks reject MOS RAM and overflowing lengths; complete
   maintained firmware build/link checks pass. This is provisional bounded
   evidence, not whole-memory/stack high-water or general MOSlet qualification.
   The firmware occupies 131056 of 131072 ROM bytes: only 16 bytes remain.

See [machine-readable results](MOSLET-RESULTS.json). P4 and mainboard VDP were
unchanged. No new network protocol or background execution was introduced.
