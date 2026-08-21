# SETUP-003 Work 5 symbol-index review

Review date: 2026-08-20

## Tool provenance

The host did not have Universal Ctags installed, and system installation was
not possible without an interactive sudo password. The Ubuntu Noble package
`universal-ctags_5.9.20210829.0-1_amd64.deb` was downloaded and extracted under
`/tmp` without changing the system installation.

- Tool report: Universal Ctags 5.9.0, compiled 2021-09-03
- Features used: JSON, C, and C++ parsers
- Package SHA-256:
  `e39c01992aae4208da2ca93b1fe7f4f871936a46d3d9592751aa44714d622f7e`

The package and extracted binary are disposable. Regeneration requires an
equivalent Universal Ctags executable supplied through `--ctags`.

## Result

The normalized index contains 8,274 records:

- 2,679 from agon-vdp;
- 5,010 from vdp-gl;
- 53 from ESP32Time; and
- 532 from CRC.

It includes functions, methods, classes, structs, unions, enums, enumerators,
macros, variables, external-variable declarations, prototypes, typedefs,
members, namespaces, signatures, scopes, static/file-local markers, and source
locations.

## Manual validation

Representative checks confirmed:

- Arduino entry definitions `setup`, `loop`, and `processLoop` in `video.ino`;
- the `VDUStreamProcessor` class and its header-defined methods;
- overloaded class methods with scope and signatures;
- static and inline functions defined in headers;
- macro names, parameters, and retained macro definitions;
- `extern` declarations such as `processor`, `rtc`, `soundGenerator`, and
  `startup_screen_mode`; and
- corresponding global definitions where present in the indexed source.

The first pass omitted `video.ino` because Ctags does not map `.ino` to C++ by
default. The generator now supplies `--map-C++=+.ino`; the three Arduino entry
definitions were then present at their correct source lines.

## Interpretation limits

This is a source index, not a successful-build symbol table:

- conditional branches are indexed even when inactive in the P4 build;
- macro expansion and generated declarations are not synthesized;
- declarations and definitions can legitimately produce multiple records;
- constructor definitions are reported as functions scoped to their class;
- an `extern` source statement is not necessarily one external-variable record
  because it may declare a function or multiple names; and
- link-time presence and final ownership require Work 7's successful ELF.

These limits are useful for survey work: the index describes code available in
the baseline source, while compiler and eventual ELF evidence determine what
is selected into a particular firmware image.
