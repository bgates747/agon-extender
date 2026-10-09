# PORT-008 — Native payload ROM fit

## Contract

The Author authorized EMOS trimming and continuation on 2026-10-09 after the
native payload checkpoint. First recover the space occupied by the uncalled
C reverse correctness reference, rather than removing a supported utility or
weakening a transport guard. EMOS continues to own admission, routing and GPIO
control. This is a bounded off-bench continuation of F02c3, not its completion.

RF01 [ ] — Verify all callers and reuse AUDIT-008's unchanged ELF/map accounting
tool. Preserve the preceding ordinary/private images and the refused native
link as comparative evidence; identify compiler, profile and source revisions.

RF02 [ ] — Exclude only `emos_parallel_engine_read` and its declaration from
ordinary/native firmware by default. Preserve its maintained source and an
explicit opt-in test composition, including existing paired C/C++ and linked
eZ80 reference tests. Keep the forward engine, handover checks, memory limits,
commands and public APIs unchanged. Add a compiled-symbol selection check so
tests cannot accidentally return the reference to resident firmware.

RF03 [ ] — Run complete wrapper builds for ordinary, native and reference-test
compositions, including every mandatory linked check. Account ROM/static RAM
and verify that the native image now fits. Execute the compiled native guard
and assembly from the full linked image as well as the retained RAM-only test;
rerun reference and affected forward/ownership regressions. Retain build/test
duration, hashes and result evidence. Compilation/instruction emulation does
not prove physical timing or transfer performance.

RF04 [ ] — Update current EMOS build/use documentation, paired task state and
the dated development log. Record recovered bytes and remaining integration
gates. Stop before live coordinator activation, bench access, flashing or
production promotion. Preserve unrelated checkout work.

## Bounded research

Official contracts remain agon-docs
`f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`, official MOS v3.0.2 and VDP v2.16.0;
the official checkouts remain read-only. Relevant references are
[GPIO ownership](../../../../../agon-docs/docs/GPIO.md) and
[MOS UART API](../../../../../agon-docs/docs/mos/API.md), calls 0x15–0x18.
This change neither adds nor removes an official API.

The maintained EMOS source currently has no product caller of
`emos_parallel_engine_read`; only the paired reverse test and eZ80 instruction
test call it. The preceding private ELF assigns it 574 bytes. Its shared
helpers also serve the forward engine and must remain. The existing link
checker does not require this reference symbol. Keep global linker behavior
unchanged: enabling section garbage collection would require a broader audit.

Reuse [AUDIT-008 accounting](../AUDIT-008/account.py),
[ROM review](ROM-REVIEW.md), [native contract](NATIVE-PAYLOAD.md) and
[native results](NATIVE-PAYLOAD-RESULTS.md). The predicted recovery is 574 bytes;
actual full-link measurements decide the result. Historical UARTFLOW extraction
savings must not be counted again. Resident diagnostics remain candidates for
future MOSlet extraction only if additional space is needed.
