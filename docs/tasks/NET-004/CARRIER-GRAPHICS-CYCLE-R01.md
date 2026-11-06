# Independent carrier and ordinary graphics cycle

Prepare an Extender-owned control that alternates parallel network requests
with ordinary mainboard drawing. It removes the game, module and asset loader
from the investigation. This is separate from MechAgon's single final case.

N04-018.03.1 Keep the existing four-record echo appliance and its accepted
  UART donor unchanged by default. Add an explicit compile-selected graphics
  variant:0/1/127/128-byte echo, ordinary counted VDU line drawing after each
  reply, then one ordered mode query before the next network request. [x]

N04-018.03.2 Use public MOS counted output and public ext.netp only. No raw
  Port C/UART register, callback, sprite, module, firmware or route change.
  The application owns static buffers; EMOS owns transport and Legacy route;
  mainboard VDP executes graphics. A query completion is ordering evidence,
  not optical proof, calibrated latency or guarded RFC25 qualification. [x]

N04-018.03.3 Retain entry-mode query/conditional mode20/whole-second settling,
  Escape in foreground waits, one pending query, first refusal/timeout stop,
  positive RELEASE and entry mode/cursor restoration. A refused RELEASE keeps
  owned storage for normal admitted recovery. Record four phase tick intervals,
  nominal MOS120Hz and independent fuse limits; write the result after close. [x]

N04-018.03.4 Compile/check both unchanged default and new explicit variant in a
  fresh normal compiler tranche. Preserve old fixture binaries/receipts. Prepare
  exact components, host echo inputs and fresh result paths before requesting
  a later bounded independent bench slot during consumer coding time. No
  automatic repeated invocation, test retry or extra MechAgon application case. [ ]

## Bounded research

Official documentation baseline remains agon-docs f9806bd3, official MOSv3.0.2
and official VDPv2.16.0, all read-only. `docs/vdp/PLOT-Commands.md` defines
PLOT4/5 absolute move/foreground line; `docs/vdp/VDU-Commands.md` defines the
six-byte PLOT packet and mode query. The existing fixture ModeSession and
counted-output bindings already implement the selected mode/query behavior.
No source behavior is inferred from an unaccepted upstream HEAD.

## Actual offline checkpoint

Compiler240 completes in4.217s, all children joined and released with no queued
successor. The actual graphics leaf passes ASan/UBSan packet/position/order,
single-write/refusal, Escape, timeout and mode-mismatch checks. Default UART
and parallel eZ80 builds pass; the selected new parallel graphics variant is
17336B, SHA256
`39f3893fe0aec41b14f59dd885215a19f149ff4b1994c55292fb647b554168e3`,
build `network-cycle-parallel-cycle-r01-b2026-11-06-09-20-47Z`. Exact input
source/build manifests are owner-retained. No new fixture is staged or invoked;
its separate physical plan and current-component binding remain pending. It
never replaces or precedes MechAgon's one final application case.
