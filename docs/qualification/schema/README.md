# Qualification schema and semantic rules

`compatibility-matrix.schema.json` validates the generated canonical join using
JSON Schema Draft 2020-12. Cross-record rules live in
`scripts/qualification_model.py` because JSON Schema cannot enforce global ID
uniqueness, tuple uniqueness, referential integrity, source coverage, evidence
scope, or repository references.

The validator additionally enforces:

- one globally unique ID across every collection;
- one mode-expectation tuple per interface and mode;
- valid parents, subjects, modes, evidence links, source links, task/decision
  references, and dependency-node references;
- exact pre-Gate-2 coverage of the accepted SETUP-004 VDU inventory;
- blocker and qualification-basis requirements;
- accepted supporting evidence for every `qualified` obligation;
- strict separation of compatibility and secondary-capability evidence;
- deterministic ordering and generated-input digests; and
- absence of absolute paths, credentials, and machine-local topology.
