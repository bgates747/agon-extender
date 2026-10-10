# PORT-008 — Original DevKit hardware control

## Executive summary

Author has connected the original DevKit and explicitly confirms the complete
parallel harness has remained in place. Preserve that assembly. Compare one
1,024-byte slow-profile historical receiver record with the failed P4-PC
40 MHz control. Keep current Agon EMOS and mainboard VDP unchanged. Current
EMOS requires reciprocal boot release, so first prepare a current DevKit EDP
composition for setup and recovery; the older installed EDP cannot provide it.
No missing-wire diagnosis is established by the outdated r03 drawing.

DH01 [ ] — Freeze contract and prepare current EDP for DevKit pin assignments,
with the existing reciprocal release implementation and browser/input services.
Allow this explicit nonrelease composition through the maintained builder; no
new protocol, diagnostic, GPIO assignment or resident EMOS change. Verify build
selection gates, native linked composition and exact installation segments.
Identify the physical DevKit before installation and record its identity locally.

DH02 [ ] — Install/read back that DevKit EDP, await HTTP before Agon reset, and
prove input admission and original SD startup through the foreground listener.
Verify the already-deployed historical sender and stage its reviewed temporary
startup. Preserve original startup and exact DevKit recovery image. Do not
substitute the P4-PC recovery image or require unavailable input to bootstrap.

DH03 [ ] — Rebuild the source-faithful historical receiver for the original
DevKit GPIO constants, retaining the 40 MHz control's SDK/compiler/configuration.
Prove only GPIO mappings/build identity differ from that control. Flash/read back
all segments and run exactly one 1,024-byte record at 24 NOPs. Retain USB verdict
and, if the analyzer remains attached, the existing bounded source capture.
Do not infer receiver-pad waveforms from source observations. No retries/sweep.

DH04 [ ] — Restore/read back the new current DevKit EDP and verify original
startup, actual remote command delivery and neutral input. Record the comparison
with the P4-PC controls and stop. This changes board, harness and P4 pin map
jointly, so neither a pass nor failure identifies an individual physical cause.
No production selection, reverse-transfer or ordinary ExExt enablement follows.

## Source and scope

The [40 MHz control](FLASH40-CONTROL-R01.md) owns the unchanged receiver
configuration/canary and deployed sender identity. The [historical comparison](DEVKIT-CONTROL-R01.md)
records the Author-approved original raw-GPIO sender exception; this repeat is
confined to that historical experiment, not a supported EMOS bypass. Official
read-only `agon-docs/docs/GPIO.md`, current `vdp/build/boards/p4-devkit.json`,
EMOS `src/emos_parallel_boot.c` and P4 `transport/console_hardware.inc` establish
that Agon GPIO assignments stay fixed while P4 assignments are board inputs.
Existing native payload/coordinator objects take their pins from those inputs.
The setup/recovery build adds no physical payload invocation; the historical
standalone receiver remains the measured endpoint. Keep private identities,
URLs, installed receipts and runtime artifacts in ignored local evidence.
