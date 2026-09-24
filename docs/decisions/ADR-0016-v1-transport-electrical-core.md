# ADR-0016 — V1 transport electrical core

- Status: Accepted
- Completeness: Partial
- Date: 2026-08-28
- Last amended: 2026-09-05
- Related task: HW-001
- Open-decision tracker: HW-001

## Current applicability

This accepted decision defines the **held r02 buffered circuit**, not the
active simplified r03 bench wiring. [HW-002](../tasks/HW-002.md) and the
[hardware index](../../hardware/README.md) record the latter's bounded evidence
and remaining drawing/electrical review. No buffer-enable or power-domain
isolation property here transfers to r03. The held circuit's status is not
changed by this documentation clarification.

## Context

Exclusive Compatible and Exclusive Extended require one common physical
four-signal eZ80 UART1 interface. Exclusive Extended additionally requires the
proved one-way eight-bit Agon-to-Extender parallel mapping. The predecessor
`light2-harness-r01` supplies useful pin and transfer evidence but was not
designed as the V1 common UART circuit and is not its electrical authority.

The selected circuit must tolerate separate Agon and P4 power domains, default
to released outputs, prevent opposed drivers during PC0--PC3 role changes, and
remain implementable as a controlled through-hole prototype. HW-001 derived
the candidate first from official Agon, eZ80, MOS, VDP, and Olimex evidence and
then from the exact Espressif and TI component contracts.

## Decision

1. Use one physical four-signal UART1 circuit for Exclusive Compatible and
   Exclusive Extended. Use the same PC0--PC3 contacts as parallel `D0..D3`
   only during separately owned Exclusive Extended parallel epochs.
2. Retain the predecessor's exercised forward mapping for `D0..D7`, `CLOCK`,
   `VALID_N`, and low-only `READY_N`. Do not add a reverse parallel path.
3. Use two Agon-powered `SN74LVC244AN` devices for eZ80-to-P4 forward paths,
   one Agon-powered `SN74LV125AN` for P4-to-eZ80 UART TX/RTS, and one
   P4-powered `SN74LV125AN` as four low-only isolated control sinks. The exact
   accepted channel allocation is recorded in HW-001's task-local circuit
   proposal.
4. Keep `AGON_3V3` and `P4_3V3` separate and join only the required signal
   ground. External pull-ups make every cross-board driver default disabled;
   the P4-controlled low-only sinks may enable a path only after EMOS/eZ80 and
   EDP/P4 have established the corresponding ownership state.
5. Accept this topology as the controlled-beta implementation and provisional
   V1 transport core.
6. Freeze its placement-independent electrical definition as
   `light2-harness-r02`, with R1 through R13 populated at 220 ohms. The
   authoritative record is
   `hardware/designs/light2-harness-r02/connectivity.yaml`; schematics,
   netlists, SVGs, and construction views are checked projections.
7. Retain the first forward-transport breadboard as
   `light2-extender-solderless-assembly-r01`. Assign the new construction
   target `light2-extender-solderless-assembly-r02`, explicitly selecting
   `light2-harness-r02`.
8. Permit controlled r02 prototype construction under approved bench
   procedures. This does not resolve the remaining firmware-epoch or Legacy
   electrical-absence questions and does not constitute electrical
   qualification.
9. Apply the Author-accepted PORT-008-D003 process and its D004 refinement:
   signal views isolate functions for tracing/debugging; a separate cumulative
   wiring order includes the permanent connections and input-state prerequisites
   needed for powered intermediate tests. Any electrical addition requires an
   approved successor revision. P4 and EMOS tests use applicable production-candidate components,
   and scoped diagnostic firmware may isolate an electrical measurement.
   Candidate evidence is recorded at each stage; proof that an eventual
   release consumes the tested objects follows when that release exists.
   The durable [staged process](../qualification/staged-circuit-validation.md)
   owns the workflow. This changes neither the electrical definition nor EMOS
   ownership, and confers no untested activation, mode, or release claim.

## Rationale

The four-chip arrangement implements the full UART flow-control wiring and the
existing parallel map with active, through-hole TI devices that provide
three-state control and partial-power-down behavior. Separate enable groups
permit UART and parallel epochs without rewiring. The P4-powered grounded
`SN74LV125AN` channels translate P4 control requests into Agon-domain low or
high-impedance states without tying the positive rails together.

The Author confirmed two `SN74LVC244AN` and two `SN74LV125AN` devices physically
in hand for the prototype. Availability removes a procurement blocker but was
not the electrical basis for selecting the topology.

## Consequences

1. EMOS/eZ80 owns eZ80 UART/GPIO mux and direction. EDP/P4 owns P4 UART/PARLIO
   configuration and the four active-low control GPIOs. The circuit executes
   enables but does not authorize mode changes.
2. PC0--PC3 changes role only through break-before-make UART/parallel epochs;
   PORT-008 must define and prove the two-processor transition contract.
3. The r02 breadboard may be constructed, but powered testing or connection to
   either processor remains gated by the applicable bench and qualification
   procedure. The preserved r01 breadboard is not silently revised.
4. V1 qualification still depends on resolving reset behavior, Legacy
   electrical absence, the exact EMOS/EDP epoch protocol, a production
   activation-request path, and the required physical evidence under HW-001.
   Following the Author's rejection of PORT-008-D001, the frozen r02
   all-controls-released state cannot by itself carry the EMOS-originated first
   request; r02 remains a controlled-beta core while HW-001 tracks the
   intended-circuit consequence.
5. Editorial changes that cannot affect construction, interpretation,
   behavior, or test results may preserve r02. Any electrical change requires
   a new harness revision; any physical construction change that may affect
   reproduction or results requires a new assembly revision.
