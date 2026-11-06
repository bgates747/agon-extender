# Native reverse VALID filter preparation

Add the existing fixed P4 input filter to the strict native reverse payload
owner. MechAgon's retained failure counted five VALID edges instead of exactly
two. Filtering is a bounded candidate, not proof of the electrical cause or a
hardware repair. Preserve the complete protocol proof and resource lifecycle.

## Authority, scope and evidence

MechAgon selected this owner preparation in its2026-11-06 source request
`render001-valid-filter-owner-source-request`, under Smith's delegated RENDER-001
implementation authority. Smith's overnight continuation prioritizes MechAgon,
then Wolf; it does not preempt Wolf's actual bench checkout. N04-016 owns source,
focused host checks and an identified full P4 candidate build. No target access,
installation, capture, application run or new bench reservation is selected.

1. Official Agon GPIO reference `agon-docs/docs/GPIO.md` establishes that these
   physical connections differ by board; no wiring or eZ80 register change is
   needed. The existing endpoint and board profile remain authoritative.
2. Pinned ESP-IDF5.5.5 `docs/en/api-reference/peripherals/gpio.rst`, GPIO glitch
   filter section, defines the fixed pin filter: reject pulses shorter than two
   IO_MUX sample cycles, with no configurable duration. This does not add a
   software debounce or acknowledgement per payload byte.
3. `p4_parallel_upload.cpp` already owns a VALID pin filter alongside CLOCK.
   Reuse its SDK calls, enabling before independent PCNT observation and READY
   release. `p4_native_payload.cpp/.hpp` own the native payload lifecycle;
   `p4_valid_counter.hpp` retains exact-two acceptance and the first fault.
4. MechAgon's retained R10 requested/completed93B with five VALID edges and
   blocked CTS on the next three-byte control prefix. This identifies the
   rejected proof, not the pulse origin. No relaxed count>=2 rule is allowed.

## Bounded implementation and validation

N04-016.01 Publish this plan before changing code; notify MechAgon of the
  source-only phase and its hardware boundary. [x]

N04-016.02 Add a separately owned VALID filter only for the strict reverse TX
  path. Preserve CLOCK filtering, exact DMA/byte/edge proof, deadlines, GPIO
  polarity, one-byte intervals, ABI and first-error retention. Stop counters
  and the peripheral before disabling/deleting the filter; preserve partial
  creation/enable/disable/delete failures and retained-resource compositions. [x]

N04-016.03 Extend actual native SDK-fake sanitizer checks for both filter
  identities, enable-before-PCNT/READY ordering, successful1B transfer, sustained
  extra intervals still rejected, partial second-filter setup and failed cleanup
  retaining owner/DMA until successful retirement. Test strict and retained
  ExExt compositions; do not pretend a digital fake measures analog filtering. [x]

N04-016.04 Through normal serial Pi compiler FIFO, run focused host checks and
  produce a new identified full-feature candidate using the exact installed
  diagnostic composition as donor. Preserve all feature/source/SDK linkage
  enforcement and the retained RX descriptor remedy. Expected host checks
  under2min; full build expected5min, finite15min bound per invoked tranche.
  Join owned children, release and notify the actual next compiler owner. [x]

N04-016.05 Return exact source/app/ELF/map/config/SDK/archive identities,
  unchanged compatibility, exact installed rollback and qualification limits
  to MechAgon. Commit/push logical checkpoints. A fresh selected hardware plan,
  preparation and actual bench admission remain separate. [ ]

Do not change EMOS, consumer source, production selection, firmware on either
board, startup or current Wolf inputs. Preserve the unfiltered diagnostic image
and informative failure evidence. Public version/production promotion and any
physical repair claim remain unselected.

## Actual first compile disposition

Source f3a102d5 is committed separately. Focused sanitizer checks pass246 retained
ExExt assertions,219 strict native assertions and70 counter assertions. The
identified full-build attempt stopped at its original fifteen-minute watchdog,
joined all observed compiler descendants and released the compiler slot. It
produced no deployable P4 image. No hardware was accessed and no filtering repair
is claimed. A new identified build tranche is still required; this independent
work does not block the final application case or its explicit UART1 alternative.

## Fresh complete-image tranche

After the expired first attempt is fully stopped and released, a new full-build
tranche selects the same clean source f3a102d5 and a fresh output/identity. The
matched UART build measured934 seconds; allow an expected twenty minutes and
a fresh thirty-minute whole stop including owned cleanup. No old watchdog or
output is resumed. Reconcile raw SDK-config hashes by verifying that any two
partition-path differences reference identical source and identical compiled
partition-table bytes. Keep all other composition checks exact. This candidate
is independent of MechAgon's final unfiltered attempt and explicit UART path;
no installation or additional application test is authorized by this build.

## Actual fresh complete-image result

Compiler241 produced the full identified candidate
`net-004-r04-b2026-11-06-09-24-54Z` from clean source
`f3a102d574df0d76a0bfab7676b9a5807cbdffd8` in934.859s. Linked/composition
validation passes; all owned descendants joined and the compiler slot released
with no queued successor. The expired first build remains a distinct failure.

| Artifact | Bytes | SHA256 |
|---|---:|---|
| Application |1764368|37ba69e3648ea2e7663d071149acc057fab64f8546af3d784afa711505f8e38e|
| ELF |36436040|f25a1d48c704f418b71baccd19ae4eacff7af16c11db354c90226d692db4cd64|
| Map |12380647|8645f1a8306ff617ce892a4d11d6dddf3c4dbe7d9c21959efe8cee647beea64b|
| SDK configuration |92590|65c50f9c20933ce87d53e219fcab87a16841dc2edca49505d75e1d470ea3afc9|

Retain exact BIN/ELF/map/configuration/dependencies/source archive and build
receipts with the component owner. This image is NOT installed and no physical
filtering pass is claimed. MechAgon's final unfiltered result and UART
continuation are independent; a future Extender-owned fixture comparison uses
normal fresh scheduling after consumer support.
