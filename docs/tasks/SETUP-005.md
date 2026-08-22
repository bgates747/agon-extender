# SETUP-005 — Resolve EDU operating modes and system integration

## State

- Status: In progress — decision set established; review not started
- Started: 2026-08-21 00:49 EDT
- Finished: --

## Intent

Resolve the remaining architectural decisions governing EDU operating modes,
transparent legacy compatibility, MOS integration, response ownership, and
optional use of the onboard VDP as a service behind Extender. This task is the
authoritative open-decision tracker for
[ADR-0014](../decisions/ADR-0014-edu-operating-modes-and-service-architecture.md).

Do not let these system-integration decisions block SETUP-004's source and
driver disposition survey. SETUP-004 determines what code and behavior must be
retained, replaced, stubbed, omitted, or deferred; this task determines how the
retained behavior is routed between processors and MOS.

## Open decisions

- [ ] **SETUP-005-D001 — Exclusive EDP routing:** select a transparent method
  for routing untouched legacy `RST.LIL 10h` and `RST.LIL 18h` traffic to the
  EDP in exclusive compatibility mode.
- [ ] **SETUP-005-D002 — Mode lifecycle:** define selection, discovery,
  transition, reset, failure, and recovery behavior for legacy,
  EDP-exclusive compatibility, and extended cooperative modes. Legacy mode
  must make Extender electrically and logically absent from the Agon interface.
- [ ] **SETUP-005-D003 — Compatible response delivery:** determine how EDP
  responses and onboard-VDP input packets populate canonical MOS sysvars in
  exclusive mode, and define the separate EDU result domain used in extended
  cooperative mode. The adopted P4 return path terminates on eZ80 UART1, while
  stock MOS feeds only the onboard VDP's UART0 stream through its VDP packet
  parser. Extender, applications, and a resident service must not write
  MOS-owned sysvars directly; compatible updates require an explicitly
  selected MOS-owned parser route.
- [ ] **SETUP-005-D004 — Legacy abstraction boundary:** define which classes of
  non-EDU-aware software can be supported through wrappers or loaders in
  extended cooperative mode and the qualification required for each class.
- [ ] **SETUP-005-D005 — Audio output routing:** decide whether any mode forwards
  EDP audio commands to the onboard VDP for local hardware playback. Retaining
  the complete audio command surface does not require this route; the currently
  scoped Rev 1 output is network/browser audio.
- [ ] **SETUP-005-D006 — Unsupported maintenance-command behavior:** define the
  closest practical stock-VDP-compatible command consumption, parser recovery,
  and externally observable failure behavior used in EDP-exclusive mode for
  printer/USB serial, console/terminal, ZDI, Intel HEX, YMODEM, updater, and
  local-debug commands. Determine the stock behavior for each command and
  classify behavior by operating mode. Strict compatibility modes must permit
  stock-observable Bad Things—including corrupted output, resets, crashes, or
  Guru Meditations—where suppressing them would violate compatibility. Modes
  without that strict promise should improve the behavior with deterministic
  no-op, rejection, status, timeout, parser recovery, and diagnostics. Define
  explicitly which modes are strict before assigning command behavior.
- [ ] **SETUP-005-D007 — Peripheral-input ownership and routing:** retain the
  onboard VDP as the initial physical keyboard and mouse owner and preserve its
  stock packets to MOS as the canonical legacy input path. The proof of concept
  uses an EDU-aware eZ80 application to read stock input and explicitly forward
  processed events to Extender. Injected events update EDP-local behavior and do
  not automatically echo stock input packets back to the forwarding eZ80
  application. This does not support untouched applications or constitute
  transparent exclusive routing. Determine whether and how v1 adds
  a more automatic route by which an EDP-exclusive session receives events for
  display-local behavior—including paged mode, control-key handling, mouse
  cursor state, VDP variables, and callbacks—without creating competing MOS
  sysvar writers. Compare an Extender-enabled MOS relay, an onboard-VDP bridge,
  aware-application forwarding, and other routing mechanisms. V1 will not add
  P4-owned keyboard, mouse, or other peripheral hardware beyond facilities
  already present on the selected P4 DevKit; any such expansion is post-v1.
- [ ] **SETUP-005-D008 — RTC authority and synchronization:** define the
  authoritative clock and read/set routing in legacy, EDP-exclusive, and
  extended cooperative modes. Specify how MOS RTC sysvars, the onboard VDP,
  the EDP system clock, and optional network time interact; prevent competing
  writers; define reset persistence, timezone expectations, conflict and
  failure behavior, and any capability/status reporting. Do not allow network
  synchronization to silently override an application-set clock unless the
  selected policy explicitly permits it.

When all eight decisions are accepted and incorporated into ADR-0014, change its
completeness to `Complete` and remove the resolved items from this task after
recording their disposition in the development log.

## Current routing analysis

No implementation direction in this section is accepted yet.

The required EDP-exclusive behavior is:

```text
all application audio/video output -> EDP
onboard VDP keyboard/mouse input    -> Extender compatibility path
Extender compatibility path         -> one coherent MOS response/sysvar domain
```

A normal resident program cannot transparently intercept untouched applications
through the documented MOS interrupt-vector API because the VDU restart handlers
are fixed in low ROM. The credible implementation families presently include:

1. **Hardware interposition:** place switching or gateway hardware between the
   eZ80, onboard VDP, and EDP. This offers strong transport ownership but is
   disfavored because requiring users to modify an Agon with a soldering iron is
   incompatible with the intended product experience.
2. **Narrow MOS transport support:** leave `RST.LIL 10h` and `RST.LIL 18h`
   unchanged while adding a selectable output backend to the MOS routines they
   already invoke. Stock mode targets the onboard UART; EDP-exclusive mode
   targets the Extender forward transport.
3. **Runtime ROM shadowing or patching:** redirect the low-memory handlers using
   eZ80 mapping facilities if such a safe mechanism exists. Feasibility has not
   been established.
4. **Application loaders or binary rewriting:** adapt selected programs. This
   may support useful compatibility profiles but cannot establish a guarantee
   for arbitrary untouched binaries.

The narrow MOS candidate would keep the onboard VDP's input packets arriving on
UART0 and reuse MOS's normal parser to update canonical sysvars. MOS could mirror
those parsed events to the EDU service so the EDP sees the same input. When the
EDP parser recognizes a keyboard or mouse configuration command in the diverted
VDU stream, it could ask the MOS backend to forward the corresponding bytes to
the onboard VDP; this avoids adding a second complete VDU parser to MOS.

This candidate keeps sysvar memory under MOS ownership, avoids competing packet
writers, and requires no user hardware modification. It would, however, make an
Extender-enabled MOS release a prerequisite for full EDP-exclusive compatibility
and requires a defined stock-mode fallback. These tradeoffs remain undecided.

## Review gate

Present the open decisions individually with recommendations, alternatives,
tradeoffs, prerequisites, and downstream effects. Do not implement MOS changes,
resident-service behavior, transport routing, mode transitions, or onboard-VDP
delegation until the corresponding decision is accepted and promoted into
ADR-0014.
