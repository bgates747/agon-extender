# Console8 F310 gameport conversation — 2026-11-08

This is a chronological précis of Smith's discussion with Extender, from the
initial idea through the request to record a research-only task. It preserves
the reasoning and corrections rather than treating every conversational claim
as an established hardware contract. [INPUT-006](../INPUT-006.md) owns research
scope, sources, open questions and subsequent dispositions.

1. **The idea.** After joking about the agent being rested, Smith proposed
   connecting the Logitech controller already used by FSIM to a built-in
   Console8 gameport. Extender initially asked which controller; Smith reminded
   it that Extender had implemented the firmware. Existing project records
   identify the Logitech F310 and its working P4 USB input path.
2. **More than joystick emulation.** Smith identified the ports as advertised
   Atari-style. Extender first described a USB-host adapter mapping inputs to
   four directions and two buttons, warning that full analog state would need
   a custom protocol. Smith's “that's why i wanted to make sure you were
   well-rested” clarified that the custom full-state protocol was the point.
   Smith had warned it was the “mad idea of the day”.
3. **Existing Console8 hardware.** Smith asked whether the gameports have
   level shifters and connect to eZ80 GPIO/interrupts. Schematic inspection found
   GPIO with 3.3 V pull-ups and passive filtering/protection, not gameport level
   shifters. The keyboard/mouse circuits have separate level shifters. Zilog's
   GPIO documentation supports interrupt capability. Exact physical-board
   identity, electrical timing and useful signalling rates remain unqualified.
4. **Software on the Console8 side.** Smith observed that MOS could implement
   the Console8 side in software. Extender agreed in principle: existing GPIO
   or peripheral hardware could receive packets without motherboard changes;
   the external adapter still needs USB-host hardware to acquire F310 state.
5. **Prototype hardware.** Smith suggested an Extender board or the spare WROOM,
   wondering whether the latter had a USB hub. Extender distinguished classic
   ESP32-WROOM from S3-WROOM: classic ESP32 has no native USB host/hub; S3 has
   USB OTG host capability. Extender reuse offers an existing working F310
   decoder. No particular spare module, power circuit or smaller adapter was
   selected or physically inspected.
6. **Why not UART1?** Smith anticipated the question. Extender answered that
   the aim was an existing external socket rather than opening the console or
   occupying the expansion connector, then suggested checking whether UART1's
   alternate-function pins reach a gameport. Smith confirmed that this was
   also his reasoning.
7. **Shared header pins.** Smith asked whether the expansion header also exposes
   the gameport GPIO. Inspection confirmed all twelve shared nets. Extender
   noted that a header prototype and later gameport connection could use the
   same GPIO assignments, with the gameport's additional filter path and shared
   pin-ownership constraint. The task records the exact mapping.
8. **Split GPIO ports.** Smith objected that each controller spans two CPU
   ports. Port C holds both controllers' interleaved directions; Port D holds
   buttons. Extender explained the two-read polling arrangement. Smith noted
   that grouping a single controller's six lines would better suit his usual
   single-controller use. Extender suggested four Port C data bits plus Port D
   handshaking as a possible GPIO design, before the discussion returned to UART.
9. **Hardware UART discovery.** Smith said “we really should just use uart1”.
   The eZ80 mapping and Console8 schematic establish PC1/RxD1 on gameport A Up
   (DE-9 pin 1 / EXP1 pin 15), and PC0/TxD1 on gameport B Up (DE-9 pin 1 /
   EXP1 pin 18). A one-way adapter-to-console state stream through connector A
   could therefore use hardware UART reception. MOS would select the UART
   function; the connector remains physically Atari-style while carrying a
   custom serial state protocol. No rate/filter or installed-MOS qualification
   was performed. Smith responded “ohhhh” and “<giggle.”
10. **Two-controller question.** Smith observed that the scheme might prevent
    two-controller setups. Extender proposed a USB-host adapter multiplexing
    reports with controller IDs, then left ordinary gameport B coexistence
    unresolved. The categorical statement that two ordinary joysticks become
    impossible was too broad: the adapter occupies A, but receive-only UART1
    pin mux and preservation of B's GPIO must be researched. Neither two-USB-pad
    support nor passive-B coexistence is established.
11. **Initial stopping point.** Smith requested a task, research only, and a record of
    the conversation before leaving. No code, firmware, wiring, physical run,
    reservation or production change was requested. INPUT-006 records the work
    and the required research report before any later prototype selection.
12. **Existing prototype wiring.** On returning to the discussion, Smith asked
    whether Extender already had all wiring or lacked Port D. The maintained
    confirmed Light2/P4-PC harness has all Port C lanes and PD4/PD5/PD7;
    P4 GPIO18 TX already reaches PC1/UART1 RX. The proposed one-way UART needs
    no Port D. Extender qualification would not prove Console8 socket filters
    or cable behavior, and existing UART ownership still applies.
13. **Reuse first.** Smith observed “most of this is actually already written”.
    Extender identified reusable F310 USB decoding, normalized state, UART
    hardware/wiring, EMOS controller transport and application-library work.
    The standalone adapter path and compatible public application binding remain
    to be researched; reuse does not itself qualify a new composition.
14. **Where the driver lives.** Smith asked whether EMOS supports it or the
    driver is mostly software. Extender clarified that P4 software decodes USB,
    eZ80 UART hardware receives bytes, EMOS software handles reception/ownership
    and delivery, and the newer application library interprets controls and
    freshness. The newer extraction has software evidence but its matched
    physical deployment remains pending. Serial reception is not bit-banging.
15. **Why bidirectional?** Smith asked what P4 needs from the mainboard. The
    existing service uses polls, acknowledgements of consumed button transitions,
    caller/query correlation and close requests. These support that delivery
    design, not USB decoding itself. A one-way adapter cannot reuse the exchange
    unchanged. Periodic held state alone could lose a complete short tap.
16. **Simplify rather than rebuild an ERP.** Smith called the bidirectional
    machinery “building an ERP again”. Extender accepted the criticism and
    suggested periodic full state with cumulative button-press counters as a
    smaller one-way research starting point. Smith did not approve a specific
    packet layout; counter/reset/loss semantics remain research questions.
17. **No MOS/VDP hacks; possible resident savings.** Smith said this might free
    EMOS bytes and reaffirmed the strict no-MOS-or-VDP-hacks guideline. The
    direction is an external adapter and reusable application-linked driver
    through supported public MOS UART/interrupt facilities. Research must check
    their sufficiency and inventory removable resident controller code and
    dependencies. No firmware edit/removal, build or byte saving was authorized
    or demonstrated by this discussion.
18. **Continuing record.** Smith instructed Extender to keep recording notes in
    the task document. These additions preserve the research-only boundary and
    the distinction between existing measured extraction and prospective savings.
