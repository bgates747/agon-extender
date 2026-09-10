# Bounded ExCom UART console control

Draft implementation contract for PORT-008 and EMOS INTEG-010. The Author
authorized idle-CLI Legacy↔ExCom switching in PORT-008-D005. This document
defines the first paired console composition, not full EDP compatibility.

EMOS owns UART1 at 1152000/8N1 RTS/CTS. Ordinary VDU bytes and stock keyboard
and display reply packets keep their existing formats. P4 uses the retained
VDUStreamProcessor, renderer and reply serializer. USB keyboard acquisition
remains independently selected; display activation is not keyboard admission.

## Control envelope

EMOS sends `23,0,F7h` followed by a fixed 16-byte control body. P4 returns a
private `FFh,16` packet with the same body layout. F7h is an Extender-local
VDU system-command extension, unused by the selected VDP v2.16.0; this is not
an upstream opcode assignment. FFh here is a reply header, not the unrelated
forward terminal-mode command. No packet acknowledges a public MOS write.

| Body offset | Meaning |
|---|---|
| 0–1 | ASCII `EX` |
| 2 | Wire version 1 |
| 3 | Operation: prepare=1, commit=2, leave=3, abort=4; reply sets bit 7 |
| 4–7 | Nonzero EMOS transaction counter, little endian |
| 8–11 | P4 challenge, little endian; zero only in prepare request |
| 12 | Contract selector 1: bounded compatible UART console |
| 13 | Reserved/result; must be zero |
| 14–15 | CRC-16/CCITT, polynomial 1021h, initial FFFFh, no reflection or final XOR, over bytes 0–13; little endian |

P4 gives each valid prepare a fresh nonzero random challenge and a two-second
commit deadline. Prepare invalidates its preceding display lease. Commit must
match the transaction and challenge before the deadline; replayed commits,
unknown versions, bad CRCs and malformed fields receive no success response.
This prevents accidental activation and stale commits, not deliberate imitation
of EMOS. The headers in the two implementation repositories are byte-identical
and checked by the paired test.

P4's preactivation recognizer consumes only this fixed control envelope and
the accepted stock keyboard layout/General Poll exception. Ordinary VDU is
unreachable there. Once committed, the retained VDP parser recognizes F7h
at a VDU command boundary; buffer payload is never scanned for magic bytes.
Incomplete preactivation bodies expire after 250 ms. Ordinary VDU retains
the parser's own timeout behavior. P4 serial diagnostics use its USB console.

## Commit and return

1. EMOS retains Legacy while P4 prepares a fresh mode-0 console surface and
   returns the challenge. P4 uses the complete retained VDP mode lifecycle,
   including context/font initialization, before acknowledging prepare. EMOS
   ignores its early mode-information packet while Legacy is selected.
   The bounded composition supports a known paired
   contract; it does not infer complete firmware identity or feature parity
   from a General Poll response.
2. EMOS confirms commit, then initializes the destination viewport/screen and
   visible cursor and requests mode/cursor information followed by a poll.
   Its UART1 ISR stages these display replies without changing Legacy sysvars.
3. Only after matching control and ordered display responses does EMOS publish
   the compatible backend and staged stock state. Mainboard status/cursor
   commands are explicit EMOS transition output. VBlank remains on mainboard.
4. Ordinary output passes through existing RST/C dispatch. Complete return
   packets and USB events share one P4 process-task serializer. EMOS keeps
   UART0/UART1 assembly separate and applies selected-authority display effects
   using the stock handlers under an interrupt lock.
5. Leave/abort must match the display lease. EMOS publishes Legacy only after
   successful leave, then clears the mainboard screen and restores its cursor.
   Failed entry abandons the unpublished local lease; failed active leave
   reports failure and retains the route. All EMOS control waits are bounded
   by 600 mainboard clock ticks (ten seconds at 60 Hz), with a finite poll
   budget for a stopped interrupt clock.

Keyboard selection/layout survive display transitions. Closing the keyboard
source alone does not close UART1 while ExCom needs it. Normal display polls
do not repeatedly clear held-key state. A new layout followed by a poll remains
the native keyboard admission boundary; old accepted releases precede its
acknowledgement. P4 cancels blocked TX after five seconds and requires fresh
admission; idle or power/reset activity cannot authorize a display mode.

Physical reset/fault coverage, broad VDP behavior, maintenance/RTC/audio policy
and application-state preservation remain outside this bounded console proof.
