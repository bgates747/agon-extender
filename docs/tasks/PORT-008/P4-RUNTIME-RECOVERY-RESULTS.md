# PORT-008 — P4 runtime cancellation and reattachment results

The private P4 candidate now observes EMOS CLOCK/VALID withdrawal, releases
shared pads before cancellation, discards old transport state and requires the
reciprocal release exchange plus UART TX idle before reattachment. Focused
software checks pass; complete native build checks are recorded below. EMOS
is unchanged. No bench operation or production promotion is part of this work.

## Behavior

1. The sole installing core checks live controls before each console loop's
   USB, parser and serializer work. Observed withdrawal begins a new pad fence.
   Only its successful completion permits one cancellation callback. A failed
   cleanup permanently denies restoration for that coordinator instance;
   timeouts never grant UART. Waiting polls do not repeat software cancellation.
2. The P4 console owner discards setup/peek bytes, pending UART replies,
   partial preactivation records, console/parallel capabilities and queued or
   held keyboard state. Remote keyboard admission and its old boot/session
   identity are invalidated. USB generation invalidates old/in-flight reports
   at loss and before reattachment; connection events retain HID handle
   lifecycle ownership. New physical input requires a neutral report.
3. The P4 owner clears SD presence/request/response state and admission-control
   caches. Active jobs fail; already-confirmed terminal admission receipts remain
   available to their HTTP worker. An application worker uses the mailbox
   generation to reject completions from before loss without corrupting a new
   owner's queue. Its old file-service engine and media lease are discarded.
   Previously executed local mutations are not undone.
4. Private parser recovery cancels disabled/paused control state, buffered echo,
   alternate reply destination and pending input events. It preserves the scene,
   resources and current video mode. Ordinary pause/resume intentionally may
   advance the cursor and scroll, so the private context reset does not call
   that ordinary method. No upstream fix or new video behavior is introduced.
5. UART cancellation disables TX queue interrupts, clears the TX FIFO, flushes
   RX and resets the event queue while pins remain detached. The P4 checks actual
   IDF TX-idle status before binding UART GPIO. The ordinary cancellation helper
   is deliberately excluded because it reattaches GPIO. No diagnostic, EMOS ROM
   code, new transport, display-route commit or parallel payload is added.

## Validation

1. **718 paired boot/runtime adapter cases pass**, including twelve new runtime
   cases against actual P4 coordinator/pad leaves and EMOS handover code. Held
   invalid levels, repeated waiting, wrong core, fence SDK failure/retry, cleanup
   refusal and a fresh peer exchange cannot reuse the previous grant.
2. **Four focused reset checks pass.** Actual reset/stream/mailbox leaves cover
   SDK failures, event queue refusal, busy TX, stale setup/peek/reply bytes and
   console commits, plus an old asynchronous completion after new ownership.
   The maintained context/parser method bodies execute against controlled
   boundaries; the USB epoch/report gate and actual console call ordering are
   also checked. These are host seams, not a hardware reset or electrical test.
3. **Twelve affected regression suites pass:** paired adapters, focused reset,
   UART owner, console session/lifecycle, SD queue, admission/WebDAV runtime,
   paired application card engine, USB decoder/CLI, processed keyboard and
   remote keyboard. ASan/UBSan are used by the existing harnesses, with unsupported
   LeakSanitizer disabled. Tests retain UTC endpoints and host-monotonic durations.
   Two negative controls also pass: ignoring live control withdrawal makes the
   paired runtime test fail, and accepting a prior mailbox generation makes the
   stale-worker test fail. Both controls execute the maintained tests with one
   deliberate behavior change; compilation failure is not counted as success.
4. **Native P4-PC compilation:** private candidate passes complete IDF compilation,
   a final unchanged-source Ninja dependency check and the maintained validator.
   The wrapper correctly refused source edits made during its initial compilation;
   the retained final archive and validation belong to the final unchanged source.
   The ordinary composition's complete maintained wrapper and validator also
   pass. Both final source snapshots are rechecked against the working inputs.

## Build size and time

Worst app image size first. These are compiled app bytes, not runtime memory or
transfer-speed measurements. Private increment is 3,456 bytes divided by the
ordinary 1,600,096-byte image (0.216%).

| P4-PC composition | App image bytes | Difference from ordinary | Source/validator |
| --- | ---: | ---: | --- |
| Private boot/runtime candidate | 1,603,552 | +3,456 | Pass |
| Ordinary UART-only control | 1,600,096 | Baseline | Pass |

EMOS candidate remains 130,981 ROM bytes, 91 free, with 4,063 static RAM bytes;
no EMOS source or build was changed in this tranche. Both P4 checks use the
explicit UNVERSIONED-DO-NOT-DEPLOY identity and browser output composition.
Neither is an installed or approved production artifact.

The ordinary complete wrapper took 374.947 host seconds. The private final
unchanged-source compilation/validation check took 4.459 seconds after its full
initial IDF build; its initial clean-build duration was not separately measured.
Those timings are not comparable build-speed results, nor device performance.

## Evidence and remaining gates

Machine-local checks/artifacts live under agents/port008-p4-runtime. Portable
hashes, component identities, test durations and final build status are indexed
in [P4-RUNTIME-RECOVERY-RESULT.json](P4-RUNTIME-RECOVERY-RESULT.json).
The previous observed-EMOS-loss work was published in Extender 059d469b and
EMOS 82dd593/a67e27f before this tranche; its frozen results remain unchanged.

This is sampled withdrawal, not universal detection of a brief reset. The P4
owner cannot interrupt an already executing VDU operation; resource callbacks
and all scene state are not comprehensively invalidated. P4 reattachment needs
the existing exchange, typically restarted by EMOS boot. Fresh keyboard/display
admission remains mandatory. A surviving EMOS does not automatically reconnect
or repair a committed ExCom route. Full held reset coordination, UART drain,
native payload binding and asymmetric-reset hardware qualification remain open.
Ordinary startup remains UART-only. No flash, reset, device network/serial test,
SD access, bench claim, production change or current-tranche commit occurred.
