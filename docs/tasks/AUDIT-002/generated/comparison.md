# AUDIT-002 expected/actual circuit comparison

- Result: **PASS**
- Checks: 60
- Failures: 0
- Reviewed FZZ SHA-256: `b337326248d4669e3624d07bb336077c7eb252cc0a1333ecec198def22f142a9`

## Checks

| Result | Category | Subject | Detail |
|---|---|---|---|
| PASS | `named_net` | `AGON_3V3` | all endpoints on N125 |
| PASS | `named_net` | `GND` | all endpoints on N023 |
| PASS | `named_net` | `D0_AGON` | all endpoints on N003 |
| PASS | `named_net` | `D0_P4` | all endpoints on N147 |
| PASS | `named_net` | `D0_ENDPOINT` | all endpoints on N066 |
| PASS | `named_net` | `D1_AGON` | all endpoints on N184 |
| PASS | `named_net` | `D1_REVERSE_OUTPUT` | all endpoints on N201 |
| PASS | `named_net` | `D1_FORWARD_OUTPUT` | all endpoints on N202 |
| PASS | `named_net` | `D1_P4` | all endpoints on N130 |
| PASS | `named_net` | `D2_AGON` | all endpoints on N002 |
| PASS | `named_net` | `D2_P4` | all endpoints on N065 |
| PASS | `named_net` | `D3_AGON` | all endpoints on N183 |
| PASS | `named_net` | `D3_P4` | all endpoints on N129 |
| PASS | `named_net` | `D4_AGON` | all endpoints on N063 |
| PASS | `named_net` | `D4_P4` | all endpoints on N124 |
| PASS | `named_net` | `D5_AGON` | all endpoints on N182 |
| PASS | `named_net` | `D5_P4` | all endpoints on N128 |
| PASS | `named_net` | `D6_AGON` | all endpoints on N062 |
| PASS | `named_net` | `D6_P4` | all endpoints on N123 |
| PASS | `named_net` | `D7_AGON` | all endpoints on N181 |
| PASS | `named_net` | `D7_P4` | all endpoints on N127 |
| PASS | `named_net` | `READY_N` | all endpoints on N005 |
| PASS | `named_net` | `CLOCK` | all endpoints on N132 |
| PASS | `named_net` | `VALID_N` | all endpoints on N131 |
| PASS | `named_net` | `FWD_OE_N` | all endpoints on N133 |
| PASS | `named_net` | `REV_OE_N` | all endpoints on N067 |
| PASS | `named_net` | `UNUSED_CHANNEL_3_ENABLE` | all endpoints on N146 |
| PASS | `component` | `C1` | identity and value match |
| PASS | `component` | `R1` | identity and value match |
| PASS | `component` | `R2` | identity and value match |
| PASS | `component` | `R3` | identity and value match |
| PASS | `component` | `R4` | identity and value match |
| PASS | `component` | `R5` | identity and value match |
| PASS | `component` | `R6` | identity and value match |
| PASS | `component` | `R7` | identity and value match |
| PASS | `component` | `R8` | identity and value match |
| PASS | `component` | `R9` | identity and value match |
| PASS | `component` | `R10` | identity and value match |
| PASS | `component` | `R11` | identity and value match |
| PASS | `component` | `R12` | identity and value match |
| PASS | `component` | `R13` | identity and value match |
| PASS | `component` | `R14` | identity and value match |
| PASS | `component` | `R15` | identity and value match |
| PASS | `component` | `U1` | identity and value match |
| PASS | `named_net_separation` | `AGON_3V3 != GND` | AGON_3V3=N125, GND=N023 |
| PASS | `named_net_separation` | `AGON_3V3 != D0_AGON` | AGON_3V3=N125, D0_AGON=N003 |
| PASS | `named_net_separation` | `AGON_3V3 != D0_P4` | AGON_3V3=N125, D0_P4=N147 |
| PASS | `named_net_separation` | `AGON_3V3 != D0_ENDPOINT` | AGON_3V3=N125, D0_ENDPOINT=N066 |
| PASS | `named_net_separation` | `AGON_3V3 != D1_AGON` | AGON_3V3=N125, D1_AGON=N184 |
| PASS | `named_net_separation` | `AGON_3V3 != D1_REVERSE_OUTPUT` | AGON_3V3=N125, D1_REVERSE_OUTPUT=N201 |
| PASS | `named_net_separation` | `AGON_3V3 != D1_FORWARD_OUTPUT` | AGON_3V3=N125, D1_FORWARD_OUTPUT=N202 |
| PASS | `named_net_separation` | `AGON_3V3 != D1_P4` | AGON_3V3=N125, D1_P4=N130 |
| PASS | `named_net_separation` | `GND != CLOCK` | GND=N023, CLOCK=N132 |
| PASS | `named_net_separation` | `FWD_OE_N != REV_OE_N` | FWD_OE_N=N133, REV_OE_N=N067 |
| PASS | `endpoint_separation` | `AgonPin34ThreeV3_1.agon-pin34 != P4DevKit1.ext1-pin1` | left=N125, right=N126 |
| PASS | `endpoint_separation` | `AgonPin34ThreeV3_1.agon-pin34 != P4DevKit1.ext2-pin1` | left=N125, right=N064 |
| PASS | `isolation` | `U1.connector7` | non-board members on N145: U1.connector7 |
| PASS | `structure` | `dangling_passive_pins` | expected 0, found 0 |
| PASS | `structure` | `nonreciprocal_connections` | expected 0, found 0 |
| PASS | `structure` | `occupied_hole_collisions` | expected 0, found 0 |
