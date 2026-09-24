# Remote keyboard receiver witness

## Reuse boundary

This retained fixture is not a current deployment recipe. The source receipt and qualifier still use old support-directory evidence paths, and the helper explicitly loads the ordinary application listener. REMOTE-002 owns a path/EMOSlet handover refresh before a new run.
Use [SD layout](../../docs/sd-layout.md),
[current SD operation](../../docs/mainboard-sd.md) and the
[example index](../README.md). The original instructions below explain its
retained source/evidence; do not execute them unchanged against today's bench.

## Retained fixture contract


This finite development example records ordinary MOS keyboard sysvars and the
128-bit BBC physical-key map. It installs no callback or resident code, selects
no mode, and returns after Enter release or a 90-second timeout. Its receipt is
`/extender/key-seen.txt`; preserve each tested executable's SHA-256 with results.

Build with `make -C examples/remote-keyboard` using the AgonDev toolchain; set
`AGONDEV_TOOLCHAIN` if the environment does not provide `agondev-config`.

For the automated test, use an isolated card/profile containing this program,
the accepted EMOS/sdserve pair and `/extender/key-source.txt`. Autoexec selects
mode 3 and the Extender input source, runs this receiver, then runs exactly one
final sdserve invocation. The host helper is:

```sh
.venv/bin/python scripts/qualify_keyboard.py --url http://EXTENDER --output agents/new-keyboard-check
```

Use `--after-boot OLD_EPOCH` following a mainboard reset. The helper sends a
bounded sequence, verifies the eZ80 receipt, exits the final service, types and
edits a COPY command to a new destination, then types EXEC for a verified helper
that loads/runs sdserve and checks a fresh SD write/read. It leaves that final
service running inside the new helper batch; the original startup is closed. Its
preconditions matter: Escape or EXIT may continue a still-open parent batch.

Each event receipt is ASCII, modifiers, FabGL virtual key, down flag, number of
set MOS physical-key bits. Virtual-key numbers cannot index the MOS map directly.
The helper and byte-peer emulator are machine checks; physical USB takeover and
the attended live demonstration have their own review gate in REMOTE-002.
