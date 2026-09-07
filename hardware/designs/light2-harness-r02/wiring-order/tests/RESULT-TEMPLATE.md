# Construction-step result template

Copy this template for a new result; do not overwrite a completed record.
Use the actual run ID when one exists. A blank means unrecorded, not passed.

| Identity and boundary | Record |
| --- | --- |
| Step and procedure identity/revision; source commit | — |
| Actual circuit and assembly identities; cumulative installed steps | — |
| Operator, local/UTC start and finish; run ID | — |
| New permanent connections; as-built photo/contact-map reference | — |
| Extra/missing connections and departures from the reviewed procedure | — |
| Agon and P4 firmware/build/image hashes; executed components and caller | — |
| EMOS startup invocation and declared final state | — |
| Supplies, cables, DMM, analyzer/probes and instrument settings | — |
| Exact source, destination and bank-enable probe terminals | — |
| Bench authorization and preflight record | — |

| Check | Expected | Observed / evidence |
| --- | --- | --- |
| Unpowered values, continuity and unintended bridges | Exact step wiring | — |
| Rail voltages before stimulus | Procedure's declared bands | — |
| All powered inputs and enabled-bank channels defined | Step's state table | — |
| Held low at source and destination | Procedure's declared low levels | — |
| Held high at source and destination | Procedure's declared high levels | — |
| Enabled pulse pattern | Destination follows source; counts agree | — |
| Released destination and enables | Declared passive bias | — |
| Previously installed lane(s) sharing this enable | Declared held/test state | — |
| Candidate byte/count comparison, when applicable | Exact expected content | — |
| Stop/release and final power state | Procedure's declared final state | — |

Record outcome (`pass`, `fail`, `partial`, `aborted`, or `invalid`), exact claim,
limitations, and Author's disposition: —

Raw capture/log and manifest links: —

Unexpected readings and corrective-action reference: —

A digital capture records sampled logic. Keep analog readings, byte-oracle
results and captures distinguishable in the claim. No result is qualified
merely because this template is complete.
