# Stage 01 — Power-domain construction results, 2026-09-04

Status: completed preliminary construction observations; not qualified.
Historical identity status: `pre-policy` naming/provenance; no compliant build
or run-start ID was recorded, and none has been assigned retrospectively.

1. Circuit: [`light2-harness-r02`](../../README.md).
2. Selected view: [01 — power domains](../../signal-views/generated/01_schematic_power-domains.kicad_sch).
3. Evidence source: Author-reported meter readings and bench observations,
   originally recorded in [QUAL-002](../../../../../docs/tasks/QUAL-002.md).
4. Observation times below are local EDT on 2026-09-04. Instrument identity,
   complete cumulative as-built map, and full initial firmware provenance were
   not recorded in the original observations.
5. Relocation note, 2026-09-05: moved beside the design at the Author's request.
   Readings, timestamps, hashes, and evidence limitations are retained. The
   original present-tense task status has been clarified as historical; source
   navigation now links to the fixture. This move adds no measurements.

## Recorded observations

These observations were reported by the Author on 2026-09-04 at 18:32 EDT
while constructing the `light2-harness-r02` power-domain stage. They are
diagnostic construction evidence only. At the time, formal QUAL-002
qualification had not started and neither review gate was satisfied. The task
now records staged work in progress; these observations confer no qualification
claim or review-gate approval.

1. Both processor boards, all four buffer ICs, and their ordinary
   harness/header connections were installed. Both boards were unpowered.
2. Measured resistance from `P4_3V3` to common ground was 14.6 kohm.
3. Measured resistance from `AGON_3V3` to common ground was 3.8 kohm.
4. Measurements from `AGON_3V3` to two physical points on the joined P4 power
   rail were 74.4 kohm and 28.8 kohm. Direct continuity testing subsequently
   confirmed that those P4 rail sections are joined. The differing resistance
   observations are therefore not evidence of separate P4 power domains; the
   cause has not been isolated and may include measurement settling,
   capacitor charging, semiconductor paths, probe polarity, or contact.
5. None of the reported measurements indicates a hard rail-to-ground or
   rail-to-rail short. Because the attached boards and ICs expose parallel
   semiconductor paths, these values cannot qualify the passive harness or be
   compared directly with an individual pull-resistor value.
6. No powered measurement had been performed when this record was written.
   The proposed next diagnostic is P4-only power with the Agon connected but
   unpowered. With the meter in DC-voltage mode and referenced to common
   ground, measure:
   1. the left physical P4 3.3 V rail — expected approximately 3.3 V;
   2. the right physical P4 3.3 V rail — expected approximately 3.3 V and
      substantially equal to the left rail;
   3. `U4.14` — expected approximately 3.3 V;
   4. `AGON_3V3` — expected approximately 0 V and provisionally below 0.2 V;
      and
   5. `U1.20` — expected approximately 0 V and provisionally below 0.2 V.

   Immediately remove P4 power upon heating, odor, repeated reset, abnormal
   current, or material voltage on the unpowered Agon domain. These provisional
   expectations make the construction diagnostic interpretable; they do not
   constitute a frozen QUAL-002 procedure or Gate 2 authorization.
7. At 18:41 EDT, the Author reported these P4-only powered observations:
   1. `U4.14` to common ground: 3.4 V — within the provisional 3.3 V +/-5%
      range;
   2. `AGON_3V3` to common ground: 4.0 mV — below the provisional 0.2 V
      back-power threshold; and
   3. `U1.20` to common ground: 1.4 mV — below the provisional 0.2 V
      back-power threshold.

   The Author subsequently reported 3.4 V on both the left and right physical
   P4 rail sections. These observations complete the preliminary P4-only
   construction check: both rail sections agree, `U4` receives P4-domain
   power, and the unpowered Agon domain remains effectively at zero at both
   measured points. This remains preliminary diagnostic evidence, not a
   QUAL-002 qualification pass.
