# Cross-repository ownership

The Extender product uses the following implementation and reference
repositories. Each current artifact and task must have one authoritative owner.

1. `agon-extender` owns the assembled product: ESP32-P4/EDP firmware and
   hardware, operating-mode and transport contracts, cross-processor
   architecture, wiring, system integration, and product-level qualification.
2. `agon-emos` owns Extender MOS (EMOS): maintained MOS-derived source,
   eZ80-side Extender behavior, EMOS APIs, foreground utility dispatch and resident service implementation,
   product-specific tests, implementation tasks, and EMOS qualification.
3. The canonical `agon-mos` and `agon-vdp` directories are read-only stock
   references, kept clean at their most recent official tagged releases.
   They do not host local fixes, experiments, or Extender development. Preserve
   such work in separate project-owned checkouts. The distinct `mystuff/agon-mos`
   checkout is the Author's MOS fork and owns generic MOS development; its
   `qsort` branch holds the relocated qsort work. This Author clarification
   of 2026-09-07 supersedes the earlier upstream-fork working role for the
   canonical MOS directory.
4. `mos-agondev` owns reusable AgonDev preparation, translation, build,
   linking, runtime, emulator, inspection, and qualification infrastructure for
   MOS-family source. It consumes product-specific policy only through explicit
   profiles or options and does not own maintained EMOS source.

Generated prepared source, translated assembly, objects, maps, firmware, and
emulator staging are disposable outputs. Cross-component requirements remain
here, but implementation work is assigned to the repository whose processor,
firmware, software, or hardware performs it. Historical records may name former
commits and branches as provenance; they do not restore superseded ownership.

## TRS-80 consumer boundary

Extender may accommodate TRS-80 through reusable P4 services, transport APIs,
resource ownership and EMOS integration contracts. These implementations must
remain independent of the emulated machine. The dependency runs from the
TRS-80 project to explicitly selected Extender interfaces, never from Extender
to the TRS-80 runtime.

All code that runs or specifically adapts TRS-80 belongs only in the TRS-80
project: MAME machine/CPU emulation, Model 4 devices and memory maps, guest
OS integration, machine-specific protocol interpretation, framebuffer conversion,
input mappings and startup/UI composition. Do not vendor that implementation
into Extender, including as a conditional build or test fixture. Common-service
tests here use generic providers/fakes; TRS-80 integration tests live there.

Extender task documents may retain coordination, feasibility and interface
requirements for this consumer. Their presence does not assign ownership of
TRS-80 implementation to this repository. If a requested change mixes reusable
service work and machine-specific glue, split it at this boundary before coding.
