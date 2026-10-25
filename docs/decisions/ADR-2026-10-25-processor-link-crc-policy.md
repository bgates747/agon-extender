# No processor-link CRCs without an explicit Author request

- Status: Accepted
- Completeness: Complete
- Date: 2026-10-25
- Related task: [INPUT-001](../tasks/INPUT-001.md)

EMOS and Extender VDP must not compute or require CRCs for their communications
unless the Author specifically requests them. This includes requests, replies,
control records, payloads and application copies of that traffic. Ordinary
MOS/VDP framing and existing transport error handling remain in use; another
software checksum must not replace CRC merely to evade this instruction.

The Author explicitly identifies firmware space, communication bandwidth and
processor time as scarce resources on this hobby computer. Extra software
integrity work is not a default protocol requirement. This broadens the existing
ExExt CRC prohibition to communications between EMOS and Extender VDP generally.
Historical CRC-bearing evidence and installed experimental bytes retain their
identities; this decision does not claim their implementation has been corrected.
