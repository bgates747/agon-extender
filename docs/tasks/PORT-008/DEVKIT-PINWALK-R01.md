# PORT-008 — Original DevKit header pinwalk

Reuse the exact retained one-shot [HW-002 header pinwalk](../HW-002/pinwalk/README.md)
to attribute the Author's relocated DevKit probes. This is the isolated historical
header diagnostic, not a product transport bypass or a new pinwalk implementation.
No parallel payload/DMA integrity conclusion follows from pulse attribution.

## Full-header visual reference

The Author requested literal prior art for the physical header positions and
immutable Agon ribbon colors. The existing [original wiring drawing](../../../hardware/designs/light2-harness-r01/legacy-evidence/wiring-diagram.svg)
already contains all forty DevKit header cells. The [header-only reference image](devkit-header-reference-r01.png)
extracts their labels and fills unchanged, aligns both complete headers, spells
out conductor colors and highlights the three intended control destinations.
It uses the schematic-derived [Rev D1 pinout](../../../hardware/designs/light2-harness-r01/legacy-evidence/esp32-p4-devkit-rev-d1-pinout.md):
component side, Ethernet at top, EXT1 left, EXT2 right, pin20 above pin1.
These are intended connections, not newly verified as-built positions.
Colors identify harness conductors, not analyzer leads. At the Author's request,
external pull annotations show READY_N/VALID_N 10 kΩ up to Agon 3.3 V and CLOCK
10 kΩ down to common ground, from the original profile and the Author-reported
restored controls in [the hardware record](DEVKIT-HARDWARE-R01.md). Data lanes
retain the eight 15 kΩ pull-ups to Agon 3.3 V documented in the
[simplified harness](../../../hardware/designs/light2-harness-r03/README.md).
The separate 220 Ω data-series resistors are distinguished from pull resistors;
no obsolete buffer circuit is adopted. The
[renderer](fixtures/generate-devkit-header-reference.py) preserves original
header labels/colors and adds these annotations reproducibly.

The later [breadboard landing reference](forward-r01/normal-forward-wiring-and-probes.svg)
has a different installed-view orientation: EXT2 left, EXT1 right, pin1 at top.
Do not transpose that view onto the component-side board view. The orange
outlines in the extracted image identify black CLOCK at EXT1-15/GPIO14,
white VALID_N at EXT1-14/GPIO13 and blue READY_N at EXT2-13/GPIO20.

DP01 [x] — Verify the exact retained September13 one-shot binary and unchanged
GPIO assembly. Stage it on the Author-confirmed Lenovo-mounted Agon card,
preserving and readback-verifying original startup. Startup selects mode3,
loads/runs the fixture, then retains original normal startup commands for the
marker-absent recovery path. The fixture consumes its existing one-shot marker
before GPIO, emits ordinal pulses once, releases pins and waits for reset.
Leave card mounted and await explicit return to Agon before any Agon reset.

DP02 [x] — Reuse the existing USB-ROM input-hold tool, adapting only its pin
list to include DevKit data/control/auxiliary transport pins and adding input
level readback. Independently verify input ownership; no firmware flash.
Verify exactly one analyzer and current eight-channel map. Do not infer probe
identities from wire colors alone; use observed pulse counts/timing.

DP03 [x] — After Author confirms card inserted, acquire100kHz/all8channels
for60seconds, verifying delivered samples before one Agon reset. Require the
full saved extent, the complete ordinal sequence and at least five quiet seconds
after it. Existing map observes D2/D4/D5/D6/D7 plus READY/CLOCK/VALID; D0/D1/D3
are unobserved. Expected driven counts are3/5/6/7/8 and9/10/12 respectively.
CLOCK's external pull-down can add a final release-to-low edge; distinguish
that edge from an emitted pulse rather than diagnosing a count error blindly.
Retain waveform evidence and report swaps/missing pulses separately from MCU
input readback and from payload correctness. No sweep or automatic retry.

