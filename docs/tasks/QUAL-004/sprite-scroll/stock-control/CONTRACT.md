# Official stock VDP control

Author-authorized control: flash the published stock VDP v2.16.0 application,
verify it independently, and replay the unchanged SS_INITIAL input without the
optional capture token. This isolates the capture instrumentation from the
previous mainboard failure; P4 and EMOS remain unchanged.

**QUAL-004-SC01** [x] Preserve actual flash/startup; verify published asset digest
and app0 selection. Use the existing player and byte-identical scene/sidecar.
Select mode20 through autoexec only. No capture command, patches or source build.

**QUAL-004-SC02** [x] Open mainboard debug serial before ordinary reset; launch
one initial scene and observe up to30seconds after invocation, stopping on panic.
Retain raw serial and keyboard receipts. A clean observation is only a negative
control, not proof that the stock renderer has no intermittent defect.

**QUAL-004-SC03** [x] Restore original startup and application sectors if they
differ; verify normal prompt/input and close observers. Record exact firmware,
input hashes, outcome and limits. No upstream repair or further scene authorized.

Frozen before execution. Published firmware SHA256:
`b807beef35823b13a0a056f11b7464cd1b1c6356dce0e4098b78ebe059ded35f`.
Existing sprite-scroll-probe-r01 is unchanged; no new fixture identity.
