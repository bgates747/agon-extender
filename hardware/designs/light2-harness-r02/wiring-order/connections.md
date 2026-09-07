# r02 connection ledger

This ledger assigns stable reference IDs to the connections in the existing
[authoritative r02 circuit](../connectivity.yaml), using the
[maintained schematic](../schematic.kicad_sch) to distinguish branches.
The [CSV inventory](connections.csv) contains the same connection rows.

## How to read the IDs

1. `W001` and following identify individual connections, independently of any
   signal view or future construction step. Repeated appearances of the same
   connection must use the same ID. These are reference IDs within
   `light2-harness-r02`, not new artifact revisions.
2. `U1.2`, for example, means component U1, physical pin 2. J1 uses the actual
   Agon header numbering; the drawing's JO1/JE1 split does not change it.
   Endpoint A/B order does not imply signal direction or construction order.
3. `B001` and following name existing schematic branch points between pins.
   Their locations and adjoining connections are listed below. They are
   electrical joins, not added parts or a requirement to install soldered
   splices. A shared breadboard strip can implement a join.
4. `rail:agon-3v3`, `rail:p4-3v3`, and `rail:ground` name the drawing's three
   shared power nets. The two positive rails remain separate. Each terminal's
   rail attachment has its own ID; physical rail segments and any links between
   them depend on the assembly layout and are not specified by this schematic.
5. A bend in a drawn wire does not get another connection ID. A connection
   ends at a component terminal, branch point, or named rail. Component bodies
   are not wires: the two ends of a resistor remain separate endpoints.
6. Preserve assigned IDs when sorting, annotating views, or later assigning
   steps. Never renumber or reuse an ID. An endpoint change requires retiring
   its old ID and allocating a new one; circuit changes still follow the
   [project version policy](../../../../docs/versions/README.md).

No stage assignments or installation/completion claims are recorded here.
The operator's actual wire routes, breadboard holes, and rail bridges are not
inferred from drawing geometry. This is a connection reference inventory,
not a powered-test procedure or a count of physical jumper pieces.
Only existing r02 components are included; the rejected R32–R41 additions
are excluded.

## Source and coverage

The inventory contains **133 connections**, covering all **44 nets**
and **166 connected component terminals**, with **8 named branch points**.
The 50 intentionally unconnected terminals receive no connection IDs.

Source hashes at assignment (SHA-256):

- `connectivity.yaml`: `c68e4d4ffa2211cb18d3d558b3c88393cb1583d431e9258b6e78e7a10a6eda6f`
- `schematic.kicad_sch`: `006fdbb838535f81563f0c214dfbf27bba169eb240bd134ad25738044302d209`

## Branch points

Coordinates are millimetres in the maintained schematic, not breadboard
positions. UUIDs identify the existing KiCad junction objects. A branch
already located at a component pin uses that pin name instead of a B ID.

| ID | Net | Schematic X, Y (mm) | Adjacent endpoints | KiCad junction UUID |
| --- | --- | --- | --- | --- |
| `B001` | `agon-pc1-d1-uart-rx` | 535.94, 269.24 | `J1.18`, `R11.2`, `U1.17` | `0b3582c4-4ea4-4ac8-af13-c066a255a504` |
| `B002` | `agon-pc3-d3-uart-cts` | 533.4, 271.78 | `J1.20`, `R12.2`, `U1.15` | `43a5e8de-0117-44c8-8dcc-efc2e27f1586` |
| `B003` | `p4-gpio11-d3-uart-rts` | 539.75, 144.78 | `J2.12`, `R4.2`, `U3.5` | `bb1bc784-56b2-4380-8500-6c887d8cca81` |
| `B004` | `p4-gpio12-d1-uart-tx` | 542.29, 147.32 | `J2.13`, `R2.2`, `U3.2` | `0d880bae-3ab2-4ea0-8e0d-0ed65f5fbd9b` |
| `B005` | `parallel-forward-oe-n` | 353.06, 220.98 | `B006`, `U2.1`, `U4.6` | `dab99d5f-fe77-45e1-8fab-8723074271fd` |
| `B006` | `parallel-forward-oe-n` | 500.38, 232.41 | `B005`, `R26.2`, `U1.19` | `1cfbd73a-1890-41ae-b191-b8ae5b0f91b0` |
| `B007` | `uart-forward-oe-n` | 466.09, 229.87 | `R25.2`, `U1.1`, `U4.3` | `a22d580d-a0c6-445b-a77f-e79edcee9503` |
| `B008` | `uart-return-oe-n` | 469.9, 177.8 | `R27.2`, `U3.4`, `U4.8` | `7785af99-cbdc-41b8-846d-a4bee2c0ee41` |

