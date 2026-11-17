# BENCH-019 cold rehearsal r02

Use the [r03 draft](PROCEDURE-DRAFT-R03.md) and the following job inputs. The
synthetic workload repeats the three diagnostics with the same firmware and
fixture bytes as r01. The new operator phases and the observation path are the
parts under test. The regular FIFO test is deferred to real jobs.

| Input | Path or value |
| --- | --- |
| Job manifest | `agents/bench019/rehearsal-r02/job.json` |
| Manifest SHA-256 | `14f14d44f7993f0d4cd84bd50a82542f2f7acfe93b16466c781e466b03ff386c` |
| Commissioned Pi5 binding | `agents/bench019/rehearsal-r02/bench.local.json` |
| New evidence directory | `agents/bench019/rehearsal-r02/operator-run` |
| Operator log | `agents/bench019/rehearsal-r02/OPERATOR-LOG.md` |
| Expected result | EMOS command accept/reject, fresh VDPlet screen-character reply and both P4 probe inputs pass. Restore and independently verify all three production images. |

Use the draft's single chat request and wait for its separate slot-open
message before hardware access. Normal check-in follows the final parent
receipt. A failed command or ambiguous bench state invokes the draft's
stop rule. The operator records the last actual action and sends Smith
the question alert in the operator chat. The standard flash order applies
to this fixture even though other jobs may only change one processor.

Before the slot opens, use this host-only plan preview:

```bash
.venv/bin/python scripts/olimex_bench.py \
  --job agents/bench019/rehearsal-r02/job.json \
  --sha256 14f14d44f7993f0d4cd84bd50a82542f2f7acfe93b16466c781e466b03ff386c preflight
```

After the slot opens, use the draft's phase command with the same manifest,
hash, config and new evidence directory, once per phase in the printed order.
Copy the exact commands into the durable log. Record every tool, skill, search
and resulting file read, as well as timings, first failures and check-in.
The fixture itself writes the same task-specific SD result path as r01. Staging
preserves a prior result in the new host evidence directory before clearing
that path. ROM verification uses a new task-specific SD namespace.
