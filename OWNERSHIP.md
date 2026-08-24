# Cross-repository ownership

The Extender product spans four repositories. Each current artifact and task
must have one authoritative owner.

1. `agon-extender` owns the assembled product: ESP32-P4/EDP firmware and
   hardware, operating-mode and transport contracts, cross-processor
   architecture, wiring, system integration, and product-level qualification.
2. `agon-emos` owns Extender MOS (EMOS): maintained MOS-derived source,
   eZ80-side Extender behavior, EMOS APIs and module/service implementation,
   product-specific tests, implementation tasks, and EMOS qualification.
3. `agon-mos` is the Author's upstream-oriented official-MOS fork. It owns
   official lineage and independently useful generic MOS corrections, not EMOS
   product work.
4. `mos-agondev` owns reusable AgonDev preparation, translation, build,
   linking, runtime, emulator, inspection, and qualification infrastructure for
   MOS-family source. It consumes product-specific policy only through explicit
   profiles or options and does not own maintained EMOS source.

Generated prepared source, translated assembly, objects, maps, firmware, and
emulator staging are disposable outputs. Cross-component requirements remain
here, but implementation work is assigned to the repository whose processor,
firmware, software, or hardware performs it. Historical records may name former
commits and branches as provenance; they do not restore superseded ownership.
