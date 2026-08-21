# SETUP-003 Work 4 tool audit

Audit date: 2026-08-20

Available without installation:

- PlatformIO Core 6.1.19;
- RISC-V ESP target GCC/G++ 14.2.0+20260121;
- Clang 18.1.3; and
- jq.

`clang-scan-deps` was not installed. It was not required because PlatformIO's
compiler database and the target compiler's `-M -MG` and `-H -E` modes provide
the narrower target-accurate evidence required by Work 4.

Universal Ctags was not installed. It is relevant to Work 5, not Work 4, and
no package was added during this work.

The complete compiler database contained 2,006 entries. The normalized output
retains the 40 translation units belonging to the VDP sketch, vdp-gl,
ESP32Time, and CRC. The compiler produced a complete transitive dependency
closure for the sketch when allowed to treat the absent ESP32-only header as a
generated dependency. Its direct include-tree pass correctly stopped at
`vdp-gl/src/fabutils.h` requesting absent `soc/frc_timer_reg.h`.
