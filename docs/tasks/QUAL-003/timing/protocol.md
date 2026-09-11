# Private graphics timing experiment — r01

Status: draft implementation under the frozen QUAL-003 contract. Author
version preapproval covers graphics-timing-probe-r01, EMOS v0.1.13, P4 console
r11 and registry r70. This does not define the production callback API.

## Actors and packets

1. The Agon SD application requests every route with public `mos_oscli`, and
   sends every VDU byte through the ordinary EMOS counted-output API. EMOS owns
   both destination selection and reply admission. Mainboard UART0 carries
   Legacy traffic; the existing Port C UART1 wiring carries ExCom traffic.
2. Request: `23,0,EF,op,token_lo,token_hi,detail`. EF is unassigned in selected
   stock v2.16.0. Detail 0 disables duration recording; 1 enables it. Op 1 is
   admission/setup barrier, 2 is finite-work completion, 3 ends an output-only
   observation without inserting a queue marker. Op 4 retrieves one saved
   metric, with the final byte selecting metric 2–8 instead of detail. One
   request/response is outstanding; the result remains saved until next BEGIN.
3. Response: header `8C,16`, then `Q,T,G,A1,token_lo,token_hi,metric,source,
   value32,count32`. Multibyte fields are little endian. A1 identifies version
   1 while making the payload impossible to confuse with a valid keyboard down
   byte. Source 0 is mainboard, 1 is EDP. Stock packet IDs 8A/8B are echo and
   echo-end and remain untouched. Response 8C is unrelated to VDU subcommand 8C.
4. EMOS rejects incorrect size, magic, version or selected source, and requires
   a committed ExCom lease for UART1. Its existing private reply buffer and
   registered ISR callback deliver the record; no keyboard sysvars/counter/map
   are published for a diagnostic response. The application copies only a
   matching token/source and bounded metric index into nine fixed slots.
   Repeated matching metrics fail. Its callback preserves registers, does no
   MOS calls, I/O or formatting, and is cleared on exit.
5. Metric 0 admits the BEGIN (value 1, count detail). END returns metric 1.
   The application then requests metrics 2–8 individually; all nine slots must
   be present. The callback-arrival timestamp belongs to metric 1, so retrieval
   overhead is outside that interval. An initial burst-response prototype lost
   records during native review; serialized retrieval avoids manufacturing a
   receive-overrun measurement failure. Unknown,
   stale or mismatched requests never acquire a new completion token.

| Metric | Value | Count |
|---|---|---|
| 1 | Renderer-local interval, microseconds | Wait for normal drawing completion, microseconds |
| 2 | Native primitive execution, total microseconds | Primitive calls |
| 3 | Largest primitive duration | Scopes crossing measurement boundaries |
| 4 | Software-sprite processing, total microseconds | `showSprites` calls |
| 5 | Largest software-sprite duration | Scopes crossing boundaries |
| 6 | Scanline sprite decoration, total microseconds | `drawSpriteScanLine` calls |
| 7 | Largest scanline-decoration duration | Scopes crossing boundaries |
| 8 | 256 empty timer pairs, microseconds | 256 |

Nested primitive/software-sprite durations overlap and must not be added.
Boundary-crossing scopes are disclosed; aggregates contain only scopes that
started and ended within the same admitted window. Counters cover CPU work,
not DMA transfer, physical VGA presentation or browser presentation. P4 rows
are demand-driven; their measured count is not a 60 Hz cadence claim.

## Completion semantics

Stock `Canvas::waitCompletion(false)` actively drains on the caller; it would
change the measured execution context. `waitCompletion(true)` waits for an
empty queue but can miss a primitive already removed and still running. Neither
is used for the diagnostic completion marker.

The experiment adds a compiler-guarded `GraphicsFence = 126` primitive without
renumbering stock opcodes. The normal worker consumes it in FIFO order. Its
ordinary `showSprites` exit publishes completion after that scope finishes.
The requesting parser waits cooperatively, with a ten-second failure bound.
It never takes over drawing, adds a drawing budget or emits a sprite-refresh
command. Ordinary stock flush commands already present in a workload remain
unchanged. The same fence and scopes are injected into the stock mainboard
copy and enabled on the restored P4 backend.