## Connections by net

Net grouping below is for lookup only; it specifies no wiring sequence.

### agon-3v3

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W001` | `C1.2` | `rail:agon-3v3` |
| `W002` | `C2.2` | `rail:agon-3v3` |
| `W003` | `C3.2` | `rail:agon-3v3` |
| `W004` | `C5.2` | `rail:agon-3v3` |
| `W005` | `J1.34` | `rail:agon-3v3` |
| `W006` | `R24.1` | `rail:agon-3v3` |
| `W007` | `R25.1` | `rail:agon-3v3` |
| `W008` | `R26.1` | `rail:agon-3v3` |
| `W009` | `R27.1` | `rail:agon-3v3` |
| `W010` | `U1.20` | `rail:agon-3v3` |
| `W011` | `U2.19` | `rail:agon-3v3` |
| `W012` | `U2.20` | `rail:agon-3v3` |
| `W013` | `U3.10` | `rail:agon-3v3` |
| `W014` | `U3.13` | `rail:agon-3v3` |
| `W015` | `U3.14` | `rail:agon-3v3` |

### agon-pc0-d0-uart-tx

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W016` | `J1.17` | `U1.2` |

### agon-pc1-d1-uart-rx

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W017` | `B001` | `J1.18` |
| `W018` | `B001` | `R11.2` |
| `W019` | `B001` | `U1.17` |

### agon-pc2-d2-uart-rts

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W020` | `J1.19` | `U1.4` |

### agon-pc3-d3-uart-cts

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W021` | `B002` | `J1.20` |
| `W022` | `B002` | `R12.2` |
| `W023` | `B002` | `U1.15` |

### agon-pc4-d4

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W024` | `J1.21` | `U2.2` |

### agon-pc5-d5

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W025` | `J1.22` | `U2.4` |

### agon-pc6-d6

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W026` | `J1.23` | `U2.6` |

### agon-pc7-d7

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W027` | `J1.24` | `U2.8` |

### agon-pd4-ready-n

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W028` | `J1.13` | `R13.1` |
| `W029` | `J1.13` | `R24.2` |

### agon-pd5-clock

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W030` | `J1.14` | `U1.13` |

### agon-pd7-valid-n

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W031` | `J1.16` | `U1.11` |

### ground

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W032` | `C1.1` | `rail:ground` |
| `W033` | `C2.1` | `rail:ground` |
| `W034` | `C3.1` | `rail:ground` |
| `W035` | `C4.1` | `rail:ground` |
| `W036` | `C5.1` | `rail:ground` |
| `W037` | `C6.2` | `rail:ground` |
| `W038` | `J1.33` | `rail:ground` |
| `W039` | `J2.2` | `rail:ground` |
| `W040` | `J3.2` | `rail:ground` |
| `W041` | `J3.15` | `rail:ground` |
| `W042` | `J3.18` | `rail:ground` |
| `W043` | `R18.2` | `rail:ground` |
| `W044` | `R19.2` | `rail:ground` |
| `W045` | `R20.2` | `rail:ground` |
| `W046` | `R21.2` | `rail:ground` |
| `W047` | `R22.2` | `rail:ground` |
| `W048` | `U1.6` | `rail:ground` |
| `W049` | `U1.8` | `rail:ground` |
| `W050` | `U1.10` | `rail:ground` |
| `W051` | `U2.10` | `rail:ground` |
| `W052` | `U2.11` | `rail:ground` |
| `W053` | `U2.13` | `rail:ground` |
| `W054` | `U2.15` | `rail:ground` |
| `W055` | `U2.17` | `rail:ground` |
| `W056` | `U3.7` | `rail:ground` |
| `W057` | `U3.9` | `rail:ground` |
| `W058` | `U3.12` | `rail:ground` |
| `W059` | `U4.2` | `rail:ground` |
| `W060` | `U4.5` | `rail:ground` |
| `W061` | `U4.7` | `rail:ground` |
| `W062` | `U4.9` | `rail:ground` |
| `W063` | `U4.12` | `rail:ground` |

### p4-3v3

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W064` | `C4.2` | `rail:p4-3v3` |
| `W065` | `C6.1` | `rail:p4-3v3` |
| `W066` | `J2.1` | `rail:p4-3v3` |
| `W067` | `R14.1` | `rail:p4-3v3` |
| `W068` | `R15.1` | `rail:p4-3v3` |
| `W069` | `R16.1` | `rail:p4-3v3` |
| `W070` | `R17.1` | `rail:p4-3v3` |
| `W071` | `R23.1` | `rail:p4-3v3` |
| `W072` | `R28.1` | `rail:p4-3v3` |
| `W073` | `R29.1` | `rail:p4-3v3` |
| `W074` | `R30.1` | `rail:p4-3v3` |
| `W075` | `R31.1` | `rail:p4-3v3` |
| `W076` | `U4.14` | `rail:p4-3v3` |

