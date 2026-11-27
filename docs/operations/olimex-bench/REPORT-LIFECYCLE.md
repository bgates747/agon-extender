# Attempt-bound fixture reports

Status: offline candidate. The shared Olimex checkout and existing job packets
retain their currently commissioned behavior. Use this guide to prepare a
separately reviewed pilot packet.

Each arm writes its declared reports to fixed filenames on the SD card.
The Pi gives every invocation an attempt ID, checks those paths for vacancies,
and archives the report bytes and verdict before cleanup. The operator can
resume interrupted collection without invoking the workload again.

## Author a packet

Use a normal schema-3 named job with production EMOS, P4 and mainboard
firmware and mirrored MOS command output. Declare a `report_lifecycle` object:

| Field | Value |
| --- | --- |
| `project`, `fixture` | Lowercase names with letters, digits and hyphens. Start with a letter and use at most 24 characters each. |
| `mode` | `token-v1` for new producers. `legacy` for a reviewed single-writer fixture with an unchanged existing report format. |
| `firmware` | `native_vdp_sha256`, `p4_app_sha256`, and `emos_rom_sha256` from the approved installed images. The local inventory must point to matching boot-ready verification receipts. |

Each arm's working directory is `/test/<project>/<fixture>/<arm>`. List each
absolute result path in the existing `results` array. The result must be in
that directory, have an ASCII 8.3 basename, and fit the 120-byte path and
32 MiB staged-read limits. Names are checked case-insensitively on FAT.
Programs and staged inputs use the usual 112-byte upload path limit. Put
`report_validator` in each arm. It uses the same `path`, `bytes` and
`sha256` fields as the executable pin.

The job-local validator takes four arguments in order: the archived local
file, the local `report-run.json`, the absolute SD path and the attempt ID.
It emits one JSON object with boolean `accepted` and a nonempty string
`reason`, then exits zero. Return a rejected verdict for semantic failures
such as a clipped timing row. Treat exit failures, timeouts or malformed
verdicts as validation infrastructure failures. The Pi preserves the bytes
and leaves the SD copy in place. Keep the validator local and read-only.
It can use the command-correlated serial lines in `report-run.json` to
compare workload counters with the decoded payload.

## Fixture protocol

The runner sends `RUN &<address> <attempt>` in `token-v1` mode. The token
is 16 lowercase hexadecimal characters. Reject a missing or invalid token
before the workload. After timing has ended, create each report at its
declared path with `FA_CREATE_NEW | FA_WRITE`. Begin the report with ASCII
`OLXR1 <attempt>` and one LF, then write the format's payload. Parse the
original payload after the 23-byte envelope.

Emit exactly one status line per output before the fixture's existing final
success marker or failure line:

```text
OLXR1 <attempt> <basename> <expected> <actual> <stage> <error> <close-error>
```

Byte counts are decimal and include the envelope. Stages are `saved`,
`open`, `write`, `short`, and `close`. The two error fields carry raw
MOS FatFS result codes in decimal. The helper returns `saved` only when
the entire count was written and close returned zero. A workload failure
can still save a report. Emit the workload verdict independently.
A failed write or close leaves the SD copy for disposition.

The [AgonDev fixture example](../../../examples/olimex-report/README.md)
shows the writer, the small ADL wrapper that preserves the MOS write status,
and a host validator. The helper makes no changes to the MOS image.

Legacy mode passes no argument and requires one successful, command-correlated
invocation, the fresh-path check and uninterrupted custody and boot continuity.
Its save status is unreported. Record which provenance mode the job uses.
Continue to use existing instructions for human-start jobs and native UART
listener-handoff fixtures.

## Operate and recover

Use the ordinary supervisor, startup and checkout procedure. The commissioned
local config must name the scheduler's authoritative absolute state path as
`report_lease_state`. The runner binds the active operator and exact snapshot
to the job, including the underlying file revision. If the scheduler rewrites
a snapshot without a distinct lease generation, the runner conservatively
retains the file and requires reconciliation even if the active name is the
same. Apply the same operation lock across stage, run, collection and cleanup.

Use a new Pi evidence root for each new attempt. For a repeat of the exact
packet with continuous custody, firmware and both boot identities, pass
`--reuse-stage /absolute/original-evidence-root` to every phase. The original
stage must have joined successfully and contain the original upload receipts.
The runner matches the recorded uploads to the local pins and verifies the
destination file type and size with metadata only. Use the ordinary stop rule
if the known custody or data changed. No payload readback or repeat upload is
part of reuse.

After an authorized, joined failure during collection or cleanup, keep the
same job, config, evidence root, operator and any original reuse argument.
Use `resume-run-<arm>-01`, then the next two-digit number for a subsequent
approved recovery. The resume requires the original command-correlated MOS
return and attempt journal. It issues no `LOAD` or `RUN`. It does not
admit a different operator, a live worker, a started successor, an unknown
online listener, or a changed baseline. An already retained P4 transfer is
resumed by its own journal. A changed boot can permit archival of a tokened
report under the same lease and firmware when the transfer is recoverable.
The runner leaves the SD copy in place after a boot change. A lost staged
job that the P4 cannot reconcile remains a blocker for the operator to review.

The evidence root records the original supervisor result, attempt and
command-correlated output. Each `report-NN` directory contains the archived
file, local SHA-256, transfer receipt, validation verdict and, when applicable,
exact delete intent and completion. A rejected report can be cleaned only
when its exact identity, bytes and rejection reason are durably recorded.
If a delete acknowledgement is lost, recovery can confirm the file is absent.
If it is still present, the approved resume fetches that one report for
comparison before attempting removal. Other transfers remain checksum-free
and have no readbacks. Stale or unidentified files remain on SD. Use the
ordinary handback procedure after verification.