DP04 [x] — Preserve completed capture/results. Explicitly release ROM hold
after the walk is finished and pins released. Restore exact pretest startup
and the appropriate previously verified normal DevKit firmware/input path
without new firmware backups. Record actual restored state and stop; do not
reset into a live raw sender with full UART firmware driving the same pins.

Exact specimen, analyzer channel attachments, card identity, hashes, helper
commands and current installation remain in ignored local evidence. This run
does not change EMOS, mainboard VDP, production selection or wiring.

## Authorized reverse walk — bounded follow-up

### Repaired connection repeat — 2026-10-10

The Author found that the three Agon control conductors reached their landing
headers/probes but were not carried onward to the DevKit GPIO pins. The Author
now reports those paths repaired using one 220 Ω series resistor per control.
Record the revised assembly as `devkit-parallel-control-harness-r02`: existing
data connections/pulls retained, control pulls unchanged, three control paths
completed through 220 Ω. This is an Author-reported assembly change pending
electrical test, not a newly qualified product harness.

Analyzer contacts remain on the Agon side of the series resistors. Thus P4-driven
pulses must traverse the repaired resistor/conductor paths to reach the probes.
The disconnected paths explain the preceding reverse failure and invalidate
the assumption that those probe contacts were themselves P4-pin contacts.
No DMA failure was demonstrated. The P4-PC remains unmodified and requires
220 Ω series resistors on all eleven data/control signals before a comparable
follow-up; do not transfer this DevKit acceptance to that board.

RW05 [x] — Repeat the existing bounded reverse helper once, unchanged, with
fresh evidence. Preserve the preceding informative capture. Confirm normal
input admission first, hold powered Agon in reset, check all eleven P4 driven
readbacks and the eight unchanged probe channels, then independently verify
P4 output release and restore normal application/input admission. No flash,
SD mutation, arbitrary GPIO sweep or automatic retry. Report continuity
separately from payload correctness; pause on any discrepancy.

#### Repaired repeat result

All eight observed paths pass. READY_N and VALID_N now show their expected
P4-driven pulses at the Agon-side probes through the repaired series paths.
CLOCK shows ten commanded pulses plus the initial enable-to-high and final
release-to-pull-down transitions. Every driven low/high P4 readback passes for
all eleven tested signals. The preceding zero-control response is explained
by the Author-identified missing connections; it is not a demonstrated DMA fault.

| Signal | P4 GPIO | Commanded pulses | Observed falling / rising edges | Result |
| --- | ---: | ---: | ---: | --- |
| READY_N | 20 | 9 | 9 / 9 | Pass |
| CLOCK | 14 | 10 | 11 / 11 | Pass; enable/release edges included |
| VALID_N | 13 | 11 | 11 / 11 | Pass |
| Data2 | 23 | 3 | 3 / 3 | Pass |
| Data4 | 32 | 5 | 5 / 5 | Pass |
| Data5 | 10 | 6 | 6 / 6 | Pass |
| Data6 | 33 | 7 | 7 / 7 | Pass |
| Data7 | 9 | 8 | 8 / 8 | Pass |

Full acquisition: 6,000,000 samples at 100 kHz, 60 seconds, with 49.49984 seconds
quiet after the last observed edge. Data0/1/3 remain unprobed. P4 outputs were
independently released before restarting the unchanged normal application;
Agon stayed held until HTTP initialization and then recovered neutral admitted
keyboard input. No flash, SD mutation or payload transfer. No active capture,
reset hold, serial or automated input remains. Fresh evidence is retained under
the ignored reverse-pinwalk-r02 directory alongside the prior informative failure.
The next useful step is the existing bounded historical payload comparison.

The Author authorizes the P4-to-probe direction after the forward walk. Both
boards stay powered. The Pi holds the existing Agon reset transistor asserted;
the eZ80 product specification states reset stops execution and configures GPIO
as inputs (PS0153, Reset Operation p32; port DDR reset values p44). Turning off
only Agon would remove its pull-up supply and does not isolate connected GPIO.
This is an isolated bench diagnostic, not a supported EMOS transport bypass.