8. At 18:53 EDT, with both processor boards and all four buffer ICs connected,
   the Author reported these Agon-only powered observations:
   1. `AGON_3V3` and the VCC pins `U1.20`, `U2.20`, and `U3.14`: 3.27 V;
   2. both physical P4 3.3 V rail sections and `U4.14`: 0.1--0.2 mV.

   These observations complete the preliminary Agon-only construction check.
   The Agon-powered ICs receive a consistent in-range supply while the
   connected, unpowered P4 domain remains effectively at zero, well below the
   provisional 0.2 V back-power threshold. This remains preliminary diagnostic
   evidence, not a QUAL-002 qualification pass.
9. At 18:59 EDT, a temporary bench-only P4 passive-GPIO image was built and
   flashed for subsequent dual-powered construction diagnostics:
   1. application identity: `agon-extender-p4-passive-r01`;
   2. source SHA-256:
      `50b60db9aa6e33a19b41a357d8c01bce9b380703c6ecc566ac044e839a6e7091`;
   3. factory-image SHA-256:
      `6693897457b4d4afa283b15111f7576532e2f29277942132afc21c63743733a2`;
   4. selected harness pads: P4 GPIO 9--15, 17, 20--23, 32, and 33;
   5. application behavior: reset each selected pad, set it to input-only, and
      disable both internal pulls before idling indefinitely; no Extender
      transport, Ethernet, UART, PARLIO, display, or application service is
      initialized;
   6. target identity: the expected stable USB identity resolved uniquely and
      esptool identified ESP32-P4 revision 1.3 with the expected MAC;
   7. deployment: the 440,272-byte combined image was written at offset zero,
      esptool's write hash verified, and the P4 hard-reset normally.

   This temporary image controls application behavior only. It does not prove
   boot-ROM or pre-`setup()` pad behavior; r02's external fail-safe circuit owns
   that interval. The first isolated build attempt also exposed that an
   absolute `board_build.sdkconfig_defaults` path was ignored by this
   PlatformIO composition, leaving the ESP-IDF default 100 Hz FreeRTOS tick.
   Copying the accepted defaults into the temporary project selected the
   required 1000 Hz tick and produced the successful build. The source
   is preserved in the [passive-GPIO fixture](../../../../../docs/tasks/QUAL-002/p4-passive-r01/README.md); its tracked
   source hash matches the flashed temporary source exactly, and a build from
   that tracked project completed successfully. The rebuilt factory image is
   not expected to be byte-identical because the application embeds its build
   timestamp.
10. At 19:07 EDT, with both boards powered and the P4 running the passive-GPIO
    image, the Author reported these dual-powered idle observations:
    1. `AGON_3V3`, `U1.20`, `U2.20`, and `U3.14`: 3.27 V;
    2. both physical P4 3.3 V rail sections and `U4.14`: 3.43 V;
    3. direct `AGON_3V3`-to-`P4_3V3` difference: 153 mV;
    4. the Agon retained stable stock-VDP VGA output without resetting and
       displayed a flashing cursor at the MOS prompt throughout the
       measurements, supporting that MOS/eZ80 and stock VDP remained normally
       responsive;
    5. neither processor board, IC, power/ground conductor, nor passive became
       hot to the Author's touch, and no odor or smoke was observed; and
    6. a subsequent read-only Pi check found the expected P4 USB identity still
       present at its stable by-id path, resolved to `/dev/ttyACM0`.

    The P4 Ethernet jack was physically disconnected throughout the reported
    unpowered, single-board-powered, and dual-board-powered checks. These
    observations therefore provide no evidence for an Ethernet-connected power
    state.

    The rail readings agree with the two independently regulated domains and
    satisfy the proposed dual-powered construction expectations. Stable USB
    enumeration establishes only continued host visibility; it does not prove
    application liveness, absence of reset, or GPIO high impedance. This is a
    completed preliminary dual-powered power-domain check, not a QUAL-002
    qualification pass.
