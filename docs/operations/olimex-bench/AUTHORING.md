# Prepare an Olimex test job

The [temporary Olimex restrictions](README.md) apply to all job preparation.
Use the named schema-3 UART route below while the transfer restriction is in
force. Mainboard firmware changes require the FLASH utility while the
flashing restriction is in force.

Create the fixture and check the job packet before asking for bench time.
The [Olimex bench procedure](README.md) governs physical checkout and handback.

The commissioning owner supplies the operator chat UUID, the full checkout
commit, a job-local evidence directory, the commissioning chat UUID, and the
exact phase commands alongside the job manifest. The operator follows the
guide's host-only readiness command and fixed Pi sender before reservation.
The initial dispatch names the durable operator log path before the operator
begins reading or executing commands. Precreate that directory and log. If
the app assigns the chat UUID only at creation, supply it in a follow-up while
the operator records its initial reading in that already-named log.
For a cold run, each logged action names its guide section or job command.
The owner records hardware outcome and instruction completeness separately
when reviewing the run.

1. Define the behavior under test, the expected result, the required
   processor and display mode, and what ends the run. State who invokes the
   test, what the operator may observe, and which firmware must be restored.
   Write expected results from the test contract before collecting outputs.
2. Follow the [appliance lifecycle](../../procedures/test-appliances.md) for
   mode changes, settling time and cleanup. Read the
   [bench constraints](../../qualification/bench-constraints.md) before
   preparing an eZ80 fixture. Use the [SD layout](../../sd-layout.md) for
   files and [test execution](../../procedures/test-execution.md) for staging,
   invocation and collection. Keep startup intact and give each fixture an
   explicit CLI invocation. For suites that require an unattended host
   supervisor, see [host process evidence](../../procedures/bench-completion.md).
3. Build the fixture with the toolchain maintained by its project. For an
   AgonDev C program, the example below shows the build and result contract.
   Use the project's matching MOS/VDP interfaces and retain the exact build
   inputs beside the artifact. The full Extender checkout's
   `docs/building.md` covers component firmware builds. When a job changes
   firmware, obtain candidate and production restore files from the component
   owner and follow the write extents in the bench procedure.
