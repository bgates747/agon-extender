# P02 — composition and transmission isolation

## Executive summary

Author approved P02 after P01 reproduced an output-associated timing tail.
Implement one default-off diagnostic candidate based on archived r43 and compare
normal output, output off, full native composition with local discard, and
prebuilt full-size frame transmission. No renderer algorithm, MOS, upstream
reference, browser credit contract or mainboard firmware changes. Golem excluded.
Stop at an actionable conclusion; notify by hardware voice, preserve original
startup and restore the verified r43 baseline before human review.

## Frozen diagnostic choices

These are agent-selected implementation details within approved P02, not new
Author-specified product requirements.

1. A compile-time diagnostic flag enables mode selection using the existing
   NPTRACE nonce: prefix `P02`, then mode0 normal,1 off,2 discard,3 prebuilt,
   followed by four random bytes. Ordinary builds have no selector or altered
   output behavior. The fixture and stock discard-buffer command remain intact.
2. The marker arms the control only for the deterministic game window. Return
   to ordinary mode after terminal accounting. Normal/prebuilt retain production
   browser ownership, takeover, credit and complete-send behavior; no reduced
   payload, receive-only client or browser-local rendering substitute.
3. Discard uses the existing snapshot producer, native rows and normalization,
   plus a local immutable-lease consumer at logical-frame opportunities. No
   frame bytes go to Ethernet. Prebuilt initializes each producer-owned slot
   once per geometry and reuses full-size bytes, bypassing native row work.
   It remains visibly synthetic and never qualifies gameplay or parity.
4. Target opportunity cadence remains nominal60Hz. Browser credit can reduce
   achieved normal/prebuilt rates; local discard may compose more frames.
   Record counts, pixels, bytes and achieved rates explicitly. Unequal work is
   not an apples-to-apples cost comparison. If needed, propose a matched-rate
   follow-up rather than hide the difference or call fewer pixels an improvement.
5. Count admitted composition/prebuilt/send operations and elapsed wall times
   with bounded counters, no timed-window prints/SD. Account operations begun
   in the window and allow a bounded post-terminal drain before dumping. Declare
   failures or unfinished operations instead of silently truncating counts.
6. Reuse r05 SW2400-state fixture and completion recorder;180second wired-Pi
   observer for transmitting controls. Verify hashes, full completion, pixel
   checks, memory placement and post-run SD/native-keyboard health. Preserve
   raw evidence. Run normal/off controls on the same diagnostic image as the
   two isolations. Repeat the discriminating contrast if material.
7. Host-check mode selection, bounded accounting, prebuilt slot initialization
   and lifetime assumptions; compile and verify candidate/rollback before flash.
   Verify normal control still reproduces the relevant behavior before attribution.
8. P02c permits at most one evidence-supported scheduling change. No blanket
   priority changes, resurrection of rejected same-core controls, or restoring
   stock's disabled blanking budget. If controls localize a useful next step,
   stop for review rather than stack speculative changes. No experimental push.

## Execution checklist

1. [x] I01: Implement and host-check default-off controls; freeze candidate source.
2. [x] I02: Build/hash/preserve/deploy/verify candidate and fixture readiness.
3. [ ] I03: Run and validate four controls, repeat informative contrast as needed.
4. [ ] I04: Interpret per-operation/output and paced completion separately;
   select at most one justified P02c change or stop with a proposed next step.
5. [ ] I05: Restore baseline/startup, verify service/input, commit evidence,
   deliver hardware voice notification and pause.

I01 host checks passed with C++17, warnings-as-errors and pthread support:
invalid selectors, repeated arm rejection, phase accounting, in-flight stop
join, producer-only cache reuse/invalidation, geometry bounds and slot capacity.
The stop dump copies counters under exclusion and prints only after releasing
it. Normal/prebuilt keep the existing network sender and browser protocol.

I02 candidate r45 built successfully; installed r43 was preserved and matched
before writing. Candidate flash was readback verified and boot/native USB
startup identity observed. Original startup and r05 fixture were read back.
P01's full asset readback is reused with no intervening asset writes.

## P02c source inventory — before selecting an affinity change

The selected candidate's `project_description.json` resolves SDK and Arduino to
the project-local `.pio/packages` paths, not an unrelated global installation.
The following is source/configuration evidence, not measured runnable time:

| Owner | Priority | Affinity/configuration evidence |
|---|---:|---|
| Parser |3|Explicit core0 in `video.ino::setup`|
| Drawing |5|Explicit core0 in `stock_p4_service.cpp`|
| Snapshot |2|Explicit core1 in selected experimental configuration|
| Network worker |3|`xTaskCreate`, unpinned|
| HTTP server/send task |5|`HTTPD_DEFAULT_CONFIG`, unpinned; project does not override priority/core|
| lwIP TCP/IP |18|Selected SDK config has NO_AFFINITY|
| Ethernet RX task |15|`ETH_MAC_DEFAULT_CONFIG` flags0; Arduino ETH changes reset timeout/stack but not pin flag|
| EMAC interrupt |Not a task priority|Allocated in MAC creation via `esp_intr_alloc`; setup call path and Arduino core1 configuration suggest core1, not independently observed|

Pinned SDK sources consulted: `components/esp_http_server/include/esp_http_server.h`,
`components/lwip/Kconfig`, `components/esp_eth/include/esp_eth_mac.h`, and
`components/esp_eth/src/mac/esp_eth_mac_esp.c`; selected Arduino
`libraries/Ethernet/src/ETH.cpp`. Distinguish the priority3 network worker from
the priority5 HTTP task that executes queued sends. Moving lwIP alone would
not isolate all these actors. No affinity change is selected by this inventory.
