# Pure UART fixture — uart-data-probe-r01

Experimental, not a production VDP command. Both destinations retain ordinary
stock bufferWrite/readIntoBuffer and send_packet paths. Mainboard input is stock
VDP v2.16.0 plus this probe; P4 input is the measured image's archived source plus
this same probe. No graphics fence, forced drain, per-byte timer, renderer change
or browser consumer. Initial video modes are selected outside the fixture.

## Private observation envelope

Request: `23,0,EE,op,token16,length16,pattern8` (nine bytes, little endian).
EE is unassigned in the pinned stock switch. Compile the include only in the
identified diagnostic images. It never alters ordinary VDU behavior.

Responses use the existing EMOS private8C/16-byte path:
`Q,T,G,A1,token16,kind8,source8,value32,count32`. Source0 mainboard,1EDP.
Its installed source/magic/length admission remains unchanged; the fixture owns
the existing ISR vector only while running. The callback copies fixed words or
8payload bytes and counters, with no MOS/I/O/printing/allocation. No new EMOS
firmware is needed for the initial baseline.

1. Op1 begins forward observation, returns kind0 admission, then records local
   micros. The application next uses ordinary VDU23,0,A0,64010;0,length;data.
   The owned buffer is cleared before each case outside timing. Length0 is a
   no-upload control; it does not invoke zero-count MOS delimiter output.
2. Op2 closes forward timing at handler entry, before checking buffer content,
   returns kind1 elapsed_us and observed_total_bytes. Exact verification uses
   the deterministic pattern over every stored byte, preserving block order.
   Op3 returns kind2 mismatch_count and first_bad_offset (FFFFFFFF if none).
   The verification work is outside the timed interval; op2 reply latency
   includes it and is explicitly not pure upload time.
3. Op4 emits length packets (1/8/64/256 initially), kind96, token equal to packet
   index0..length-1, and8pattern bytes each. Then kind3 with the request token,
   local enqueue duration and packet count. The application preallocates output
   storage and checks exact bytes/order after timing. Total UART return bytes
   are18*(packets+1); useful test data is8*packets. Maximum initial queued reply
   is4626bytes, below current EDP8192byte staging capacity. Callback loss fails
   the case; it is not silently retried or hidden by throttling.
4. No simultaneous arbitrary bidirectional traffic is claimed by these steps.
   Add a bounded stock-compatible concurrent case only after separate directions
   pass; record any necessary plan amendment before implementing it.

Patterns: zero,FF,alternating55/AA, and xorshift32 with initial state12345678hex
(each byte uses the next state low8bits; unsigned32 wrap). Forward lengths:
0,1,63,64,65,255,256,257,4095,4096,4097,32768,65535. Three measured repetitions,
first allmainboard forward then allP4 forward, then both return passes. Return counts1/8/64/256 with pseudorandom bytes.
A short smoke selects a subset before the full matrix. A failure closes/syncs
its CSV, releases the callback, attempts application-permitted Legacy --keep-display return and leaves the result
visible. Fixture returns zero to let the recovery EXEC continue; its terminal
CSVstatus, not MOSexit, owns pass/fail. Never overwrite prior results.

Each case records route,repeat,pattern,length,direction,raw send/receive ticks,
destination elapsedus,expected/observed bytes,errors,case status. Store results
between cases only, closed/synced to physical SD. Collection uses accepted SD
service afterward; captures are not streamed during timing.

## Recovery and comparison

Preserve actual flash/startup before replacement and retain verified rollback
images for both processors. Preserve EMOS16 and keyboard/SD contracts. Deploy
only identified clean committed fixture inputs. Separate probe-baseline images
from bulk-read/return-alignment candidates. Same payloads and fixture must run
on both. No pure-transport claim from graphics-loaded historical results.
After each firmware pair, verify keyboard neutral admission and SD read/write;
return through Legacy mode and restore ordinary startup. Retain failures once,
diagnose before continuing, and do not reset repeatedly without evidence.

## U10 bounded simultaneous-traffic extension

Before rendering, add an optional application `duplex` mode using the existing
probe and ordinary commands. No firmware/protocol change. For each destination,
three repeats of257/4096/65535random forward bytes overlap an outstanding request
for256reply packets (2048verified return bytes). Arm forward observation and wait
for its admission, request the return burst, immediately submit the stock buffer
write while the existing ISR accepts replies, then verify both directions.
Store two rows per trial: duplex-forward and duplex-reverse,36rows total.
Exact forward bytes, exact return sequence/content/count, terminal status and
Legacy/SD recovery must pass. The destinations retain stock command ordering;
this does not promise simultaneous parser execution.

Forward destination elapsed includes handling the preceding return command and
its scheduling; label it mixed-traffic completion, not pure upload rate. Return
eZ80 timing ends at its final reply, with the same coarse timer. No SD access
or additional producer input during either timed interval. Keep the original
336case invocation unchanged so its comparisons remain repeatable.

## U11 paired rendering continuation

After the complete pure-data matrices and wire attribution, reuse QUAL-003's
exact framebuffer-first39case fixture and corpus: app SHA256
be39dd91e939b3e1c861136b50d83528882b0d1c90b697d2f18bc15590a0777a,
mainboard graphics diagnostic SHA256
529808bd1d3f0e9ea04cb13ca1142032da8431fe26605932ffc46738d2dd17cd.
Both images and the original624interval baseline already exist; no fixture,
renderer, corpus or timing algorithm is changed. Keep current P4 stock-UART
ordering candidate; its existing graphics diagnostics are the same as the
baseline and its extraEE pure probe is unused. Record both image identities.

Use fresh owned SD binary/batch names, verify startup remains unchanged and
read back the staged app/batch before execution. Both displays are mode20,
512×384,64colours,singlebuffered; external MOS batch selects modes before the
fixture. The39case selection omits all BSP30 population stress; four repeats,
two routes, draw/output phases produce624intervals. Eight known paired SHP23
probe differences remain recorded as baseline mismatches, not new failures.

No browser/video output or serial observer. Save P4 frame-timing counters
before/after and require zero new snapshots. SD file collection follows timed
work, with a20minute bounded recovery wait. Validate exact row/metric/case
sequence against the retained corpus, terminal result and known probe outcomes.
Compare destination load, primitive draw and total draw separately to stock
and to the earlier unchanged-P4 run. Do not subtract transport from rendering
using unrelated clock scopes. Preserve raw results, failures and timing limits.

Temporarily replace only the mainboard app region after checking the installed
pure-probe identity and partition table. Final stock restoration must cover
**all erase sectors touched by either temporary image**, using the actual
pre-test4MiB backup; the graphics diagnostic is larger than the pure probe.

Documentation correction during preparation/collection: the retained fixture's
two phases are `draw` and `output`, as its unchanged protocol, validator and
original baseline specify. An earlier paragraph here called them load/draw.
Loading-heavy stages remain inside those intervals; there is no isolated load
timestamp. No program, procedure execution, metric or hardware changed for
this naming correction.