RW01 [x] — Adapt the existing P4 USB-ROM input setup and capture tools. Verify
exact DevKit identity and GPIO register constants against retained IDF5.5.5
ESP32-P4 hw_ver1 headers. Record tool/source hashes. No firmware build/flash,
SD mutation, probe move or EMOS/mainboard VDP change is required.

RW02 [x] — Pi asserts and verifies the Agon reset hold before P4 output starts.
Host holds P4 in USB ROM, releases all transport outputs, disables internal
pulls/sleep selection on tested pins, and verifies software GPIO routing.
Verify delivered analyzer samples before enabling any test output. P4 pulses
one pin at a time: eight board-mapped data GPIOs emit ordinals1–8, READY emits9,
CLOCK10 and VALID11. Each slot ends with that pin released. Read back the P4
input at driven low/high states, retaining discrepancies separately from probes.
No neighboring/unknown GPIO sweep or automatic repeat.

RW03 [x] — Preserve full60-second/100kHz capture and at least five quiet seconds
after final test release. Attribute observed probes by pulse count and slot
timing. A final CLOCK release-to-pull-down edge is expected; no READY/VALID
response at a probe must remain distinguishable from a swapped signal or a
failed P4 output readback. Five data lines and three controls are observed;
unprobed data lines cannot receive an end-to-end pass.

RW04 [x] — Independently verify all P4 transport outputs disabled before
releasing Agon reset. Restart unchanged normal P4 application while Agon remains
held; await its HTTP initialization, then release Agon and verify neutral keyboard
admission from unchanged original startup. On failed P4 release verification,
leave Agon held in reset and report the explicit recovery boundary; never let a
fixed timeout release reset while a P4 output might still be active.

Register reference: retained ESP-IDF components/soc/esp32p4/register/hw_ver1/
soc/gpio_reg.h, io_mux_reg.h and reg_base.h. GPIO OUT/W1TS/W1TC offsets4/8/12
(upper bank16/20/24), ENABLE offsets32/36/40 (upper44/48/52), PIN0 offset116
with PAD_DRIVER bit2, and software output selection GPIO256 are material here.
The existing [reset circuit](../../bench-reset.md) and current DevKit board JSON
are reused; private endpoint/reset-line identities remain in local configuration.

### Reverse-walk result — 2026-10-10

The five probed data connections conduct the expected P4 pulses. **None of the
three control probes sees its configured P4 GPIO toggle**, although P4 input
readback confirms every driven low/high state for all eleven tested GPIOs.
Together with the preceding forward walk, this localizes the unresolved
discrepancy to control electrical paths/header assignment, before PARLIO/DMA
or transfer timing. It does not identify a specific broken contact or establish
where those wires actually land. No neighboring GPIO sweep was performed.

| Probe signal | Configured P4 GPIO | Reverse pulses expected | Observed | P4 own low/high readback |
| --- | ---: | ---: | ---: | --- |
| READY_N | 20 | 9 | 0 | All nine pairs correct |
| CLOCK | 14 | 10 | 0 | All ten pairs correct |
| VALID_N | 13 | 11 | 0 | All eleven pairs correct |
| Data2 | 23 | 3 | 3 | Correct |
| Data4 | 32 | 5 | 5 | Correct |
| Data5 | 10 | 6 | 6 | Correct |
| Data6 | 33 | 7 | 7 | Correct |
| Data7 | 9 | 8 | 8 | Correct |

READY/VALID probe levels remain high and CLOCK remains low throughout. No
additional control pulses appear on the five observed data channels. Data0/1/3
were toggled with correct P4 readback but were not probed and receive no
end-to-end pass. Capture has exactly6million samples at100kHz/60seconds;
last observed edge6.48344seconds, followed by53.51656quietseconds. The host
completed all eleven pulse slots well before the end of the capture. Host-paced
pulse widths are attribution evidence, not calibrated throughput measurements.

