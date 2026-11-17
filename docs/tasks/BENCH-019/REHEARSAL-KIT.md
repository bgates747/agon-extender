# Olimex rehearsal kit

The kit uses three small diagnostics to prove that the cold operator can
install and exercise a custom image on each processor. Each diagnostic uses
an existing interface. The production images provide the required handback.

| Processor | Baseline source | Restore SHA-256 | Diagnostic |
| --- | --- | --- | --- |
| EMOS | `2c79c6006d6bcb0c2b3f9d8d6aae3ef4b36c730a` | `a25f1612f4aaa542c5488cf3266d968ad3d1d61e9df3b5ce2c680650f5d7a2ca` | `EMOS BENCH019 probe` returns success through the ordinary CLI dispatcher. The same command with a different argument returns invalid parameter. |
| Extender P4 | `e14e0b8a5c3c52f87b34bbeb03f9aa463816c8c5` | `d9bcb1a2b277e4dcec808d46a33d53879ea4ac4f3e35d69f80345d3c9ac4043e` | `GET /display/status?bench019=3` returns a test JSON value of `9`; the fixture also asks for `5` and expects `25`. Ordinary display status keeps its existing behavior. |
| Mainboard VDPlet | `60e5b4ebafa3e1c8bb740e45260d78cdb6125e30` | `dc43ecb8b1c324ffd1a032e6cc0c56d8c05dd33a355ce170c23adb35ffb533ab` | The test-only system selector `VDU 23, 0, &B8` returns `&56` using the existing one-byte screen-character reply. Production ignores this selector. |

1. **Build offline.** Apply the test-only changes to isolated copies of the
   pinned sources. Keep the EMOS linked checks, the P4-PC composition, and the
   pinned VDPlet release composition with its UART provider verification. Use
   the Pi compiler FIFO for a finite, serial build job. Keep each patch, final
   binary hash, and build result with the kit.
2. **Build the fixture.** The Agon executable uses `mos_oscli` to exercise
   the EMOS command, then sends the mainboard request through ordinary EMOS VDU
   routing in Legacy. It clears the screen-character flag first and accepts
   only a fresh matching response inside a bounded wait. It saves both
   results to a task-local SD file. A host probe checks the two P4 responses
   independently. Keep the original startup file unchanged.
3. **Prepare the operator packet.** Pin the three production restore images,
   custom images, fixture, invocation, expected outputs, and supported flash
   write and verification instructions. Confirm the baseline and draft
   binary links before declaring the cold operator ready for the scheduler.

## Fixture invocation and evidence

Stage `BENCH19.bin` at `/test/bench019/BENCH19.bin`. The fixture writes
`/test/bench019/result.txt`. Use a fresh rehearsal directory or clear only a
previous result from this rehearsal's namespace. Stage installation payloads
under `/extender/install/bench019`. Leave normal startup and the SD listener
bytes alone.

Stage and verify both EMOS images and the fixture while the known working
CLI and transfer service are available. Exit the listener before issuing any
install command. Install and verify the mainboard VDPlet, the P4 application,
then EMOS. After collection, restore in reverse order. All three changes are
additive diagnostics and retain the production transport paths during the
intermediate boots.

From a working Legacy prompt, explicitly invoke the fixture:

```text
LOAD /test/bench019/BENCH19.bin &040000
RUN &040000
```

Retrieve `result.txt` after the `BENCH019 PASS`/`FAIL` completion line and the
returned CLI. The two expected lines are:

```text
EMOS PASS accepted=0 rejected=19
VDPlet PASS status=0 value=86
```

Run `check_p4.py` with the configured bench Extender HTTP origin. Both
`P4 PASS input=3 value=9` and `P4 PASS input=5 value=25` must appear. Save the
Agon result file and the host probe output before restoring the images.

## Component write scope

| Processor | Write scope | Verification |
| --- | --- | --- |
| EMOS | Full 128 KiB ROM via the existing MOS `FLASH mos … -f` utility at a verified Legacy prompt | `SAVE` `&20000` bytes from `&0` into the rehearsal namespace. Retrieve and compare the full file. |
| Extender P4 | Active application partition at `0x20000` in the retained P4-PC layout | Verify the intended flash extent and ordinary P4 startup. Preserve bootloader, partition table, OTA metadata and mutable data. |
| Mainboard VDPlet | Active application partition at `0x10000` in the retained classic ESP32 layout | Verify the intended flash extent after writing. Preserve the other app slot, bootloader, partition table and mutable storage. |

Use the machine-local bench description for the commissioned USB devices and
reset route. Follow the [installation instructions](../../installing.md) for
startup, EMOS flashing, and restoring a working CLI. Use the current draft's
exclusive slot throughout. Verify the active partition and bound application
writes to it. The final restore must cover any application sectors the custom
image wrote beyond the production binary. An application image never goes at
address zero. Stop if a component write or independent verification fails.

The frozen kit manifest identifies the original application images and the
sector-padded ESP32 write files derived from them. Write and read back only
the manifest's application range. The full-ROM EMOS files are already padded.
The application partition tables are included as layout references.

The last regular handback records a custom `767987f1` mainboard VDPlet app.
Use that existing provenance for entry. The rehearsal writes all three custom
images in one slot and leaves the listed production tuple, including `dc43ecb8`
on the mainboard. There is no preliminary production flash or firmware backup.

The [official MOS API](../../../../../agon-docs/docs/mos/API.md) documents OSCLI,
VDP flags, and sysvars. The [VDU system command reference](../../../../../agon-docs/docs/vdp/System-Commands.md)
defines the byte framing and the native screen-character reply. The classic
VDP reference is tag `v2.16.0` and MOS is tag `v3.0.2`. The test-only VDP
selector is local to this kit.
