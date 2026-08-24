# PORT-003 Phase E — Official mode integration

[`../../PORT-003.md`](../../PORT-003.md#phase-e--official-mode-integration) is
the authoritative checklist and scope fence. This directory owns Phase E's
bounded official-mode provenance, independent mode/lifecycle fixtures, exact
official-handler harness, host qualification, diagnostic target closure, and
gate validators. Production P4 adaptations remain under
`vdp/video/extender/display/`; the unavoidable official-facade patch remains at
its upstream path, `vdp/video/agon_screen.h`.

## Structure

```text
phase-e/
├── README.md
├── contracts.md
├── compatibility-delta.md       # reviewed result, added during implementation
├── implementation-manifest.yaml
├── evidence/                    # generated provenance, host, and build records
├── fixtures/                    # independent mode/lifecycle expectations
├── scripts/                     # deterministic extractors, models, runners
└── tests/                       # fixed harness pieces and permanent tests
```

The fixture generator models the written and documented contract and must not
import production headers, invoke production binaries, or parse production
output. The host runner may extract the exact pinned `VDU 22` and mode-packet
function bodies into a temporary harness, but no generated extraction becomes
production source.

## Frozen official inputs

1. `agon-docs/docs/vdp/VDU-Commands.md` — `VDU 22` command contract.
2. `agon-docs/docs/vdp/Screen-Modes.md` — current, legacy, and buffered mode
   table, fallback, Teletext, scaling, and swap behavior.
3. `agon-docs/docs/vdp/System-Commands.md` — mode-information packet contract.
4. `agon-docs/docs/vdp/Context-Management-API.md` — mode-change context reset.
5. `agon-docs/docs/vdp/Buffered-Commands-API.md` — callback registration and
   mode/VSYNC event vocabulary.
6. `agon-vdp@v2.16.0:video/agon_screen.h` — facade, complete mode switch,
   palette/Copper delegation, Canvas, waits, swaps, and cursor endpoint.
7. `agon-vdp@v2.16.0:video/vdu.h` — exact `VDU 22` lifecycle.
8. `agon-vdp@v2.16.0:video/vdu_sys.h` — exact mode packet construction.
9. `agon-vdp@v2.16.0:video/vdu_context.h` and `video/context.h` — context reset
   and writable frame-counter consumers.
10. `agon-vdp@v2.16.0:video/agon_ttxt.h` — retained Teletext implementation.
11. `agon-vdp@v2.16.0:video/agon_ps2.h` — cursor/mouse coupling evidence only;
    its physical driver and tasks remain excluded.

After every completed numbered checklist item, reread `TODO.md`, the Phase E
section of `PORT-003.md`, and the implementation/gate section of
`qualification-plan.md` before beginning the next item.

## Commit boundary

Phase E ends in one coherent commit containing the narrow official-facade
patch, project-owned facade/cursor adapters, host fixtures and evidence,
diagnostic target selection/closure, managed patch provenance, dependency
updates, compatibility delta, task completion, and development-log record. No
deployment, physical result, transport, EMOS parity claim, input implementation,
consumer API, output sink, or PORT-008 work belongs in that commit.
