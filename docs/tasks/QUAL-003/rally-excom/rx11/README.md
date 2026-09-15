# RX11 results

## Executive summary

The reusable numeric import procedure and one-command regression gate are in
place and passing. Future imports must reconcile changed protected inputs and
repeat conversion enumeration before acceptance. No firmware or game changed.

[Procedure](../../../../procedures/numeric-upstream-import-r01.md) and
[review fingerprints](../../../../dependencies/reviewed/numeric-conversions.json)
are the durable entry points, linked from the existing dependency workflow.
`code-graph.yaml` remains the sole source-selection authority.

The full runner passed in2.29seconds:65,764 fixed,65,931 parser and146 guarded
renderer cases plus36 stock controls. Gate tests reject changed/missing files
and invalid inventories. [Raw result](validation.json). Registry validation
passes. No blind hash refresh option is provided. Passing fingerprints/tests
does not replace new-site enumeration, target builds or hardware/human gates.

RX10 manual review remains open. The wider unsupported-command inventory and
game benchmarks have not started. Hardware spoken notification completed with a fresh verified receipt; startup
unchanged, Legacy MOS prompt. Human hearing remains separate. Changes committed
locally; no push. Stopped before the next chunk.
