# ASYNC-001 stopped collection recovery

Recover the stopped generation-71 consumer, preserve returned application RAM
and its status before another LOAD, then finish the already selected cleanup
and normal release. MechAgon observed a real native CLI return with result 4,
four decisions, five view records and successful VDPlet UNLOAD. Its subsequent
listener-start collection failed with keyboard admission unavailable and reason
6. This does not identify the application or transport root cause.

1. Extender explicitly assumes sole recovery operation under the same central
   MechAgon lease after the actual stopped-consumer mailbox handback. Verify
   matching context/token, joined original actors, idle worker and free ports.
   Retain original logs and the setup-only unchanged startup identity.
2. Inspect actual keyboard/SD state. If admission is already positively ready,
   establish actual CLI/read/EXIT without reset. If admission remains unavailable,
   issue one commissioned Agon reset and verify actual CLI; use the standing
   initialized-P4 then Agon fallback only if this fails. No blind retry, firmware
   replacement, application replay or startup modification is selected.
3. Before any LOAD, save 64 KiB from 040000 into a fresh recovery namespace,
   retrieve/hash it and available `/MechAgon/render-status.txt`. The exact native
   map's BSS ends at 04A19D, within that saved range; dynamically allocated data
   outside the range is not claimed preserved. Mark whether reset preceded SAVE.
4. Run the existing identified bounded feature getter only after preservation;
   preserve its previous output first. Check exact feature absence, callback and
   buffer retirement, raw mode 0/callback zero/Legacy 0, complete unchanged
   startup/listener, responsive CLI/cursor, neutral input, offline listener,
   idle worker, free ports and joined children. This is cleanup, not a new game.
5. Release generation 71 on fresh truthful evidence; notify MechAgon and the
   actual prepared successor. Preserve failed native result and collection
   journals. Reset-state cleanup is distinct from the original native exit.

Private source freeze, stopped-return evidence, context and operational receipts
remain in the ignored request-local recovery directory. Existing selected
ASYNC-001 implementation/verification and standing monitored-recovery authority
cover this cleanup. No new consumer or firmware task is authorized here.
