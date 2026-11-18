# Two-way PARLIO SD physical qualification r03

The corrected P4 candidate staged the worked example and all scratch inputs,
then retrieved all eight scratch files with exact byte equality. The worked
example reported `OLIMTEST PASS` and returned its exact 20-byte report over
PARLIO. The largest file transferred in both directions was 1,100,000 bytes.

The [r02 candidate record](PRODUCTION-SD-PARALLEL-R02.md) preserves the first
campaign's two transport losses and the listener-install correction. The r03
P4 source closes the tested boot-watcher race. The hardware result qualifies
the selected combination and cases. The first campaign's pin-level failure
cause remains unconfirmed.

## Installed candidate

| Component | Pin |
| --- | --- |
| P4 source | `be1d94329e55cc5e4243adbcdad73e3c530f9053` |
| P4 application, 1,768,624 bytes | `539dc7176f079bc6c298c48352b7e94c54db654fb6fdbb9c42897370fb19834b` |
| P4 app0 write, 1,769,472 bytes | `10d4b60a67888c2363e79ad29adbfd68d58a8638fd9013af413973655cb33ae4` |
| EMOS ROM, 131,072 bytes | `9b90b5d94ec6888d85ef1fa1acf23a82b2e0eb1f179b75f549863fbd72343673` |
| Canonical listener, 26,127 bytes | `98492acc7dcd29e484ef76c69026e8801375738c33c617ba61a94d8481151f08` |
| Qualification packet | `16d117ebe71361afa786d42741b76e34f485e1bedaa8a1cc9eae6d83c1e00bf5` |
| Runner revision | `39a7348bf61eed9885c071d771eb770e2caa4bba` |

The Pi5 runner used the fresh `/test/port008-sdparallel-r03` namespace.
It checked each PUT's transfer completion and recorded PARLIO for all
nonempty files. The empty file used control records in both directions. A
separate qualification GET compared each destination with its local source.
The fixture used one observed LOAD and RUN, followed by the returned CLI.

## Largest file, 1,100,000 bytes

| Direction | Pi5 elapsed (s) | Pi5 rate (kB/s) | P4 file worker (s) | Physical completion |
| --- | ---: | ---: | ---: | --- |
| Mainboard SD → Pi5 | 31.556 | 34.9 | 30.084 | 2,149 PARLIO blocks |
| Pi5 → mainboard SD | 13.266 | 82.9 | 10.801 | 1,100,000 clocks and one VALID interval |

The table ranks the slower direction first. The Pi5 elapsed times include
the staged HTTP operation and remote file work. Rates use decimal kB and
describe the full file operation. The scratch comparison runs afterward.
The eight tested scratch sizes were 0, 1, 511, 512, 513, 4,097, 65,537,
and 1,100,000 bytes.

## Evidence and process reconciliation

The host stopped the original stage supervisor and worker after the nine
successful transfer receipts and the listener EXIT reply. Its wait result
was unavailable. The continuation verified both process groups were absent,
matched the nine receipts and local staged inputs to the packet, and witnessed
a fresh working CLI, idle transfers and free ports. It then ran the original
download and fixture phases without repeating any uploads.

The operator's local evidence under
`agents/port008-production-parallel-r03/physical-r02/` includes the output
and source identity receipts in `stage/`, `reconcile-stage/`,
`verify-scratch/` and `run/`. The exact result was
`Result file example\n`, SHA-256
`ab0d8b9c5c3da3b3a2f7263d85c7b8724f065bbe5d29d3f3b694742643555810`.

## Production handback

The operator restored the canonical listener, the 131,072-byte production
EMOS ROM and the 1,769,472-byte production P4 app0 extent. The listener
matched its production pin and both processor readbacks matched the
complete pinned restore bytes. The handback verified a working Legacy
CLI, neutral input, idle transfers, listener offline and both serial
handles free. The restoration and handback worker results were joined.
The scheduler confirmed the slot was released and its FIFO was empty.

The [production promotion item](../PORT-008.md) retains the tested-acceptance
step for this candidate.
