# Live rolling scanout integration

## Current result

The latest684×384 rolling image completes marked3600-update hardware Nurples
at nominal60/s with57% median active-work headroom, no scanout faults and clean
buffer destruction. Ordinary menu/mode changes, Escape and CLI commands pass.
The earlier crash was an84-byte internal mutex allocation failure: ordinary
malloc now prefers PSRAM, as does the unchanged primitive queue payload; RTOS
control and three scanout slots remain internal. Loaded free internal RAM rises
from83 to22691bytes. See [memory results](../HDMI-002/MEMORY-RESULTS.md).

Original startup/configuration are restored; the tested684 candidate remains
installed for Author manual review. ExCom automatic SD admission after ordinary
exit returns503; EMOS Legacy restores access without reset. That remains open,
as do slight tearing and broader qualification. The earlier848 image is service
recovery only, not a hardware-Nurples handback. Historical failures below and
[full wide results](../HDMI-002/FULL-WIDE-RESULTS.md) retain diagnostic evidence;
they do not describe the current installed build.

| Candidate | Outcome | Next change |
|---|---|---|
| rgb-001-r04-b2026-10-07-06-21-39Z | Compile rejected protected sprite access | Expose snapshot access through the owned P4 controller; upstream base unchanged |
| rgb-001-r04-b2026-10-07-06-29-15Z | Build/link/source/silicon checks pass; flash segments verify; startup asserts on strip allocation | Move immutable scene metadata to PSRAM; use15blocks/three32-row SRAM slots instead of12blocks/three40-row slots |

The revised strip storage requires244224bytes instead of305280bytes, a20% reduction.
It still retains three buffers and the original stock sprite painter. Shorter
strips also shorten available refill time; the guard becomes1600µs and runtime
measurements must establish whether that is adequate. Heap allocation diagnostics
identify available capacity/contiguity at each slot. No test is passed merely by
compiling this revision.

Host tests pass for snapshot ownership/deep-copy lifetime, arena growth/alignment,
RGBA2222/RGBA8888, clipping, overlap/XOR, empty scenes and both32/40-row boundaries.
The non-rolling real-renderer regression passes. Nine build-selection tests pass.
No passing full-application visual or Nurples result was available at that stage.

The companion scan-scroll-suite-r03 hardware Nurples fixture reproduces the r02
binary exactly before changing only hardware-sprite admission/type and identity.
It retains the same simulation, timing, input polling and assets. Its maintained
builder is tests/performance/scan/hardware_nurples.py. New physical runs require
fresh result paths; original SD startup and game binaries remain preserved.

Local build/capture/rollback evidence is retained under agents/sprite001/integration.
The original normal848×480 image was restored/readback-verified after the startup
failure. Production remains unchanged.

The15-block revision `rgb-001-r04-b2026-10-07-06-41-46Z` starts scanout cleanly:
about60Hz, no underrun/late/overlap/fault, maximum observed refill734µs and minimum
ready lead1326µs at the idle native mode0 output. However, Ethernet initialization
then fails to allocate RX DMA buffers. The network state is Faulted, not merely
waiting for DHCP. Retained boot output directly identifies the allocation.

The next candidate changes only this experimental build's ordinary-malloc PSRAM
preference from16384 to1024bytes, preserving Ethernet buffer counts, DMA-capability
requirements and SRAM scanout storage. This is an allocation-placement experiment,
not an established remedy. It must pass normal service startup before game tests.
The exact normal firmware was restored again; no invalid fixture measurements
were taken through the failed network state.

The06:56:34Z candidate starts Ethernet and accepts foreground listener commands.
Its idle capture reports maximum refill729µs, minimum ready lead1331µs, zero
late/underrun/sequence/overlap/fault counts, but only about12KiB internal memory
free. P4 card status reports mounted=false/ESP_ERR_NO_MEM. Automatic WebDAV
HEAD/MKCOL therefore refuses503; the fixture never starts and no result is
claimed. The foreground listener was exited normally. SD startup retains the
original38bytes and no timed run/config was installed. This is a service
prerequisite failure, not a rendering benchmark.

The next bounded build increases the internal-only reserve from32KiB to64KiB
while retaining the1024-byte ordinary-malloc preference. Peripheral DMA memory
requirements and buffer counts remain unchanged. This is unqualified until
SD mount, file service and loaded rendering pass. Meanwhile the standalone
native512×384 pattern uses an independent image with no Agon services.

The07:14:02Z64KiB-reserve candidate fails at startup: before allocating its
third81408-byte strip, total internal free memory is206343bytes but the largest
contiguous block is71680bytes. Flash segment readback passes; service startup
does not. The native512 pattern is restored after the failed helper finishes.

The next bounded candidate restores the32KiB reserve and places only the two
32KiB file-service worker stacks in PSRAM through pinned IDF's
xTaskCreateWithCaps/vTaskDeleteWithCaps pair. The default build is unchanged.
These task paths perform FAT, UART and socket work, not SPI-flash/NVS operations;
future cache-off/flash operations would require revisiting this placement.
No stack-size reduction, peripheral-memory relaxation or upstream patch is made.
Compile validation checks the existing external-stack configuration explicitly.

## Loaded-transition failure and return to mode work

Build rgb-001-r04-b2026-10-07-07-37-07Z passes compilation and source/artifact
validation (the preceding validation-only failure checked IDF’s deprecated
external-stack alias, corrected to its canonical option). Flash segments verify.
Idle scanout remains about60Hz, but P4 SD still reports ESP_ERR_NO_MEM; the exact
failed SD allocation has not been localized. USB startup also reports HCD pipe
allocation failure in the retained subsequent boot log. Moving the storage-worker
stacks does not qualify normal services.

