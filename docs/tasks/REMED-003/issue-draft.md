# Draft: host-directory SD accepts an existing FA_CREATE_NEW file and fails f_sync

Ready for review; unsubmitted. The identical executable has now been checked
on physical Agon hardware and both emulator SD backends.

## Summary

The same standalone MOS application produces different FatFS results with
Fab's host-directory SD backend and its raw FAT-image backend. An existing
file opened with `FA_WRITE | FA_CREATE_NEW` returns success in directory mode
instead of `FR_EXIST`. `f_sync` on a successfully opened and written file then
returns `FR_INVALID_OBJECT` (9). Raw-image mode and physical Agon hardware
return the expected results.
The original file remains intact because the reproducer deliberately closes
the unexpectedly successful open without writing to it.

## Reproducer and results

The [small C application](fixture/src/main.c) uses only public MOS APIs.
It needs MOS 3.0 or later for `ffs_fsync`; it uses no EMOS-specific operation,
UART peer, direct hardware access or emulator-specific conditional code.
Each run creates a new `/extender/fscheck/Rnnnnn` directory and saves
`RESULT.TXT`, `CREATE.DAT` and `SYNC.DAT` there.

| Observation | Expected | Fab host directory | Fab raw FAT image | Physical Agon |
| --- | --- | --- | --- | --- |
| Open existing file with FA_CREATE_NEW | 8, FR_EXIST | **0, FR_OK** | 8 | 8 |
| Re-read original contents | Unchanged | Unchanged | Unchanged | Unchanged |
| Sync an open, written file | 0, FR_OK | **9, FR_INVALID_OBJECT** | 0 | 0 |
| Close file | 0 | 0 | 0 | 0 |
| Reopen/read written contents | Match | Match | Match | Match |

These are independently reported numeric observations, not just an aggregate
PASS/FAIL. All three runs used the identical binary:

Retained output: [directory mode](evidence/directory-result.txt),
[raw FAT image](evidence/image-result.txt), [physical Agon](evidence/hardware/RESULT.TXT),
[initial emulator observations](evidence/observations.json) and
[hardware collection record](evidence/hardware/collection.json). The returned
SD's executable hash matches the emulator executable, and both saved sentinel
files match byte-for-byte. These records do not invent exact run-start times.

```text
fatfs-file-probe-r01-b2026-09-10-17-44-59Z.bin
SHA256 58689fc7d0443ee1ca3adf8fc24cce31a1ea6724b0d3fea48a53048de27ff41a
```

The Fab checkout was `fbb7d7ca887a06966ca8a62ed22272409a5ab640`, with no
tracked changes. Its existing executable was used without modification:
SHA256 `2d1b290c37ea37cb7044f24522522f546b750b7ef93050f1ebbdbd1c66e30ac3`.
These identify the inspected checkout and executed binary separately; no new
Fab build was made for this report. The emulator was run with its native
mainboard VDP, normal CPU pacing, and SDL's dummy driver for automation.

MOS in these initial runs is the installed project EMOS v0.1.12 build
`agon-emos-v0.1.12-b2026-09-10-03-50-35Z`. Its `src_fatfs/ff.c` is byte-for-byte
identical to official MOS v3.0.2 at
`8336409351ee5314e02801a7b72a4f1bb5282519`:
SHA256 `ec97d9bceabd12ade1daf28b9c957e6b8433afddd6e349b556d20e099fbfaf64`.
Do not represent these as runs of an official stock MOS firmware image.

## Minimal procedure

1. Compile the application with AgonDev using its [Makefile](fixture/Makefile)
   and [identity-producing build script](build.py). Keep the binary unchanged
   between runs.
2. Put it at `/extender/fscheck/FSCHECK.BIN` in otherwise isolated test media.
   The parent directory must exist. Use this `autoexec.txt`:

   ```text
   VDU 22 3
   LOAD /extender/fscheck/FSCHECK.BIN
   RUN
   ```

3. Launch Fab with `--sdcard <isolated-directory>` and the identified MOS/VDP.
   Read the screen and `R00001/RESULT.TXT`: create-existing returns 0 and sync
   returns 9; the test reports FAIL.
4. Copy the same initial tree into a fresh 32 MiB FAT16 image and launch Fab
   with `--sdcard-img <image>` instead. The test reports PASS with 8 and 0.
5. Run the same binary on the physical Agon and retain `RESULT.TXT`. The
   observed result is PASS, with create-existing=8 and sync=0. The comparison
   used an Olimex Agon Light 2 without changing its installed EMOS firmware.

The project [review helper](review.py) creates isolated media and uses the
unmodified upstream runtime. It observes completion with a debugger
breakpoint; it does not substitute results for any FatFS call.

## Source correlation

In [`hostfs_mos_f_open`][source], the request uses
`OpenOptions::create(...)`; `FA_CREATE_NEW` therefore does not request Rust's
exclusive-create semantics. The error mapping also needs to preserve
`AlreadyExists` as FatFS `FR_EXIST`, rather than a generic disk error.

The same file's host-filesystem dispatcher leaves `_f_sync` untrapped.
Meanwhile, the host-backed open zeroes the emulated `FIL` and keeps the real
file in a Rust map. The observed invalid-object result is consistent with
falling through into real FatFS validation of that synthetic object. This is
source interpretation supporting the reproduction, not a tested fix.

Raw-image mode is a usable workaround for these tests. A prospective hostfs
repair should implement exclusive creation/error mapping and synchronization
of the mapped host file, including invalid-handle and host-I/O failure cases.
No repair is included in this report.

[source]: https://github.com/tomm/fab-agon-emulator/blob/fbb7d7ca887a06966ca8a62ed22272409a5ab640/agon-ez80-emulator/src/agon_machine.rs
