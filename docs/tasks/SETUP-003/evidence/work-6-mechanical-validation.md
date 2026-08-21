# SETUP-003 Work 6 mechanical validation

Validation date: 2026-08-20

The extractor generated 5,610 normalized evidence records from the official
VDP and declared dependency source trees:

- 103 global/static symbol candidates;
- 864 include directives;
- 729 conditional-compilation directives;
- 397 protocol-related symbol-name candidates; and
- 3,517 categorized platform, lifecycle, memory, transport, and feature source
  occurrences.

Validation established that:

- the YAML parses successfully;
- every owner/path/line tuple resolves to the indexed source and a valid line;
- declared section and category counts equal the emitted records;
- two consecutive runs produce byte-identical output;
- no checkout or host-specific absolute path appears in the output; and
- the generator passes Python syntax validation.

The first validation pass found that normalized CRC and vdp-gl paths omitted
their `src/` component. The path mapper was corrected before this evidence was
accepted. The final generated file has SHA-256
`9e73b22c71e9d88cef304fa89a9e4cff133ea7e5215834ce4b05366830bcd62d`
at the mechanical-only review gate.

The completed Work 6 generator now merges a separately reviewed semantic layer
after validating 95 owner/path/line references and six exact source-wide
searches. The combined output contains 12 reviewed runtime subsystem records
and has SHA-256
`f29b4d4f3711769b48a7d38dcafe4e543d7beaca77f49baf9904f8774ed5d7b7`.
No architectural driver disposition is inferred.