### p4-gpio10-d5

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W077` | `J2.11` | `R6.2` |
| `W078` | `J2.11` | `R19.1` |

### p4-gpio10-d5-driver

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W079` | `R6.1` | `U2.16` |

### p4-gpio11-d3-uart-rts

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W080` | `B003` | `J2.12` |
| `W081` | `B003` | `R4.2` |
| `W082` | `B003` | `U3.5` |
| `W083` | `J2.12` | `R17.2` |

### p4-gpio11-d3-uart-rts-driver

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W084` | `R4.1` | `U1.5` |

### p4-gpio12-d1-uart-tx

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W085` | `B004` | `J2.13` |
| `W086` | `B004` | `R2.2` |
| `W087` | `B004` | `U3.2` |
| `W088` | `J2.13` | `R15.2` |

### p4-gpio12-d1-uart-tx-driver

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W089` | `R2.1` | `U1.3` |

### p4-gpio13-valid-n

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W090` | `J2.14` | `R10.2` |
| `W091` | `J2.14` | `R23.2` |

### p4-gpio13-valid-n-driver

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W092` | `R10.1` | `U1.9` |

### p4-gpio14-clock

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W093` | `J2.15` | `R9.2` |
| `W094` | `J2.15` | `R22.1` |

### p4-gpio14-clock-driver

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W095` | `R9.1` | `U1.7` |

### p4-gpio15-uart-forward-control-n

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W096` | `J2.16` | `R28.2` |
| `W097` | `J2.16` | `U4.1` |

### p4-gpio17-parallel-forward-control-n

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W098` | `J2.18` | `R29.2` |
| `W099` | `J2.18` | `U4.4` |

### p4-gpio20-ready-control-n

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W100` | `J3.13` | `R31.2` |
| `W101` | `J3.13` | `U4.13` |

### p4-gpio21-uart-return-control-n

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W102` | `J3.12` | `R30.2` |
| `W103` | `J3.12` | `U4.10` |

### p4-gpio22-d0-uart-rx

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W104` | `J3.11` | `R1.2` |
| `W105` | `J3.11` | `R14.2` |

### p4-gpio22-d0-uart-rx-driver

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W106` | `R1.1` | `U1.18` |

### p4-gpio23-d2-uart-cts

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W107` | `J3.10` | `R3.2` |
| `W108` | `J3.10` | `R16.2` |

### p4-gpio23-d2-uart-cts-driver

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W109` | `R3.1` | `U1.16` |

### p4-gpio32-d4

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W110` | `J3.9` | `R5.2` |
| `W111` | `J3.9` | `R18.1` |

### p4-gpio32-d4-driver

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W112` | `R5.1` | `U2.18` |

### p4-gpio33-d6

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W113` | `J3.8` | `R7.2` |
| `W114` | `J3.8` | `R20.1` |

### p4-gpio33-d6-driver

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W115` | `R7.1` | `U2.14` |

### p4-gpio9-d7

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W116` | `J2.10` | `R8.2` |
| `W117` | `J2.10` | `R21.1` |

### p4-gpio9-d7-driver

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W118` | `R8.1` | `U2.12` |

### p4-uart-rts-driver

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W119` | `R12.1` | `U3.6` |

### p4-uart-tx-driver

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W120` | `R11.1` | `U3.3` |

### parallel-forward-oe-n

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W121` | `B005` | `B006` |
| `W122` | `B005` | `U2.1` |
| `W123` | `B005` | `U4.6` |
| `W124` | `B006` | `R26.2` |
| `W125` | `B006` | `U1.19` |

### ready-n-driver

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W126` | `R13.2` | `U4.11` |

### uart-forward-oe-n

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W127` | `B007` | `R25.2` |
| `W128` | `B007` | `U1.1` |
| `W129` | `B007` | `U4.3` |

### uart-return-oe-n

| Connection ID | Endpoint A | Endpoint B |
| --- | --- | --- |
| `W130` | `B008` | `R27.2` |
| `W131` | `B008` | `U3.4` |
| `W132` | `B008` | `U4.8` |
| `W133` | `R27.2` | `U3.1` |
