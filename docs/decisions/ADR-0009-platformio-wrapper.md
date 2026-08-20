# ADR-0009 — Provide a transparent PlatformIO wrapper

## Status

Accepted.

## Context

The VDP PlatformIO project lives in the repository's top-level `vdp/`
directory, while the required Python and PlatformIO environment lives in the
repository root `.venv`. Canonical Agon development practice requires explicit
use of the project-local virtual environment rather than silently selecting a
system interpreter or tool installation.

Developers and automation should also retain PlatformIO's familiar command
vocabulary. A Makefile or bespoke command dispatcher would introduce a second
interface whose names and behavior could drift from upstream PlatformIO usage.

## Decision

Provide a tracked executable wrapper at `scripts/vdp-pio.sh` with this public
interface:

```text
scripts/vdp-pio.sh [PlatformIO arguments...]
```

The wrapper:

1. resolves the repository root independently of the caller's current working
   directory;
2. requires the repository root `.venv/bin/pio` executable;
3. requires `vdp/platformio.ini`;
4. runs PlatformIO with `vdp/` as its working project directory;
5. reports the selected executable and project; and
6. forwards all caller-supplied PlatformIO arguments unchanged.

It does not activate a shell environment, install dependencies, choose a serial
port, build, clean, upload, or monitor unless the caller explicitly supplies
the corresponding PlatformIO arguments.

Direct invocation such as `(cd vdp && ../.venv/bin/pio run)` remains a
supported equivalent.

## Rationale

1. The wrapper makes canonical `.venv` selection automatic and visible.
2. Reliable repository-relative path resolution allows use from any directory.
3. Transparent argument forwarding preserves PlatformIO documentation and
   upstream habits as the authoritative command interface.
4. Avoiding implicit device actions keeps builds reproducible and hardware
   mutations intentional.

## Consequences

1. The wrapper is convenience and policy enforcement, not a separate build
   system.
2. Help, new PlatformIO options, and uncommon targets remain available without
   wrapper changes because arguments are not interpreted.
3. Missing local prerequisites produce a focused error rather than falling back
   to globally installed tools.
