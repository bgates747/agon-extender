# Virtual-key query reply — frozen work contract

P4 consumes `VDU 23,0,&99,vk` today but sends no reply. Restore the stock event
reply using actual admitted keyboard state, the retained parser and serializer,
and upstream character conversion. Author authorized contract freeze, coding,
flashing and tests, followed by review; no audible/emulator notification.

## Scope and research

1. Official docs: `agon-docs/docs/vdp/System-Commands.md`, request &99;
   checkout f9806bd3cbff6ed5d1c08bef1d51fed11764b86b.
2. Official VDP v2.16.0, c7ac293d2aa81ddfa693390549bcd909069c8fc3:
   `video/vdu_sys.h` queues a virtual-key event with current down state.
   `video/agon_ps2.h` retains the previous keycode on key-up and translates
   navigation keycodes on key-down. Normal callbacks and PACKET_KEYCODE reply
   remain authoritative; no new EMOS command or reply packet is required.
3. Vendored vdp-gl `devdrivers/keyboard.cpp` uses current modifiers and
   `codepages.cpp::virtualKeyToASCII` with its default null codepage. Reuse that
   converter; do not invent a reverse HID/layout map or instantiate PS/2 hardware.
4. P4 processed input is owned by the console/parser task. Track admitted virtual
   key state through that existing FIFO; synthetic query events preserve ordering
   and use the ordinary retained callbacks/serializer. No HTTP task writes UART.
5. Restrict to valid retained virtual keys; invalid byte values must not access
   beyond the state table. Bounded queue exhaustion must be explicit failure,
   not a silent lost reply. Clear tracked state on transport reset; ordinary
   physical/browser releases and source boundaries continue through existing paths.
6. Legacy mainboard query handling is unchanged. Test ExCom through ordinary MOS
   VDU output and existing EMOS keyboard ingress. No EMOS or mainboard VDP flash,
   mouse work, maintenance implementation, new browser capture behaviour or
   browser-game latency repair. Query callbacks/control-key effects stay stock.

## Work and gates

1. Freeze this contract and the Legacy-only maintenance scope. Use
   key-query-probe-r01 and registry r92 under standing version approval.
2. Implement the smallest input-adapter/FIFO change and tests for released and
   held keys, modifiers, stock ASCII/navigation conversion, multiple queries,
   ordering, invalid keys, capacity and reset cleanup. Preserve ordinary input.
3. Build from the exact installed browser-capture-r03 composition, preserving
   codec/storage/UI work. Freeze hashes and preserve the installed rollback.
4. Prepare a finite SD-loaded fixture using MOS APIs only. Select modes outside
   the fixture, retain results on SD, and bound every wait. Host input goes
   through the admitted P4 keyboard path, not eZ80 memory injection. No test
   writes outside its directory or changes the user's games.
5. Flash identity-verified P4 and independently verify bytes/startup. Normal Agon
   reset is authorized as needed for readmission; no reset loop or flash retry.
   Run the fixture through EMOS, retrieve its durable result and verify neutral
   keyboard, normal CLI and working SD access. Restore any changed startup.
6. Report exact tested scope and limitations; leave candidate for Author review.
   No app/emulator/hardware attention sound. Do not claim broader qualification.

## Review boundaries

Upstream internal query synthesis may differ from an ordinary physical release:
its ASCII is recomputed with current modifiers while the transmitted keycode on
key-up is the retained preceding code. Preserve that distinction only for the
synthetic query; do not change existing physical/browser packet semantics here.
Arbitrary malformed stream recovery and a hung whole-board recovery are not
part of this increment. Baseline failure evidence may be supplied by deterministic
host checks; do not reflash old firmware merely to reproduce known silence.
