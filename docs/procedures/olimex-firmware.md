# Firmware references

The commissioned Olimex P4-PC bench uses **Extender v0.3.0**. The
[production selection](../../production/current.yaml) pins the bundle.
Use **Production restore images** in the
[current operator procedure](../operations/olimex-bench/README.md)
for exact write files, target offsets and checksums.
The [firmware-owner procedure](../../production/olimex-bench-firmware.md)
covers maintaining the production images.

Alexe and Console8 use the
[VDPlet v0.1.2-alpha release](https://github.com/bgates747/agon-vdplet/releases/tag/v0.1.2-alpha)
and Eirene MOS from [3.1.0_uart0_rc_3](https://github.com/bgates747/eirene-mos/releases/tag/3.1.0_uart0_rc_3).
Verify VDPlet against the release's SHA256SUMS. Use the release ZIP member
`mos-rc3.bin`, 100,879 bytes, SHA-256
`d7a51147f3381cd68d56f3fbe4605434a897dfae1b049269afeba09ec2b7eb50`.
