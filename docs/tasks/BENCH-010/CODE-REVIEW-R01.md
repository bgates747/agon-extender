# Installed Pingo2 / EMOS / EDP input review — 2026-10-12

The Author now confirms an isolated reproducible trigger: opening the mainboard
serial monitor immediately resets the Agon, keyboard input does not recover,
and a second reset restores it. Fsim's retained before/after HTTP snapshots still
report ready=true, so that flag alone is not functional qualification. The
installed pyserial open sequence and Olimex shared eZ80/ESP32 reset circuit expose
a plausible control-line mechanism; the actual transient is unmeasured. Earlier
mid-command failures separately show an EDP keyboard-layout boundary. No hardware
was accessed by Extender during this source/evidence review.

## R01-01 — Exact installed combination and source authority

| Component | Selected installed identity | Verification used |
| --- | --- | --- |
| Mainboard Pingo2 | P2 count/resource app, SHA256 `3cbc3efc01e2fad673c9433868627f3a14b2cdaeb9f8a1ca429327b2e357a2a6` | Fsim's final artifact, build script and independent flash receipt |
| EDP | `rgb-001-r10-b2026-10-07-22-56-28Z`, app SHA256 `a6607a8c51d8dfff5f1724bae5023fef678fde12ec45c8a4394b3c2e70e589ab` | Retained source archive; reviewed input/transport/web files match its source-input manifest |
| EMOS | `agon-emos-v0.1.24-b2026-10-07-23-11-33Z`, image SHA256 `44d217b555f68a7d030bc0a89a2fa1d27f0fb537576f2925e90ef055b0a44d02` | Base `9b67182cca4cb51f9fee0473ab32dda1e766e3db` plus retained exact Pingo callback source overlay; installed full-ROM receipt retained |

Use the immutable fsim messages ending `fsim-pingo052-web-sequence` and
`fsim-pingo052-firmware-hashes` for the chronology. Fsim's owner evidence is
`tests/0069-pingo052-physical` in the sibling project; this review does not modify
that project. Retained local review inputs/replay are under ignored
`agents/bench010/source-review-r01`.

Fsim's initial source-pins file predates its final physical instrumentation:
platformio.ini, pingo2_commands.c and pingo2_control.h differ. Its build.py and
resource_finish.py account for those additions, including f052_log.cpp. Do not
claim that every final file matches the initial pin list. The UART, PS/2 and
startup-handshake files examined here match the retained pins. Official VDP
v2.16.0 was consulted read-only as a source comparator, not used as a substitute
for the installed P2. No stock hardware reproduction was run in this tranche.

## R01-02 — Findings

| ID | Finding | Evidence and practical meaning |
| --- | --- | --- |
| F01 | `reason=4` specifically identifies a layout/admission boundary. | Retained EDP remote_keyboard.hpp defines admission=4; console_hardware.inc calls the default boundary only from consoleLayout(). That function is reached through VDU `23,0,&81,region`. Other transport failures use reason6. |
| F02 | The reported `boot` change does not prove P4 restarted. | RemoteKeyboard::boundary increments this input epoch while preserving session/counters and marking queued events discarded. begin(), used on P4 startup, clears those fields. Fsim's preserved nonzero session and 2/52 counters fit boundary(), not a fresh begin(). |
| F03 | Host replay reproduces the exact session failure. | Feed the actual 52-transition command, emit Shift-down then E-down, apply boundary, drain releases, admit locale1: epoch+1, ready=true, reason4, emitted2, discarded50, held0/pending0. The two mapped keys are VK117/modifiers2 and VK52/modifiers2/ASCII69; neither requests MOS Ctrl+Alt+Delete. This is an input-state replay, not a UART/hardware root-cause reproduction. |
| F04 | Browser capture is also invalidated by that boundary. | InputOwner::boundary cancels BrowserCapture and the automation session. A browser heartbeat for the former capture then returns409 in the replay. The browser uses a WebSocket generation and individual transitions; scripts/keyboard.py uses HTTP epoch/session and paced batches. Both share the same processed-key serializer/UART owner. Later successful browser typing does not prove its previous capture survived the boundary. |
| F05 | The mainboard USB programmer can reset both Agon processors. | Olimex Rev B schematic sheets1/2 connect eZ80 RESET and ESP32 EN to RST/EN; sheet4 connects CH340 DTR/RTS through Q4 to that same net. Fsim's final verify_flash explicitly uses hard_reset. Correct the earlier description that only VDP was reset. The Pi Reset Agon actuator uses the same net. |
| F06 | The Author confirms serial opening immediately triggers reset; input recovers only after a second reset. | Fsim isolated collector opening after a successful web DIR, with no agent reset, flash, input or transfer. Its capture contains the startup warning. The Author confirms the reset and failed keyboard recovery, then recovery after a second reset. Actual DTR/RTS transient is unmeasured. The earlier collector-free post-flash failure remains a separate boundary. |
| F08 | ready=true does not establish working mainboard input after this reset. | Retained before.json and after.json from the isolated collector check are identical for keyboard/SD, including ready=true and unchanged input epoch, while the Author reports nonfunctional keyboard. These samples do not identify why admission failed or whether later status changed. |
| F07 | No direct Pingo2 keyboard-protocol conflict was found in the reviewed paths. | Installed P2 vdp_protocol.h, agon_ps2.h, vdu_sys.h and agon.h match official v2.16.0 after line-ending normalization. Its processNext/key handler is unchanged; the additional declaration is for Pingo buffer use. Pingo ten-byte completion is sent only after a Pingo command produces a notice; the failed service command precedes benchmark invocation. EMOS's exact P3DR callback guard admits ten bytes only on mainboard display and ordinary four-byte keys retain source filtering. This does not rule out a timing or electrical interaction. |

