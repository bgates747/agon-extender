# Serial printer, console and terminal — deferred research and likely implementation

## Author direction — 2026-09-20

Retain `VDU 1`, `VDU 2` and `VDU 3` as potential useful debugging/output
facilities. Likely implement working EDP output after further research; do not
replace these commands with intentional discard-only stubs. Research,
implementation and qualification are deferred until the Author chooses to
resume. This is not a frozen P4 endpoint design or a release commitment.
Existing code and hardware remain unchanged, and working output is not claimed.

## Shared console/terminal scope — Author direction, 2026-09-20

Group `VDU 23,0,&FE,n` (console mode, C-CONSOLE) and `VDU 23,0,&FF`
(terminal mode, C-TERM) with printer output in this same deferred bucket.
They concern the stock VDP serial programming/data connection and share the
endpoint, host access, debug-log, flashing and recovery considerations below.
Revisit when useful to the Author or closer to production. Do not implement,
remove or qualify them now; this does not select a P4 endpoint or a v1 deadline.

Before implementation, review exact stock bidirectional behavior, entry/exit
semantics and input ownership as well as output. Preserve EMOS route authority
and avoid contention with the existing physical/browser keyboard sources.
The current P4 console-mode selector is consumed but console mode remains off;
terminal entry has no operands and remains disabled. No guarantee is made that
subsequent terminal bytes are safe ordinary VDU commands. Existing behavior is
unchanged pending the shared review.

## Verified stock printer semantics

Official `agon-docs/docs/vdp/VDU-Commands.md` at
f9806bd3cbff6ed5d1c08bef1d51fed11764b86b documents:

| Command | Behavior |
| --- | --- |
| `VDU 1,n` | Send the next byte to the enabled printer output only; discard it when disabled |
| `VDU 2` | Enable copying text and control characters 8–13 to printer output, alongside screen output |
| `VDU 3` | Disable printer output; ordinary screen output continues |

Other graphics/VDU command argument bytes are not copied. The stock “printer”
is a serial terminal on a host computer attached to mainboard VDP's USB serial
programming/data connection, not the USB-shaped PS/2 keyboard connector and
not a general USB printer driver.

Official VDP v2.16.0, c7ac293d2aa81ddfa693390549bcd909069c8fc3:
`video/vdu.h` owns consumption and writes to `DBGSerial`; `video/video.ino`
constructs `HardwareSerial DBGSerial(0)` and initializes that UART. P4's retained
parser consumes these commands, but its build skips the stock DBGSerial setup.
That alone does not establish a functional or qualified P4 output endpoint.

## Questions for resumption

1. Determine which P4 serial programming/data interface should carry output,
   on both the current DevKit and intended P4-PC; distinguish UART from native
   USB serial interfaces and verify their actual host-visible endpoints.
2. Check sharing with debug logs, flashing, recovery and existing services.
3. Preserve stock enable/disable and byte-filtering behavior, using the retained
   parser and a board-appropriate output binding. EMOS remains VDU route owner.
4. Test exact captured bytes, absence of graphics-argument leakage, and behavior
   with no host or a slow/disconnected host. Do not introduce renderer/input
   stalls merely to retain a diagnostic facility.

Scope owner: PORT-003, inventory C-PRINT, C-CONSOLE and C-TERM. No action is authorized by this record.
