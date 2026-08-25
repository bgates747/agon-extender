# AUDIT-002 extracted Fritzing connectivity

- Input: `tasks/SETUP-006/SETUP-006.4-wiring-design/light2-extender-breadboard-wiring-draft_v1.fzz`
- SHA-256: `e3b5a44bb1c795dc120c21c77ffd0e3855eb2a6d0772b7781700ce1d59a836c0`
- Instances: 49
- Conductive nets: 234

## Components

| Component | Kind | Value/color | Endpoint nets |
|---|---|---|---|
| `R1` | resistor | `220` | connector0=N127, connector1=N181 |
| `R2` | resistor | `220` | connector0=N128, connector1=N182 |
| `R3` | resistor | `220` | connector0=N129, connector1=N183 |
| `R4` | resistor | `220` | connector0=N062, connector1=N123 |
| `R5` | resistor | `220` | connector0=N063, connector1=N124 |
| `R6` | resistor | `220` | connector0=N002, connector1=N065 |
| `Wire1` | wire | `#ffffff` | connector0=N131, connector1=N131 |
| `Wire2` | wire | `#ef6100` | connector0=N132, connector1=N132 |
| `R7` | resistor | `220` | connector0=N184, connector1=N201 |
| `Wire3` | wire | `#fff800` | connector0=N023, connector1=N023 |
| `Wire4` | wire | `#999999` | connector0=N184, connector1=N184 |
| `R8` | resistor | `10000` | connector0=N067, connector1=N125 |
| `R9` | resistor | `220` | connector0=N202, connector1=N130 |
| `R10` | resistor | `10000` | connector0=N133, connector1=N125 |
| `Wire9` | wire | `#cc1414` | connector0=N133, connector1=N133 |
| `Wire10` | wire | `#cc1414` | connector0=N133, connector1=N133 |
| `C1` | capacitor | `100nF` | connector0=N023, connector1=N125 |
| `Wire11` | wire | `#25cc35` | connector0=N023, connector1=N023 |
| `Wire12` | wire | `#ef6100` | connector0=N125, connector1=N125 |
| `Wire15` | wire | `#ffffff` | connector0=N133, connector1=N133 |
| `Wire16` | wire | `#ffffff` | connector0=N131, connector1=N131 |
| `Wire17` | wire | `#418dd9` | connector0=N132, connector1=N132 |
| `R11` | resistor | `220` | connector0=N066, connector1=N147 |
| `Wire22` | wire | `#999999` | connector0=N023, connector1=N023 |
| `R12` | resistor | `10000` | connector0=N125, connector1=N146 |
| `R13` | resistor | `10000` | connector0=N023, connector1=N132 |
| `R14` | resistor | `10000` | connector0=N005, connector1=N125 |
| `Wire48` | wire | `#418dd9` | connector0=N005, connector1=N005 |
| `Wire49` | wire | `#418dd9` | connector0=N005, connector1=N005 |
| `R15` | resistor | `10000` | connector0=N125, connector1=N131 |
| `Wire70` | wire | `#999999` | connector0=N130, connector1=N130 |
| `Wire71` | wire | `#999999` | connector0=N130, connector1=N130 |
| `Wire72` | wire | `#25cc35` | connector0=N067, connector1=N067 |
| `Wire73` | wire | `#fff800` | connector0=N066, connector1=N066 |
| `Wire74` | wire | `#fff800` | connector0=N003, connector1=N003 |
| `U1` | logic_ic | `--` | connector0=N133, connector1=N184, connector10=N147, connector11=N003, connector12=N133, connector13=N125, connector2=N202, connector3=N067, connector4=N130, connector5=N201, connector6=N023, connector7=N145, connector8=N023, connector9=N146 |
| `Agon3V3Entry` | wire | `#cc1414` | connector0=N125, connector1=N125 |
| `Agon3V3RailBridge` | wire | `#cc1414` | connector0=N125, connector1=N125 |
| `AgonGroundEntry` | wire | `#111111` | connector0=N023, connector1=N023 |
| `GroundRailBridge` | wire | `#111111` | connector0=N023, connector1=N023 |
| `P4SignalGround` | wire | `#111111` | connector0=N023, connector1=N023 |

## Structural findings

1. Nonreciprocal direct connections: 0.
2. Multiply occupied breadboard holes: 0.
3. Passive pins with no direct placement/connection: 0.

The extracted net IDs are deterministic within this exact input. They are audit
labels, not design net names and not stable interface identifiers.
