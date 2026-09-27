# Emulator setup for Extender development

## Executive summary

Use the shared Agon setup tool for an isolated Linux stock-MOS application
profile. An emulator does not run the P4 console firmware or establish UART,
Ethernet, PSRAM, DSI or hardware timing behavior. EMOS and native VDP reviews
need their own identified inputs and review procedure. The commands below were
checked against maintained source; no fresh-host installation or graphical
run was performed for this documentation review.

## Prerequisites and ownership

Use the standard sibling checkout layout: `agon-extender`, `agon-dev-env`,
`agon-emos` and `mos-agondev` under the workspace's `mystuff` directory, with
an official Fab runtime elsewhere. Read the shared
[emulator guide](../../agon-dev-env/codex/emulator.md) and
[bespoke VDP guide](../../agon-dev-env/codex/bespoke-vdp-emulator.md).
These sibling files are required workspace resources, not files included in an
Extender-only clone. Obtain the maintained agon-dev-env checkout from the
workspace owner if absent; do not invent a replacement launcher.

The runtime must include a host-compatible executable, stock native VDP modules,
firmware images/maps and standard SD utilities. An existing compatible Linux
binary can be reused; a custom VDP does not require rebuilding the executable.
The shared setup tool checks pinned MOS image and map hashes (currently stock
MOS 3.0.2 Arthur). A mismatch requires deliberate release-pin reconciliation,
not disabling verification. Native modules and SDL libraries must match the
host architecture and loader ABI.

Keep profiles ignored under `.emulator/`. Never map the containing project tree
into its own nested SD tree. A directory-backed SD is writable host storage;
only map files/directories the fixture is allowed to change. It is not equivalent
to physical FatFS media. Use [SD layout](sd-layout.md) for guest file placement.

## Stock application profile on Linux

Run from the Extender repository root, with its Python environment available.
Before setup, inspect `.emulator/` for existing work and preserve it. The shared
`extender` preset owns that directory and replaces its SD `/extender` payload
from `tgt/`; it is not a generic blank profile creator.

1. Prepare the selected application payload in `tgt/`: nonempty `.bin` files
   and, optionally, an `assets/` directory. The tool rejects symlinks and other
   top-level entries. A new startup requires `tgt/hello.bin`; use this preset
   only for that demo layout, not an unrelated test fixture.
2. Set `FAB_ROOT` to the existing complete official Fab runtime directory, then
   inspect the available options and generate the profile:

   ```sh
   .venv/bin/python ../agon-dev-env/scripts/setup_emulator.py --help
   .venv/bin/python ../agon-dev-env/scripts/setup_emulator.py extender \
     --extender "$PWD" --extender-emulator "$FAB_ROOT"
   ```

   The explicit `--extender-emulator` avoids the tool's historical default
   runtime in another project's directory. `--emulator` alone does not override
   the Extender preset's runtime.
3. Inspect `.emulator/sdcard/autoexec.txt`. New startup selects keyboard layout
   1, mode 3, then loads/runs `/extender/hello.bin`; an existing regular startup
   file is preserved. Keep CRLF endings and mode selection in autoexec, outside
   the fixture program. Change startup deliberately before launching if the
   test should pause at MOS or only load a fixture.
4. Verify the generated topology before running:

   ```sh
   test -f .emulator/fab-agon-emulator
   test ! -L .emulator/fab-agon-emulator
   test -x .emulator/fab-agon-emulator
   test -L .emulator/fab-agon-emulator.bin
   (cd .emulator && sha256sum --check .mos-release.sha256)
   ```

   These checks cover topology and MOS hashes, not complete runtime validity.
   Inspect the wrapper and resolved input paths as well. The executable wrapper
   must select the profile SD/MOS and delegate to the raw `.bin` executable.
5. From a graphical session, launch the profile-local wrapper:

   ```sh
   cd .emulator
   ./fab-agon-emulator
   ```

   The reviewed Linux generator defaults `SDL_VIDEODRIVER` to Wayland. On an
   X11 desktop, use `SDL_VIDEODRIVER=x11 ./fab-agon-emulator`. Do not force a
   Wayland environment on another host. The wrapper adds the user's local SDL3
   library directory when present. An SSH shell also needs access to the real
   graphical session; merely setting DISPLAY does not supply authorization.

A missing library or wrong module is a setup failure, not a fixture result.
Confirm the intended firmware identity, startup and visible output in a human
review before treating a new or changed profile as accepted. This guide does
not qualify macOS portability of the Linux wrapper (`readlink -f`, `sha256sum`
and `.so` module conventions require host-specific consideration).

## EMOS and custom VDP reviews

Stock profiles boot stock MOS: they do not provide EMOS commands. Follow
[Building](building.md) for the owning EMOS build tools. The EMOS
`prepare_boot_review.py` takes `--fab-root`, builds an identified bundle,
creates separate stock/EMOS SD trees and runs `verify_runtime.py`. It is an
active build/check workflow, not a read-only setup inspector or a general
interactive launcher. Its review output is not a physical deployment.

Use the owning fixture's reviewed profile generator for EMOS or a bespoke
native VDP. Record exact firmware, map, module, runtime and payload identities.
Do not overwrite the shared stock runtime or bypass its MOS hash checks to
inject EMOS. A native VDP module is a host library, not a flashable ESP32 image.
A bespoke launcher must fail closed if the selected module is missing, rather
than silently loading stock VDP. The shared bespoke guide owns that procedure.

Emulated UART peers prove only the behavior they implement. They do not prove
P4 rendering performance, electrical flow control, physical SD durability or
network responsiveness. Preserve those qualification boundaries in results.
