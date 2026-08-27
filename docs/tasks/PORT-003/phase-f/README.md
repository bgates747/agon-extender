# PORT-003 Phase F — Browser handoff and bootable port

[`../../PORT-003.md`](../../PORT-003.md#phase-f--browser-video-handoff-and-bootable-port)
is the authoritative checklist and scope fence. This directory owns Phase F's
bounded source evidence, immutable snapshot and browser-video contracts,
independent fixtures, host/target qualification, and gate validators.

The initial implementation has one primary product sink: the browser interface
served directly by EDP/P4 over the Olimex DevKit's onboard Ethernet. PORT-006
owns Ethernet and generic HTTP/connection mechanics; PORT-003 owns pixels,
snapshots, video framing, and browser presentation.

## Planned structure

```text
phase-f/
├── README.md
├── contracts.md
├── legacy-browser-assessment.md
├── compatibility-delta.md       # added with implementation
├── implementation-manifest.yaml # added with implementation
├── evidence/                    # generated provenance, host, build, target
├── fixtures/                    # independent frame and state expectations
├── scripts/                     # deterministic extractors and runners
└── tests/                       # fixed harness and browser test pieces
```

The Author accepted this planning package on 2026-08-27. It authorizes the
tracked implementation and nonphysical validation checklist, but deployment,
EMOS modification, Agon connection, and bench operation remain separately
gated. After every completed checklist item, reread `TODO.md`, the authoritative
Phase F checklist, and `contracts.md` before continuing.
