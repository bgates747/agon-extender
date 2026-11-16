# NET-009 — Pi header UART to P4 Ethernet

Hold the Pi5 UART, modem, modem power, Wi-Fi association and deterministic
N8BW stream fixed. Move the TCP endpoint from Pi5 to the P4-PC's wired
Ethernet interface. In upload, Pi5 transmits and P4 validates. In download,
P4 transmits and Pi5 validates. Each arm has one bulk producer.

1. Build the isolated P4 peer against the retained ESP-IDF toolchain. It
   uses the P4-PC Ethernet wiring and USB Serial/JTAG control. Boot starts
   Ethernet DHCP and the control console. Only an explicit USB ARM command
   starts a finite one-connection listener. Match the stream nonce, baud,
   duration and frame size before transmitting.
2. Verify interoperability with the existing host protocol, including
   fragmented socket reads, short writes, premature EOF, bad CRC, wrong
   sequence and pattern, wrong HELLO, and bounded terminal status. Freeze
   source, build manifest, install/return recipes and operating argv.
3. Use the normal Olimex lease and joined handoff. Independently verify the
   application-only P4 install. Preserve the mainboard and SD. Restore the
   retained working P4 product and verify current operability during handback.
4. Run three-second arms independently at 115200, 230400, 384000, 576000
   and 1152000 baud, stopping each direction at its first data fault.
   Qualify the highest passing rate in that direction with 10, 30 and 60
   second windows. Require matching nonzero frame counts, valid sequence,
   CRC, deterministic payload and EOS. Require verified modem command
   mode before starting another arm. A fixture, network, or cleanup
   failure stops the series for reconciliation.
5. Use bounded waveform capture on the Pi/modem UART pair only if the
   probes have an independently confirmed connection to those wires.
   Retain endpoint bytes around any first fault and state the limits of
   attribution when the Pi UART waveform is unavailable.
6. Retain the sender and receiver results and the first bad frame where
   available. Close both USB and Pi header ttys before product installation.
   Report the highest qualified rate separately for each direction.

## First hardware start

The first fixture image reached its USB control console, then the Ethernet
event task hit a stack protection fault in newlib `_vfprintf_r` before
DHCP produced an address. No transfer started. Increase the fixture-only
`sys_evt` stack from 2304 to 8192 bytes, retain the first boot capture, and
verify the new image can reach DHCP before arming any transfer.

The stack-fixed fixture reached DHCP. Opening its USB Serial/JTAG tty
again for the first arm reset the P4. The host received a fresh boot and
an addressless status, before it sent ARM or any TCP data. The owner now
keeps the P4 control handle open from the identified DHCP boot through
all finite arms, then closes it before reprogramming the P4.
