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
  Join owned children, release and notify the actual next compiler owner. [ ]

N04-016.05 Return exact source/app/ELF/map/config/SDK/archive identities,
  unchanged compatibility, exact installed rollback and qualification limits
  to MechAgon. Commit/push logical checkpoints. A fresh selected hardware plan,
  preparation and actual bench admission remain separate. [ ]

Do not change EMOS, consumer source, production selection, firmware on either
board, startup or current Wolf inputs. Preserve the unfiltered diagnostic image
and informative failure evidence. Public version/production promotion and any
physical repair claim remain unselected.

## Checked source checkpoint

The clean implementation worktree starts from published plan414cdff8. Its P4
source matches retained installed diagnostic sourcee14e0b8a after preserving the
cached VALID-count failure log (that leaf lived on the earlier owner branch).
Only the new strict reverse filter/lifecycle and corresponding SDK-fake checks
change from that diagnostic source; the existing RX descriptor remedy remains.
No EMOS or public caller ABI changes.

Three actual-component sanitizer methods pass:246 retained ExExt cases,219
strict native payload cases and70 VALID/CLOCK counter cases. The SDK fake checks
filter identities, enabling before PCNT/READY, counter/peripheral retirement
before VALID-filter disable/delete, all successful-path SDK fault points and
DMA retention until cleanup. One-byte intervals still succeed;3..6 sustained
edges still fail exact-two proof. The first compile caught misleading indentation
in the new fake; formatting was corrected before the passing checks. Two local
receipt-path mistakes changed no source/runtime behavior and were corrected;
all invoked children exited. Digital fake checks make no analog/glitch-width
claim. Host duration4.024s, not transport timing. Full candidate build follows.