All fourteen mapped/auxiliary P4 transport outputs were independently verified
disabled before the unchanged normal P4 application restarted. Pi kept Agon
in reset through P4 HTTP initialization, then released reset. Fresh keyboard
status is ready/neutral, held0/pending0, locale1. No flash or SD mutation; original
startup, EMOS, mainboard VDP, probes and wiring unchanged. No active reset hold,
serial connection, capture or automated input remains. Exact executed tool source,
manifest/hash, pad readbacks and waveform retained in ignored reverse-walk evidence.
After preserving that executed source, the maintained helper gained an explicit
post-release host timestamp and nonzero exit for incomplete recovery; these host
bookkeeping changes were syntax-checked and not re-run on hardware.

## Recovery boundary — 2026-10-10

The exact normal September30 DevKit P4 image was restored and all four flash
segments independently verified. EMOS/mainboard VDP remain unchanged. The host
then sent one separate recovery Agon reset after P4 initialization; keyboard
admission did not complete within the 60-second observation window. No retry.

**Preparation error:** the retained fixture returns status1 when its one-shot
marker is absent. The temporary startup incorrectly relied on MOS continuing
past that failed RUN to its original keyboard-admission commands. Source review
establishes that nonzero return. The Author confirms an error executing autoexec
line3 (`RUN`), reported as an SD-access error, matching the marker-absent failure
path. This is not evidence of a new physical card fault. Do not claim keyboard
recovery or restored startup.
The Author returned the card to Lenovo. Exact original38-byte startup was
restored offline, synced and independently read back; original backup and
temporary-startup archive were verified first, and marker absence confirmed.
The card was left mounted for the Author, who subsequently returned it to Agon,
reset and confirmed keyboard input extender. Independent read-only HTTP status
confirms a fresh boot, ready/neutral keyboard, zero held/pending events and locale1.
Recovery is complete. No automated input, reset, capture or serial process remains.
Do not re-arm the walk or modify the frozen binary. The READY/VALID electrical
discrepancy below remains unresolved; successful recovery is not parallel-transfer
qualification.

## Results — 2026-10-10

The existing pinwalk reached every expected signal at the eight probe contacts.
The five observed data lines and three controls match their expected pulse
ordinals; no swap or absent signal was observed there. This does **not** prove
continuity from those contacts to the configured P4 silicon inputs. READY and
VALID remain an unresolved discrepancy: the analyzer ends high on both, while
independent P4 register reads immediately before/after the walk report low on
GPIO20 and GPIO13, with both input-enabled and output-disabled.

| Analyzer channel | Expected signal | Driven pulses expected | Falling edges observed | Result |
| --- | --- | ---: | ---: | --- |
| D1 | READY_N / Agon PD4 | 9 | 9 | Expected ordinal |
| D4 | VALID_N / Agon PD7 | 12 | 12 | Expected ordinal |
| D6 | CLOCK / Agon PD5 | 10 | 11 | Ten pulses plus final release to pull-down |
| D0 | Data7 / Agon PC7 | 8 | 8 | Expected ordinal |
| D2 | Data5 / Agon PC5 | 6 | 6 | Expected ordinal |
| D3 | Data2 / Agon PC2 | 3 | 3 | Expected ordinal |
| D5 | Data4 / Agon PC4 | 5 | 5 | Expected ordinal |
| D7 | Data6 / Agon PC6 | 7 | 7 | Expected ordinal |

Capture: 100,000 samples/s, exactly 6,000,000 samples / 60 seconds. Delivered
samples verified before the single Agon reset. The final observed edge is at
15.65506 seconds, followed by 44.34494 quiet seconds on all eight channels.
CLOCK returns high after its tenth low pulse, then falls when released; that
eleventh falling edge has no later rise and is not an extra emitted pulse.
Data0, Data1 and Data3 were not probed. No payload, DMA or parallel-transfer
test was performed. Exact run identity, waveform, hashes and P4 readbacks are
retained in ignored local evidence referenced by the owning task.