## R01-02a — Serial collector addendum

Immutable fsim messages `2026-10-12_04-42-13_fsim_fsim-pingo052-no-serial-success`
and `2026-10-12_04-42-32_fsim_fsim-pingo052-exact-wdt-diagnostic` add the
capture-first versus command-only evidence. The successful attempt establishes
keyboard command delivery, not independent benchmark completion. Original retry
logs remain in the sibling project's `tests/0069-pingo052-physical` evidence.

Subsequent immutable messages ending `fsim-pingo052-serial-reset-confirmation`,
`fsim-pingo052-keyboard-no-recovery` and `fsim-pingo052-second-reset-recovery`
report the isolated reproduction. The Author directly confirms the same sequence
in this conversation: serial monitor open → immediate reset → keyboard unavailable
→ second reset → keyboard restored. How the second reset was initiated was not
specified; do not invent a reset method. The retained
`serial-monitor-20261012T084719Z/{before.json,after.json,capture/serial.log}`
files were read offline and agree with fsim's report: unchanged ready=true status
and a startup diagnostic. No live poll was used to verify them.

The installed host pyserial 3.5 POSIX implementation executes:

```text
os.open(port, O_RDWR | O_NOCTTY | O_NONBLOCK)
_reconfigure_port(force_update=True)
_update_dtr_state()  # separate ioctl, false clears DTR
_update_rts_state()  # separate ioctl, false clears RTS
```

Setting `dtr=False` and `rts=False` before `open()` does not make those settings
atomic with the kernel opening the device. The collector requests no reset, but
its comment cannot guarantee no electrical reset pulse. A conditional mechanism
fits Olimex Rev B's Q4 circuit: if the driver initially asserts both controls,
pyserial deasserts DTR before RTS, briefly leaving physical DTR high and RTS low;
Q4 can pull the common RST/EN low until RTS is also deasserted. The actual initial
CH341 levels, pulse duration and occurrence on this bench have **not** been
measured or established from kernel source. This is a testable hypothesis, not a
confirmed driver defect. Do not blindly reverse control-line order: Q5 also
controls ESP32 boot selection.

The exact captured diagnostic is:

```text
[683][E][esp32-hal-misc.c:143] disableCore1WDT(): Failed to remove Core 1 IDLE task from WDT
```

The 683 is firmware time, not host time. The warning is consistent with startup
but may be buffered; it does not by itself prove a fresh reset or cause the
keyboard failure. A shared reset followed by EMOS startup/layout configuration
could explain the observed input-epoch boundary, but that causal chain remains
unverified. Retained pyserial source inspection is in the ignored review record
`pyserial-open-order.txt`; no device was opened to inspect it.

The schematic provenance is retained in
[AUDIT-004's hardware trace](../AUDIT-004/trace-hardware-and-dependencies.md).
Official API context: sibling agon-docs `docs/mos/Keyboard.md`; the retained
VDP source defines the standard general-poll and keyboard-layout streams.

## R01-03 — Next bounded investigation, not executed

1. Treat the final mainboard flash reset as an Agon reboot. Establish completed
   startup and an actual CLI/listener exchange afterward, rather than assuming
   eZ80 stayed at its prior prompt or trusting a ready flag sampled mid-startup.
2. The Author has now isolated collector opening as the reset trigger on this
   installed P2 pair. Further physical work should identify the control-line
   transient and compare the failed first startup with recovery on the second
   reset, without another broad campaign. For subsequent capture qualification: Arrange the collector
   before final reset/CLI qualification, then compare one listener/EXIT/re-entry
   with it absent and one with it already open. No campaign replay or automatic
   recovery. Opening after qualification is the specific suspected disturbance.
3. If an unexpected epoch appears, stop. The decisive missing evidence is whether
   RST/EN pulsed and whether EMOS replayed startup before EDP received `23,0,&81`.
   Correlate those boundaries before proposing firmware repair. Existing status
   counts alone cannot distinguish legitimate startup from misframed UART input.
4. Require an actual harmless CLI exchange to qualify keyboard recovery; do not
   accept ready=true alone. Keep firmware and wiring fixed for that comparison. Author reports cold power
   recovery and a successful browser Agon-only reset; neither explains all prior
   failures. Do not require stock VDP substitution to investigate the installed
   P2 combination. No renderer, parallel or keyboard replay changes are justified
   by this review alone.

Source review/replay complete; physical diagnosis and remedy remain open under
BENCH-010 B10-02/B10-03. The current fsim foreground service/bench is untouched.
