# P4 passive-GPIO fixture r01

This is a bench-only ESP32-P4 firmware fixture for incremental construction
checks of `light2-harness-r02`. It is not product firmware and must not be
described or deployed as an Extender release.

This is an example of the scoped electrical diagnostic permitted by
PORT-008-D003 and the
[staged process](../../../qualification/staged-circuit-validation.md). Its
power-domain observations do not test candidate transport code. A later active
stage selects the relevant candidate components and safe states through its
own reviewed procedure; this fixture is not an implicit next-stage firmware.

The application explicitly places every P4 GPIO connected by r02 into
input-only mode with both internal pulls disabled, then idles indefinitely. It
initializes no Extender transport, UART, PARLIO, Ethernet, display, or
application service. The selected pads are GPIO 9--15, 17, 20--23, 32, and 33.

This contract begins only when Arduino invokes `setup()`. It makes no claim
about ESP32-P4 reset, ROM, bootloader, or framework behavior before that point;
r02's external fail-safe circuitry owns that interval. Logic-analyzer or meter
evidence is still required for any claim that a physical pad remained passive.

Build from the repository root with:

```text
.venv/bin/pio run \
  -d docs/tasks/QUAL-002/p4-passive-r01 \
  -e p4-passive
```

The first isolated build on 2026-09-04 showed that this PlatformIO composition
ignored an absolute `board_build.sdkconfig_defaults` path and retained
ESP-IDF's incompatible 100 Hz FreeRTOS default. This fixture therefore carries
frozen local copies of the accepted P4 defaults and partition table. Do not
replace those paths with absolute repository paths. Their source versions were
copied from `vdp/sdkconfig.defaults` and `vdp/partitions.csv`; review and update
this fixture deliberately if those product inputs change.

The image flashed on 2026-09-04 had factory-image SHA-256
`6693897457b4d4afa283b15111f7576532e2f29277942132afc21c63743733a2`.
Its source SHA-256 was
`50b60db9aa6e33a19b41a357d8c01bce9b380703c6ecc566ac044e839a6e7091`.
Build timestamps mean a later semantically identical build need not reproduce
the factory image byte-for-byte.
