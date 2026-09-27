# R05-A04 — resident admission implementation results

The development EMOS image builds, all 112 host tests pass, and five real-eZ80
emulator runs pass against a controlled UART peer. This establishes the private
CLI wake and finite-utility dispatch boundary, not working WebDAV transfers.
No P4 source, hardware, physical SD or production selection was changed.
Emulator-coupled source is uncommitted pending Author validation.

## Scope and evidence

| Check | Result | Evidence |
| --- | --- | --- |
| Older/unresponsive peer | Prompt remains usable; no job admitted | [absent](absent.json), [transcript](absent.log) |
| Corrupt offer CRC | Offer ignored; typed command completes | [corrupt](corrupt.json), [transcript](corrupt.log) |
| Key before DECIDE acknowledgement | Partial input wins; provisional grant withdrawn; no utility | [key race](key-race.json), [transcript](key-race.log) |
| Missing finite utility | Error reported, later command executes | [missing](missing.json), [transcript](missing.log) |
| Loaded finite probe | 4096 application bytes preserved, nested loader denied, public editline works without service polling; prompt restored | [utility](utility.json), [transcript](utility.log) |
| Maintained C engine with ASan/UBSan | Invalid sequence/incarnation, timeout/stalled clock, mode gate, counter exhaustion, loader failure, no false success pass | EMOS tests/test_emos_admission.py |
| Existing EMOS regression suite | 112 tests pass; 3.265 seconds host wall time | EMOS unittest suite with selected prepared worktree |
| Target build and linked guards | Pass: ABI, VDU routing, parallel entry points, keyboard, console and UART divisor | EMOS firmware-check wrapper |

The fixture deliberately returns without implementing a file operation. EMOS
reports backend unavailable rather than falsely claiming transfer success.
The CLI emulator's minimal VDP prints unknown mode/startup packets; it is not a
visual rendering check. Its retained UART adapter replaces P4 and does not prove
physical baud, P4 capability handling, ExCom parser behavior or reboot recovery.
Run durations in JSON are host wall-clock functional-test durations, not throughput
measurements. The initial fixture used decimal 40000 for its sentinel LOAD;
corrected to explicit 0x40000 before the retained passing run.

## Memory and compatibility

| Measurement | Bytes |
| --- | ---: |
| Development firmware image, unversioned / do not deploy | 127474 |
| Arithmetic space below 128 KiB flash image limit | 3598 |
| New admission object text | 2529 |
| New admission object initialized state | 4 |
| New admission object BSS | 143 |

The selected production image is 124774 bytes; the development image is 2700
bytes larger. This whole-image comparison includes differing identity strings;
it is not an identity-normalized code-size delta. The resident implementation
contains no WebDAV/filesystem engine and no dynamic allocations.

Public mos_EDITLINE flags and CR/ESC returns are unchanged. Only top-level
mos_input calls the private editor wrapper. An empty line may poll at most once
per clock advance. A pending key invalidates admission; tab storage is freed
before utility loading. The checked existing loader uses the MOSlet region and
loads only `/emos/sdjob.bin --admitted`. The manual sdserve command is unchanged.

## Remaining boundaries

R05-A04 is implemented with automated checks passing; human emulator validation
remains before commit. A05–A08 must supply the linked application helper, finite
file utility, descriptor handling, job-bound data, confirmed completion/cleanup,
P4 staging and WebDAV. READY/actual filesystem success is intentionally unavailable
in this A04 implementation. Test double capability advertisement does not qualify
those endpoints. Paired ExCom and physical testing remain A09–A12; no bench work
was performed. This candidate must not replace production.
