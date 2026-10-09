# PORT-008 — Private boot-release adapter results

**Both physical boot adapters pass off-bench checks; ordinary startup remains
unchanged.** The adapters reuse the existing held-level recovery sequencers.
EMOS's guarded image is 130,718 bytes, with **354 ROM bytes free**. The Author
released the bench through the mailbox; no hardware operation, commit or
production change occurred. Live startup binding and physical reset qualification
remain open under the parent integration task.

## Implemented boundary

R01 — EMOS's private boot leaf disables UART1 interrupts, releases all eight
Port C lanes and isolates UART receive through the existing loopback idiom.
It reuses the atomic Port D helpers, preloading CLOCK low / VALID high while
both controls are inputs, then enables those two control outputs. The poll leaf
samples READY and verifies actual Port C release before the sequencer can
advertise completion. Neither leaf restores UART or drives parallel payload.

R02 — P4's boot adapter disconnects UART RX/CTS, attempts release on every data
lane, disables internal pulls and configures CLOCK/VALID as inputs. It preloads
READY high before enabling that output. Any failed GPIO operation prevents
acknowledgement. Wrong-core calls refuse GPIO operations. A cancellation requires
a new physical fence; a previous release completion cannot be reused after UART
restoration. The coordinator must supply actual authorized UART restore completion.

R03 — These are exclusive boot/recovery leaves, with no ordinary startup caller.
They do not replace normal packet/queue/shift-register draining and parking.
The EMOS linked guard admits only this new writer's exact Port C sequence and
rejects direct calls into either private boot leaf from the linked image. A
patched-ELF negative control confirms that an unreviewed call is rejected.

R04 — The actual F92 defaults show that `init_UART1()` leaves Port C as inputs
with ALT1=ALT2=0. The earlier broad concern about this function enabling outputs
was incorrect. The future candidate must gate **`open_UART1()`** and subsequent
restore/error writers. P4 `beginConsole()` still binds UART pins at startup.
The [contract](BOOT-RELEASE.md) records this correction and the remaining boundary.

## Validation

| Check | Result | Evidence scope |
|---|---:|---|
| Paired physical adapter/SDK/register cases | 695 pass, ASan/UBSan | Real adapter and sequencer code; uneven polling, one-sided resets, absent/fixed-level peers, every boot SDK failure, core refusal and output-enable ownership |
| Complete-image eZ80 boot leaves | 126 pass | Actual linked instructions; exact writes, latch-before-output, preserved onboard GPIO, release refusal, restore sequencing, IX/SP/IFF and memory guards |
| Prior paired handover/session/control | 5,208 / 1,149 / 218 pass | Existing ownership and control contracts |
| Prior paired block admission/native parking | 18,097 / 196 pass | Existing admission gates and UART parking |
| Final-image control/session/reservation/parking | 10 / 1,334 / 22 / 289 pass | Existing linked eZ80 fixtures |
| Console lifecycle, installing-core and profile checks | Pass | Existing owners, retained N002 negative control and six EMOS profile checks |
| Full EMOS and P4-PC builds | Pass | Maintained wrappers, target adapter compilation, link/ABI/image guards, P4 validator and frozen-source recheck |

Leak scanning was disabled because the sandbox tracer prevents LeakSanitizer
inspection; ASan/UBSan remained enabled. The paired harness models owner phase
deadlines by releasing and retrying. Those are not calibrated physical deadlines
and never permit timed UART fallback. No whole-system Fab or electrical test is
claimed. The reusable host fixture records UTC start/end and monotonic elapsed
seconds; the final run took about 1.11 s including host compilation. This is not
a GPIO speed measurement or a hardware runtime estimate.

| Measure | Previous control candidate | Boot-leaf candidate | Difference |
|---|---:|---:|---:|
| ROM free below 131,072 bytes | 592 | 354 | −238 bytes |
| ROM used | 130,480 bytes | 130,718 bytes | +238 bytes (+0.18%) |
| EMOS static RAM | 4,058 bytes | 4,058 bytes | 0 |

Percentage is `(boot − control) / control × 100`. No resident boot coordinator
instance or second packet buffer is added. The remaining live coordinator must
fit the unchanged ROM limit; this checkpoint does not authorize another purge.

## Evidence and next step

[The result manifest](BOOT-RELEASE-RESULT.json) records exact source and artifact
hashes. Local evidence is retained under ignored `agents/port008-boot-release/`.
Reproduce with `tests/parallel_boot_release_test.py` and the sibling owner's
`parallel_boot` CPU fixture against the retained guarded image and symbol map.

The next increment must gate the real earliest UART writers in a private
parallel-capable startup composition, bind bounded polling and actual UART
restore, invalidate identities and quarantine stale bytes. Existing version-1
keyboard/ExCom operation must remain available in the ordinary UART-only build.
Actual one-board resets and shared-pad electrical behavior still require the
bench. No ExExt activation, native payload or production promotion follows from
these private-leaf checks. Changes remain uncommitted for Author review.