## Workload and timing boundaries

1. The 64 cases preserve all selected page prerequisites and quiet stages.
   The generator serializes the existing audited VM calls exactly, including
   fixed-point truncation. All SD data is preloaded into a bounded RAM buffer
   before BEGIN. The largest current case occupies approximately 95 KiB.
   RST18 counts use BC16: larger stages are split into calls of at most 32768
   bytes, preserving every byte in order. Zero-length data does not invoke
   RST18's delimiter mode.
2. Page reset/cleanup and mode/route setup are outside measurement. Resource
   creation/uploads which belong to an original stage remain in its original
   position; their bytes are explicitly counted. They are included in stage
   submission/elapsed time, while native primitive aggregates identify drawing
   CPU time separately. Moving them ahead would change dependency semantics.
3. Each stage records submission ticks, terminal callback-arrival ticks,
   renderer-local time, native CPU aggregates, then a separate output window
   with no application VDU or SD activity. Ordinary mode 20 is selected only
   in autoexec on both renderers. Pixel probes follow, outside timing; record
   mismatches rather than hiding known stock/document differences.
4. One complete instrumentation-off pair precedes three on pairs. Mainboard
   runs the whole curated sequence first, then EDP. Off keeps the common fence
   and hook admission checks, but records no operation durations; it is not a
   claim of zero instrumentation overhead. Do not subtract the empty timer
   measurement as a universal correction.
5. Physical output windows last 120 raw MOS ticks: the selected MOS increments
   by two per VBlank. Always retain raw ticks and independently measured local
   microseconds; no subtraction between processor clocks. The explicit
   `review` argument uses one on pair and six-tick windows for functional
   emulator review only, never for physical performance evidence.
6. Every completed interval is appended, synced and closed on Agon SD. Setup,
   transport, timeout, probe and persistence failures are retained with a
   terminal incomplete result. Existing result files are never overwritten.
   Raw FAT emulator media exercises the real FatFS create-new/sync path;
   directory-backed emulator SD is inappropriate for these operations.

## Build and review boundaries

1. Official MOS/VDP references remain clean at v3.0.2/v2.16.0. The mainboard
   builder exports stock VDP c7ac293 and vdp-gl ac2dd598 into an ignored owned
   directory and applies only these diagnostic hooks. It retains stock platform
   options and pins dependency contents. No Pingo fork or renderer fix is used.
2. EMOS uses its own repository wrapper and full ROM/ABI/baud/runtime gates.
   The first diagnostic image is 130340 bytes, leaving 732 bytes under 128 KiB.
3. Fab uses its own userspace rendering adaptation, not the physical ESP32/P4
   machine code. It checks protocol, routing, fixture and durable file behavior;
   its times are not device performance evidence. The temporary native build
   matches stock's `getFilename`/`getFilesize` definitions to their size_t declarations because
   unsigned and size_t differ on the 64-bit host. No physical source changes.
   Stock's unused USERSPACE hex-loader missing-return warning is retained;
   no upstream bug fix is introduced to silence it.
   Missing Arduino `max` and heap-inspection interfaces bind to the equivalent
   host library functions in the disposable build, including actual allocation
   extent for a tile-layer debug message.
   The earlier project UART1 byte-peer adapter exited on `WouldBlock` when a
   large upload filled its host socket. The owning mos-agondev TEST-001 helper
   now retains bounded pending bytes and withdraws modeled CTS until drained.
   This corrects the test transport, not EMOS or physical UART timing.
4. Preserve the accepted r10 P4 and v0.1.12 EMOS bundles as rollback inputs.
   Before touching the mainboard, establish its stable serial identity and
   save/verify its actual flash image. A rebuilt stock image is not proof of
   the existing installed bytes. Failure to obtain the backup stops deployment.
   New emulator-coupled work stays uncommitted until Author validation.