The foreground listener lacks newer directory capability0x20. The bounded test
setup therefore uses documented MOS MKDIR/RENAME only after acknowledged
listener EXIT, with independent STAT/byte verification. This bypasses the P4
staging-card prerequisite without modifying the installed listener. Original
startup is preserved and each transition recorded.

The one-sprite attempt fails before its measurement window: immediately after
ExCom admission, P4 asserts in vQueueDelete(NULL) and restarts. Retained stack
addresses resolve to BitmappedDisplayController’s destructor (vendored
displaycontroller.cpp:508), destruction of StockBoundController<VGA16Controller>,
and changeMode/consoleControl. The native primitive queue is null; an allocation
failure is plausible given the SRAM pressure, but the allocating call has not
been captured. No null-delete workaround or upstream fix was introduced. There
are no valid small-fixture results and the longer hardware Nurples run is not
executed. Idle DMA success is explicitly insufficient.

The exact known full848×480 image is restored. Its P4 card mounts successfully,
separately confirming service recovery. A controlled startup-recovery invocation
may briefly run the already prepared fixture on that image only to reach the
listener and restore the original startup; its samples are excluded. Native
512×384 pattern review then resumes, with other timing candidates compiled but
unflashed. Full rolling integration remains open, not accepted or promoted.

Recovery completes: acknowledged Escape exits the prepared case on the known
working image; original startup is restored by independent full readback and
normal reset. Final receipt confirms ready/neutral input, no held/queued keys,
offline idle listener and closed/nonoverflowed measurement windows. Original
Nurples binaries/assets and run.cfg remain unchanged; hardware-r03.bin is the
only separately deployed test companion. The native512 pattern is then restored
for Author review, deliberately without Agon services. No active capture, fixture
or transfer remains. Local closeout: integration/restoration-final.json.

## Offline native-width preparation

Pinned IDF `components/freertos/heap_idf.c` routes `pvPortMalloc` to internal
8-bit-capable RAM, including dynamically allocated queues. Reducing ordinary
malloc's internal preference therefore cannot move FabGL's primitive queue to
PSRAM. Vendored `BitmappedDisplayController::setDoubleBuffered` creates a
1024-element queue in a single-buffer mode; P4 mode staging retains the old
controller while creating its replacement. This establishes the allocation
constraint, not the precise failed allocation in the retained assertion.
No queue shortening, PSRAM queue substitution or upstream null-delete patch
is made.

Under the Author's native-mode priority, compile-only preparation selects the
same 512×384 signal as the standalone pattern, twelve 32-row blocks and three
SRAM slots. It saves 96768 bytes (39.6%) relative to 848-wide rolling output.
The C DMA derivative and C++ scene adapter share the selected geometry; both
retain the 1600µs abort and original sprite painter. Default and 848-wide
behavior remain available. Physical service/mode/game tests still require
monitor acceptance of the pattern, which remains installed and unchanged.

The retained failed build's DWARF records `sizeof(Primitive)=18` and
`sizeof(QueueDefinition)=84`: one stock single-buffer queue requests 18516 bytes
before allocator overhead. That already exceeds the roughly 12 KiB internal
free reported at idle. P4 candidate mode staging can also require the old and
new queues simultaneously. This strengthens the memory diagnosis, while the
exact allocation failure at the transition still lacks a captured hook.
Native-width preparation preserves queue behavior.

Build `rgb-001-r04-b2026-10-07-08-21-48Z` now passes full compilation and
source/link/config/silicon validation. The actual C DMA compile action selects
512-wide geometry, and a negative control removing that definition is rejected.
ASan/UBSan scene tests pass at both 848 and 512 widths; HDMI geometry/conversion
checks pass at 1280, 848 and 512 widths, and the existing independent browser
input test passes. The original sanitizer attempt was sandbox-limited; the
reported passes use the unrestricted local test process. No hardware operation
was performed in this preparation turn.

[Native512 preparation receipt](NATIVE512-PREPARATION.json) records exact build
and factory identity. It remains unflashed and unqualified. The unchanged
standalone pattern's physical picture gate remains pending; that gate cannot
be replaced by host tests or the full build's success.

The next small-sprite and deterministic hardware-Nurples runners are prepared
locally with fresh result destinations and explicit full-image identity guards.
Offline checks verify the candidate bytes; negative checks reject the installed
standalone image before network, SD, input or reset operations. They preserve
original startup/configuration and use the retained foreground listener. They
have not executed on hardware. The unattended goal is blocked on the pending
native512 monitor observation; no host job remains active and no further
bench change occurs while that review is pending.

## Author timing review and target correction —2026-10-07

The standalone512×384 picture fails: intermittent flicker and loss of image.
The Author also clarifies512×384 must remain a game canvas centered in a
widescreen HDMI signal. HDMI-002 therefore tests the prepared684×384 carrier
next. The512-wide full build and guarded runners remain unexecuted and are no
longer the deployment target. A matching684-wide full build would need196992
bytes for its three32-row slots, not147456; SRAM/peripheral readiness must be
revalidated. No full sprite or hardware-Nurples pass is inferred.

The subsequent684×384 carrier passes bounded Author review: steady continuous
output, correct circle/square aspect and visible full border. Misplaced color
labels are a fixture-only spacing error. A corrected centered512×384 pattern
preserves the exact successful timing and bridge code. This qualifies neither
full services nor sprite integration; the old512-wide full image stays unflashed.
