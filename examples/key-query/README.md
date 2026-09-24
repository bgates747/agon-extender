# Virtual-key query witness

## Reuse boundary

This retained fixture is not a current deployment recipe. The source still writes `/test/keyquery.csv`, outside the current evidence layout. PORT-003 owns a source/path refresh before a new run.
Use [SD layout](../../docs/sd-layout.md),
[current SD operation](../../docs/mainboard-sd.md) and the
[example index](../README.md). The original instructions below explain its
retained source/evidence; do not execute them unchanged against today's bench.

## Retained fixture contract


Finite SD-loaded MOS application for `VDU 23,0,&99,vk`. The P4 host input
controller supplies held Shift and `a` events through admitted keyboard input;
the application observes ordinary EMOS sysvars, not direct UART registers.

Build with the Agon dev toolchain: put the reviewed build identity in
`build/identity.h` as `#define KEYQUERY_BUILD_ID "..."`, then `make`.
Install `bin/keyquery.bin` at `/test/keyquery.bin` using the maintained SD service.
Do not change video mode inside this fixture.

From an admitted MOS prompt, select `EMOS EXCOM`, `LOAD /test/keyquery.bin`, then
`RUN`. At the four cues hold Shift, release Shift, hold `a`, release `a`.
Do not type other keys. Each input wait is bounded to 20 nominal seconds and
each query to two; timing uses the MOS nominal 120-Hz clock, not calibrated wall
time. A host controller must maintain its input lease and release every key.

The application writes `/test/keyquery.csv` (replacing its previous receipt),
then returns to MOS. Expected success is 269 passing rows. Independently check
all `count_delta` values equal one; the 260 held-Shift queries exercise an
8-bit event-counter wrap. The run includes host coordination delays and is
functional evidence, not a performance benchmark. Retrieve the CSV through
the maintained Legacy-mode SD service and exit that service afterward.

See `docs/tasks/PORT-003/key-query/PLAN.md` and `RESULTS.md` for the frozen scope
and hardware evidence. No physical USB/browser latency claim follows from this
controlled input test.
