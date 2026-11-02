# Original fast transfer baseline and candidate readiness

The original fast client transfers1.1MB at3.88kB/s uploading and2.17kB/s
downloading. Both directions verify byte for byte. The matched replacement P4
build passes source/composition checks but remains uninstalled: P4 SD mount
times out again after a restart. Physical card access is the remaining prerequisite.

## Results

Exact1,100,000-byte payload; slowest direction first, decimal kB/s:

| Direction | Original fast seconds | Original fast kB/s | UART records | New staged path |
|---|---:|---:|---:|---|
| Agon to host | 507.445 | 2.168 | 5,093 | Not run; P4 card unavailable |
| Host to Agon | 283.396 | 3.881 | 5,193 | Not run; P4 card unavailable |

Upload includes the existing fast client's HELLO/BEGIN/WRITE/FINISH/ACTIVATE,
with payload prepared and connection/path preflight outside timing. Download
includes existing READ requests; byte comparison/hash is outside timing.
Host monotonic seconds are elapsed wall time, without independent oscillator
calibration or CPU-time claims. Compilation and passive serial observation
stopped before timing. The printer mirror was disabled. No CRC or whole-file
verification download is part of upload timing; the separately timed download
provides the exact byte proof. This is one matched directional pair, not a
distribution or a performance guarantee. Total timed baseline runtime is790.841s;
setup/build/readbacks are separate. Raw timings/identities are in
[BASELINE-R01.json](BASELINE-R01.json).

## Preserved state and source

1. Fresh128KiB EMOS ROM equals the accepted v0.1.27 companion byte for byte;
   current listener and108-byte startup are preserved. Startup contains LOAD,
   not test RUN/EXEC; no startup edit occurred. Entry mainboard/P4 modes are0.
2. Fresh P4 boot reports the incoming r25 build. No P4 flash occurred, and no
   new whole-chip readback is claimed. Mainboard VDP remains untouched; observed
   W3D debug output is not a firmware hash or stock-release identification.
3. Candidate `indexed-hdmi-r27-b2026-11-02-22-32-18Z` is built from clean
   `512d18668e19a278ed6638595cf60fae01787cc2`, adding exactly the seven staged
   transfer files/deltas to incoming source9c393360. The source branch is
   `codex/remote009-staged-r01`. HDMI, USB, controller, compiler, pin profile,
   partition table and SDK configuration agree with r25 except output paths.
   Candidate bytes/hash are recorded in JSON. Private-configured generated
   firmware remains local-only; it is not a published production archive.

## Remaining dependency and setup corrections

P4's own SD status reports ESP_ERR_TIMEOUT twice across fresh boots. USB logs
show `sdmmc_init_ocr: send_op_cond (1) returned0x107`, followed by failed card
initialization. Formatting is disabled; no card formatting/removal/file change
was performed. This does not distinguish an absent/loose card from another
electrical or driver problem. Check/reseat the P4-PC card with power off before
further deployment; the Agon card is working. The P4 mount implementation caches
failure until restart, so repeated status requests are not fresh mount attempts.

Host keyboard readiness is not completed CLI startup/SAVE handback. A brief
startup settle plus acknowledged listener exchange, and a separately staged
explicit EXEC command file sequencing SAVE then listener, resolved preparation
pacing without replaying uncertain writes or altering startup.

An attempted direct pyserial P4 observation captured a fresh P4 boot and lost
EMOS input admission. It must not be reused as a passive opener; intent is not
proof of passivity. Restore the Agon handshake after P4 restarts. Existing
joined-control capture guidance remains controlling; no new universal P4
serial-open qualification is claimed.

R09-06 remains partial. No new speedup, staged hardware pass, production
promotion or release acceptance is claimed.
