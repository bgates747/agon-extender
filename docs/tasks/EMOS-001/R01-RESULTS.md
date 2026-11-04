# Eirene-based EMOS: first isolated offline result

## Executive summary

The isolated Eirene-based EMOS candidate compiles and links with the existing
controller/parallel-upload composition, and all four mandatory product linked
checks pass. The candidate includes Eirene's explicit asynchronous UART0/OTIRX
sender while keeping EMOS routing and synchronous legacy output. Nothing was
installed, merged or selected as production. Runtime behavior remains untested.

## Resource comparison

Largest ROM use first; baseline is the existing identified EMOS parallel trial.
Static RAM includes initialized data, BSS and the RAM interrupt jump table;
comparing BSS alone would overstate the increase.

| Measure | Existing EMOS trial | Eirene EMOS candidate | Candidate minus baseline |
|---|---:|---:|---:|
| ROM image, bytes | 128918 | 128098 | -820 (-0.636%) |
| ROM free, bytes | 2154 | 2974 | +820 |
| Total static RAM, bytes | 4174 | 4284 | +110 (+2.64%) |
| Remaining RAM for heap and stack, bytes | 12210 | 12100 | -110 |

Eirene's pristine source-built control is100965B ROM/2889B static RAM. It is a
foundation control, not feature-equivalent to EMOS. The published RC2 image is
reported100950B; its15B difference remains a reproducibility investigation, not
a claim of identical release bytes. The existing EMOS build uses its prior
restricted runtime and identified strings; this is a complete-composition
comparison, not a causal attribution of820B to the async sender. Heap/stack
remaining is a region size, not measured stack high-water or safe app capacity.

## Passed checks and adaptations

1. UART0/UART1 linked baud arithmetic programs the intended divisor.
2. Parallel sole gateway/leaf, admission, pad ownership, instruction shapes
   and ROM bound pass. The earlier native RST-name and high-address JR
   disassembly assumptions were corrected in the task-local validator. The
   latter now decodes opcode/displacement and proves both exact targets; no
   firmware relocation or weakened assertion is used.
3. Keyboard IRQ, BYTE returns, callback, keymap bound and public UART guards pass.
4. Compatible console dispatch/register handling and stock reply bridges pass.

These are compiler/linked-image checks. They do not execute an application,
measure eZ80 speed, qualify CTS reserve, prove arbitrary legacy compatibility
or test mode transitions on the new kernel.

## Monitored Pi compilation

All attempts use one serial compiler child, nice10, no CPU quota and1s raw
CPU/temperature/frequency/memory/throttle samples. Each stops at its first
unexpected result, releases using fresh native evidence, and reports to Pi5
manager before offline analysis. The separate follow-ups each receive a new
token. No governor, boost, kernel thermal, firmware or hardware change occurs.

| Attempt | Guarded wall, s | Peak host CPU, % across4cores | Peak job CPU, % of onecore | Peak temperature, C | Result |
|---|---:|---:|---:|---:|---|
| First build | 5.084 | 37.50 | 98.39 | 52.35 | Both images link; old RST-name check stops |
| Native-name follow-up | 4.048 | 45.00 | 103.77 | 53.45 | Branch-display assumption stops |
| Raw-target follow-up | 6.043 | 35.61 | 102.76 | 56.20 | All four mandatory checks pass |

Final candidate/check step4.623s; final control no-op0.016s. The cold first
control/candidate steps take1.768s/2.769s respectively. Overall guarded wall
includes driver, hashing and sampling; this table is not a clean-build speed
comparison. The sampled process-group CPU estimate can exceed100% because of
quantization and short overlapping process-accounting intervals; it is not
proof of another compiler running. Every run reports no throttling, at least
6.02GiB available, and no surviving owned process. Peaks are1s observations,
not continuous maxima or calibrated sensor accuracy claims.

## Preserved candidate and next review

Application image128098B SHA256
`749ff6a8e0696d10e9efad62314d98a232c248e448911f00e81184ca5a6b7f30`.
Tested code/build-input manifest SHA256
`d16f07deb7095a38c4aa1b23e823cb65c19bfaa5dd4039714c42c07245c00133`.
The dedicated agon-emos branch is `codex/emos001-eirene-r01`, based on Eirene
825eaf7 and imported EMOS6ececd56. Ignored task evidence retains exact input
hashes, source worktree, binary/ELF/maps, logs, telemetry, grants and handbacks.

The next tranche is a reviewed native/source compatibility audit and bounded
functional qualification plan. Preserve the installed pair and existing
physical benchmark reservation. Any emulator/bench run, fixture migration or
installation needs its own scope, resource admission and applicable human gate.
UART1 async reuse, runtime RST hooks and production promotion remain separate.
