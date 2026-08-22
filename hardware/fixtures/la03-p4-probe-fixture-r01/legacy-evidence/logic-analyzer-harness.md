# Preserved logic-analyzer harness facts

Bounded extract from legacy `docs/logic-analyzer.md` at commit
`df54cf6a7a23cd40e98076856f68cff0559d1c77`; complete source SHA-256
`93e0638ac01dc008a4c67b246df08eacfd41760da47a76935530aae8a0958c3b`.
Machine-local capture topology and obsolete commands are intentionally not
copied into tracked public documentation.

## Verified channel and wire-color map

| Analyzer channel | Physical probe wire |
|---|---|
| `D0` | green |
| `D1` | yellow |
| `D2` | blue |
| `D3` | orange |
| `D4` | purple |
| `D5` | red |
| `D6` | gray |
| `D7` | brown |
| qualified `GND` | black |

The probe leads are physically grouped as two ribbons: even channels
`D0,D2,D4,D6` and odd channels `D1,D3,D5,D7`. Physical lead colors, not
PulseView display colors, identify probes. Signal assignments are test-local
and every capture records analyzer channel, physical color, and target net.

The black lead is ground, never D0. Only the previously qualified physical
ground position is authoritative; one alternate position previously left all
inputs floating high. After moving or rebuilding the harness, ground-walk every
intended signal probe and require exactly the expected channel to fall low.