4. Assemble the job packet. Include the manifest and its SHA-256, the
   commissioned local bench config, the operator instructions, and an
   evidence directory for this run. Record the program load address from
   the executable's build contract. Pin each input file by path, byte count
   and SHA-256 for local artifact identity. Follow the bench procedure's
   [staging policy](README.md#stage-the-fixtures) for the actual transfer.
   For routine jobs omit `schema` or set it to `3`. During the UART rule,
   use named entries in `fixtures` and set `"transfer": "uart"`.
   The default PARLIO path applies when the bench procedure admits it.
   Use a fresh SD namespace. For additional files, add an `inputs` array
   under `fixture`, with an `sd_path` and a pinned `source` for each file.
   Obtain the startup and listener hashes from the commissioned bench record.
   For a production-only job, use an empty `firmware` object.
   For a custom job, supply only the changed components:
   - For `emos`, provide `candidate_write` and `restore_write`, each a
     complete 128 KiB ROM.
   - For `mainboard`, use [the FLASH manifest](#mainboard-flash-jobs).
   - For `p4` or an admitted mainboard USB job, provide `offset`, `partition_bytes`,
     `write_bytes`, `partition_table`, and the `candidate_app`,
     `restore_app`, `candidate_write` and `restore_write` pins.
     The owner supplies the commissioned layout and write extent. Each
     write file contains its application padded to that extent with `0xff`.
5. Run the bench runner's offline `preflight` from the checkout root.
   Confirm that it lists the expected phases. Check the staging command
   against the transfer policy separately. Preflight checks local job inputs
   and phase selection. Preserve the manifest hash with the job. For a job
   reserved for the Author to invoke, the packet
   supplies the exact command and uses the bench guide's staging boundary.

## Worked example

The [C fixture](example/src/main.c) writes one ASCII result file and prints a
completion marker at the Legacy CLI. It uses the active mode and changes no
display settings. The bench runner observes the marker and the return of the
prompt, then compares every result line in order. A real fixture replaces
the sample assertion with the behavior it is meant to check.

From the checkout root, build with the installed AgonDev toolchain:

```bash
make -C docs/operations/olimex-bench/example AGONDEV_TOOLCHAIN=/path/to/agondev
```

Without that override, the Makefile uses `agondev-config --prefix` from
the operator's PATH. Copy the resulting `bin/OLIMT2.bin` into the job
directory. Copy [job.example.json](example/job.example.json) to a new job
manifest, fill in the local artifact path and the two commissioned SD
identity hashes, and replace the example artifact size and hash with
`wc -c` and `sha256sum` results. The example uses `040000` and places
the fixture and result under `/test/olimex-authoring`. Keep the result path
in the C source and the manifest in sync.

```bash
sha256sum path/to/job.json
.venv/bin/python scripts/olimex_bench.py --job path/to/job.json \
  --sha256 JOB_SHA256 --config BENCH.local.json preflight
```

The production-only example yields `stage`, `run` and `handback`.
The example documents the default PARLIO path for when it is admitted.
Use the named-fixture contract below for UART. Stage sends the program once.
Run retrieves the result once and checks the expected output.

## Prepare a paired job with dynamic results

For a schema 3 job with several arms, replace the single `fixture` object
with an ordered `fixtures` array. Give each entry a distinct `id` such as
`full` or `ground` and an absolute `cwd` under `/test`. Keep the program,
inputs and reports inside that arm's directory. Use the same `agon`,
`sd_program`, `inputs`, `address`, `seconds`, `success` and `failure`
fields as a single fixture. Supply `results` as a list of absolute SD paths
for the generated reports in that directory in collection order. The runner
requires a nonempty result at each path. The job packet supplies its own
analysis of the report contents.

For an arm with native UART output that may outlast the application, include
`"uart_end": {"prefix": "PNT ", "line": "PNT end retained=128", "seconds": 30}`
with the fixture's actual diagnostic prefix, complete terminator line and
maximum wait after application return. For timing firmware that shares USB
UART with MOS's printer mirror, the PARLIO route supports a
`listener_handoff` object with a
fresh `sd_path` under the arm's directory and a pinned `source` for this
two-line MOS batch, with CRLF line endings and the job's load address:

```text
RUN &040000
EMOS sdserve --fast --parallel /
```

Stage uploads the batch with the fixture. Run checks the CLI and loads the
program, disables the mirror, and submits one explicit `EXEC` of the batch.
MOS starts the listener after a successful RUN. The runner requires the
listener to come online within the application bound. It keeps its passive
reader open and requires the complete native terminator within the additional
UART window. Either signal can arrive first. The runner collects the reports
through that listener, exits it, verifies a fresh MOS prompt with the mirror,
and restores the entry directory.

Preflight prints `stage`, any shared firmware installs, one `run-ID` phase
per arm, any required restores, and `handback`. Run those phases in order.
Each arm's results and UART transcript are in `RUN_EVIDENCE/run-ID/results/`.
The transcript is named `vdp-usb.bin`. Generated reports retain their SD
filenames. The phase directory also holds the separate transfer receipts
and the parent process's completion record.

## Prepare a human-start job

Use schema 3, one named entry in `fixtures`, and the normal `firmware`,
`namespace` and `preserve` fields. Set top-level `human_start` to
`stage-only` if Smith will load and run the fixture, or `preload` if
Smith will run an already loaded fixture. Include the usual `id`, `cwd`,
`agon` file pin, `sd_program`, six-digit `address`, optional `inputs`,
and `"results": []`. Omit automatic RUN markers, time bounds, listener
handoff and UART terminators. In the packet give Smith the literal MOS
commands, including the working directory for assets. The human observation
and return to MOS belong in operator chat.

With `preload`, the operator's worker enters the named directory and
requires the LOAD echo and returned prompt. The receipt names the prompt,
program and address. For `stage-only`, the packet can call the optional
`enter-cwd` phase after preparation. Reuse the same manifest, config and
evidence directory. The phase enters the manifest's `cwd`, witnesses the
returned prompt, and joins. Smith then types the packet's LOAD and RUN
commands. The default `stage-only` preflight still lists the ordinary
preparation, restore, and handback phases.

## Check observer and flash dependencies

Use the actual worker interpreter and supply the commissioned config to
offline preflight. Mainboard app0 and P4 jobs both use standalone esptool
5.1.0 from the runner's interpreter for programming and paired startup.
A manifest-only preflight without the config checks the packet and lists
phases. When an
existing adapter uses these operations, call `runtime_preflight(kit, config)`
from its own worker interpreter before it touches a device.

Pass each repeated `Bench.cli(label)` observation a distinct label such as
`before-restart` and `after-restart`. The default for a single observation is
`cli`. The observer accepts printable ASCII text or bytes for RUN markers.
A refused keyboard admission writes the status sample to
`keyboard-refused-*.json` in the phase directory.

## Refresh the operator checkout

The [sparse paths](sparse-paths.txt) select these guides, the example,
the project reviewer configuration, and the commissioned runner and its local
dependencies. The reviewer configuration authorizes operators to return
routine result summaries and evidence references to the commissioning
Extender chat. The full Extender
checkout has the broader operation index and the historical references
linked from some of the guides.

Between jobs, fast-forward the sparse checkout from its configured local
Extender remote. Reapply the selection if the path list changed:

```bash
git pull --ff-only
git sparse-checkout set --no-cone --stdin < docs/operations/olimex-bench/sparse-paths.txt
```

Use the local interpreter and commissioned configuration recorded for that
host. The bench procedure links directly to the component owners' retained
restore files. The local Olimex v0.3.0 runtime is under
`dist/production/olimex-parlio-v0.3.0/runtime/`.

## Mainboard FLASH jobs

Use schema 3 and named, automated fixtures. Set the top-level
`"transfer": "uart"`. The Pi starts `EMOS sdserve --fast /` and submits
whole files to the existing P4 staging worker. P4 exchanges checksum-free
UART records with the foreground EMOS listener. The Pi retrieves complete
reports from P4 after the fixture returns to MOS. The staged client rejects
parallel listener capabilities before submitting any file and records
the carrier in the completion receipt. Empty files use control records
only. Omit `listener_handoff`.

For a mainboard-only FLASH job, set these fields under `firmware.mainboard`.

| Field | Value |
| --- | --- |
| `method` | `agon-flash` |
| `candidate_app`, `restore_app` | Raw ESP32 applications, each with `path`, `bytes` and `sha256` |
| `partition_table` | Commissioned raw partition table with `path`, `bytes` and `sha256` |
| `candidate_slot`, `restore_slot` | Distinct integers, 0 and 1, in the required order |

Use the normal runner preflight and configuration. Include evidence from
checkout that the currently selected production app matches `restore_slot`
and `restore_app`. An unresolved current image blocks the job. Stage both
apps and the fixture files. Run `install-mainboard`, the named arms in
manifest order, `restore-mainboard` and `handback`.

The Pi checks the installed FLASH v1.9 utility over UART and witnesses its
confirmation prompt before sending one `y`. It requires the checksum and
reboot messages. After each write it reads the partition table, OTA selector
and selected application's exact bytes in one bounded USB programmer session
at 115,200 baud. The Pi closes that session, restarts Agon and proves MOS is
responsive before publishing the installed identity. The job must explicitly
cover those independent reads and restarts. Stop and retain custody on the
first unexpected failure according to the bench procedure.

The UART staging supervisor allows 300 seconds of setup plus 60 seconds per
file and a transfer allowance at 8,000 B/s, rounded up per file. Treat this
as a watchdog. Set the Pi service runtime longer than the supervisor's bound
so it can preserve failure evidence and wake the operator.
