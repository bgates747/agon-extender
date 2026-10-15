# Pi scrolling-suite coordinator

The Pi coordinator sequences the existing individual scrolling cases while
preserving normal startup and recording durable completion evidence. Host
simulation and eZ80 compilation are available offline. No live adapter has been
qualified for this coordinator; generated plans are stopped and not ready to
execute. Physical validation and deployment remain separate authorized work.

The [test appliance lifecycle](../procedures/test-appliances.md) owns behavior;
[SCROLL-001](../tasks/SCROLL-001.md) records implementation and validation limits.

## Offline preparation

Build a fresh `pattern-scroll-r03` package with
`tests/fixtures/scroll/build.py`. Generate the initial16-job plan, one invocation
per direction/region on each display, using local output paths:

```sh
.venv/bin/python scripts/run_scroll_suite.py \
  --fixture-manifest "$FIXTURE_BUILD/manifest.json" --write-plan "$SUITE_PLAN"
.venv/bin/python scripts/run_scroll_suite.py --plan "$SUITE_PLAN" --check
```

These commands read local package bytes and write/check the plan only. Neither
invokes an adapter. The generated plan has `ready: false`, an unqualified empty
adapter and a placeholder bench-lock path. Checking schema/hashes does not
qualify hardware or make the plan ready. Generated plans/receipts remain in
ignored local records, where private adapter addresses and device identities
may be configured later. No private configuration belongs in tracked examples.

The manifest pins the executable, configuration, patterns and launchers.
Configuration fields must match the manifest, including mode and colour count.
Job IDs become unique result labels, preserving earlier outputs. The application
still refuses to overwrite an existing result. The normal single-case and batch
launchers remain available for Author-controlled interactive testing.

## Coordinator behavior

1. `scripts/run_scroll_suite.py` requires an explicitly ready plan and a qualified,
   hash-pinned adapter before execution. A nonblocking Pi bench lock excludes
   another coordinator using the commissioned lock. The adapter must also honor
   the actual bench reservation; this local lock does not establish cross-project
   permission or replace an operator handoff.
2. Before each test, the coordinator obtains fresh mode/route and resident
   foreground receipts. It sends EMOS route selection if needed, then
   `VDU 22 n` only when necessary. It waits at least one monotonic second after
   a confirmed mode change, including early sleep returns, and rechecks state
   before invoking the test.
3. The coordinator invokes the same individual appliance with explicit MOS
   `CD`, `LOAD` and `RUN &040000 <case> <job-id>` commands. The appliance's own
   conditional mode check avoids a duplicate switch after host preselection.
4. Request intent is saved before each adapter operation. Replies bind schema,
   run UUID, sequence and action. Peer boot identities and read-only startup
   identity must remain unchanged. A timeout, reset, uncertain result or mismatched
   receipt stops dispatch without replay, automatic reset or further CLI input.
5. For a verified return to a visible CLI, the coordinator restores modes it
   changed before invocation, and the original EMOS route. It requests persistent
   completion/failure cues on both displays, preserving restored state. An unsafe
   or unknown return suppresses those additional hardware actions.
6. The coordinator independently hashes and parses the retrieved CSV. A PASS
   needs the expected target, case, mode, geometry, configuration, update count,
   complete metric sequence, classified call counts, no boundary crossings and
   a valid durable suite duration. An adapter exit code or claimed pass cannot
   substitute for those checks. Failed and partial evidence remains retained.
7. Host elapsed seconds include launch, execution and retrieval. The appliance's
   `SUITE` duration is retained separately in MOS ticks (2/vblank, nominal120/s
   at60Hz); renderer metrics remain local ESP microseconds. Do not call these
   clocks interchangeable, include settling in rendering cost, or add classified
   scroll/bitmap subsets to the total primitive measurement again.
8. There is no coordinator operation for startup edits, SD writes, firmware
   changes, reset or implicit resume. Any later resume is a new explicit request
   after state/evidence reconciliation; the program never restarts an old run
   merely because a process, board or connection returns.

## Live adapter contract — not yet qualified

The Pi starts a reviewed adapter argv without a shell, sends one JSON request
on stdin, and expects exactly one JSON reply on stdout. Diagnostics use stderr.
Each request includes `schema: 1`, `run_id`, `sequence`, `action`,
`timeout_seconds` and action-specific data. The reply echoes those four identity
fields and includes a fresh `snapshot`:

| Field | Required meaning |
|---|---|
| `fresh` | `true`; newly observed, not a stale cross-route cache |
| `epochs` | Nonempty `agon` and `p4` boot identities from authoritative resident lifecycle reports |
| `route` | Committed `mb` or `ext`, owned by EMOS |
| `modes` | Separate fresh `mb` and `ext` objects with `number`, `width`, `height`, `colours` |
| `foreground` | Actual resident CLI/application ownership; a keyboard-ready bit is insufficient |
| `cli_visible` | Verified visible CLI handback, including buffering constraints |
| `startup_sha256` | Read-only hash of unchanged ordinary `/autoexec.txt` |

The initial reply declares all required capabilities: `fresh-mode`,
`resident-foreground`, `peer-boot-identities`, `cli-handback`, `input-pins`,
`readonly-startup`, `completion`, and `persistent-notification`.

| Action | Adapter responsibility |
|---|---|
| `snapshot` | Observe the admitted current state without launching any fixture |
| `select_route` | Execute only the supplied EMOS route command; verify committed route and actual CLI |
| `select_mode` | Execute only the supplied `VDU 22 n`; verify the resulting full mode descriptor |
| `launch` | Verify deployed input pins and unused result path; explicitly invoke the declared job; return `accepted_job` |
| `completion` | Verify actual application return; retrieve raw CSV into the supplied host evidence directory |
| `notify` | Leave persistent cues on both declared displays, return `shown_targets`, preserve modes/route and visible CLI |

A completion reply includes `job_id`, Agon `result` path, `artifact` host path
inside that job's evidence directory, `fixture_sha256`, `config_sha256`,
`inputs_verified`, `result_sha256` and Boolean `validated`. The coordinator checks
the binding and independently validates the actual artifact. The adapter owns
bounded child-process lifetime and must not leave a retrying keyboard/transfer
worker after a timeout. It must never modify startup or silently start a listener,
test, reset or transfer outside the declared reviewed operation.

The current P4 keyboard `boot` field is an admission epoch, not an authoritative
processor boot identity. `/display/status` alone describes P4, not the mainboard
VDP. Do not fill this contract with those convenient but insufficient proxies.
Resident lifecycle/observer integration and physical qualification remain pending;
the coordinator intentionally refuses an unqualified adapter.

## Appliance limits

Revision r03 captures/restores the invoking display's mode and leaves its route
unchanged. Its completion cue stays on that display; whole-suite dual-display
notification belongs to the Pi coordinator, which has saved both displays' state.
Escape cancels measured updates, attempts the normal diagnostic drain and saves
partial results before cleanup. Cleanup failure prevents a PASS result.

The appliance settling delay is160MOS ticks, nominal1.33s at60Hz or1.14s at70Hz,
conservative for the stock refresh rates and outside measurement. Stopped-clock
waits have finite instruction budgets; these are not calibrated wall deadlines.
Hardware timing, visibility and cancellation behavior still require validation.

Double-buffered entry modes are gated. Official stock VDP exposes swapping, but
a final swap does not make subsequent CLI typing visible. The appliance and
coordinator do not silently substitute a return mode or claim that cleanup is
solved. A qualified visible-CLI strategy is required before admitting those
entry modes. This does not add double-buffered scrolling to the first test matrix.
