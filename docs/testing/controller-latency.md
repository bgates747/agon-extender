# Controller latency investigation

The deterministic Linux source removes USB polling and hand movement from a
controller test. It measures when the host intended to send, when it actually
sent, and when the host received each P4 acknowledgement. These measurements
locate host/network delays; they do not establish EMOS delivery or visible
screen latency. The tools are experimental and require an explicitly available
controller service. [INPUT-002](../tasks/INPUT-002.md) owns the investigation.

## Finite individual and background runs

Use the current host's project Python environment. `$EXTENDER_URL` is the
commissioned P4 HTTP origin from the machine-local bench record; `$RUN_DIR` must
be a new evidence directory. These commands do not discover/replace firmware,
type Agon commands, touch the SD card or change normal startup.

```sh
.venv/bin/python scripts/controller_probe.py --url "$EXTENDER_URL" \
  --output "$RUN_DIR" --hz 120 --seconds 30 --pattern triangle
```

The source first checks controller status, then asks P4 to admit its UDP socket.
An existing active source causes a failure; the source never takes over, retries
admission, reconnects or restarts automatically. The P4 receiver also arbitrates
admission if two hosts race after a status observation. The finite source uses
the existing protocol and sends axes only. No retained button queue can fill
while an Agon consumer is absent. The physical F310 and Linux input state are
not opened or changed.

For a background process, run from the prepared package directory:

```sh
nohup .venv/bin/python scripts/controller_probe.py --url "$EXTENDER_URL" \
  --output "$RUN_DIR" --hz 120 --seconds 30 --pattern triangle \
  >"${RUN_DIR}.log" 2>&1 </dev/null &
probe_pid=$!
```

The process ends after the requested duration plus bounded admission/ACK-drain/
close work. SIGINT or SIGTERM requests cancellation and closes its admitted
session. Before signalling a saved PID later, verify that it still names this
command and run directory; a PID can be reused. This is an explicitly started
process, not a boot service. Do not leave it running over another user's session.
If close cannot be confirmed, the source reports the failure and P4's existing
freshness timeout remains the fallback. The source never resets either board.

## Comparable rate campaign

The Python coordinator invokes the same individual source for each rate:

```sh
.venv/bin/python scripts/controller_probe_campaign.py --url "$EXTENDER_URL" \
  --output "$RUN_DIR" --rates 120 60 240 --seconds 30
```

Each case gets its own admission, explicit close and evidence directory. A
failed, partial or cancelled case stops further dispatch. The coordinator never
replays an uncertain case. A 30-second three-rate campaign contains 90 seconds
of source traffic; HTTP setup/close and final ACK draining are additional.
Advance estimates should use retained comparable campaigns on the same host.
No Agon application or monitor mode is changed by this coordinator.

## Evidence and interpretation

| File / value | Scope |
|---|---|
| `run.json` | UTC start, host/PID/Python, source hashes, rate/pattern/timeout and local clock resolution; resolution is not calibration accuracy |
| `events.jsonl` | Intended deadline, scheduled slot, actual pre-send/post-send times, raw eight-bit axes, packet sequence and post-receive ACK times, close and failure records |
| `summary.json` | Durable end time and durations; sent/unique ACK/missing counts; effective rate; min/median/p95/max timing in milliseconds |
| `campaign.json` | Coordinator start/end duration and outcomes of the cases actually dispatched |
| Send lateness | Actual pre-send minus intended deadline; includes host scheduling and source preparation |
| ACK round trip | Host pre-send to host post-receive; includes socket/network/P4 turnaround and host receive scheduling |

The schedule is anchored to the run's monotonic start. Missed slots are skipped,
including slots crossed during encoding/transmission; the source does not replay
old slots in a burst. Pattern values come from the scheduled slot. UDP sequence
numbers count actual sends, so skipped deadlines and lost packets remain distinct.
`step` switches every half second; `triangle` takes one second across the range
and a second back. All axes use the existing reversible raw8 encoding.

Logs are buffered during measurement and fsynced at close. Logging overhead is
part of the host workload, and an abrupt host/power failure may lose buffered
records. An incomplete run without its terminal summary is not a pass. Retain
the source package used for a run; later edits do not rename its evidence.

The local socket control is explicitly separate:

```sh
.venv/bin/python tests/run_controller_probe_loopback.py \
  --output "$RUN_DIR" --rates 60 120 240 --seconds 30
```

Its Python HTTP/UDP reflector tests scheduling and instrumentation on that host.
It does not model P4 firmware timing and sends no traffic to P4 or Agon. Do not
report its round trips as LAN or game latency.

## Clock alignment without clock adjustment

Current controller ACKs have no P4 timestamps. Their packet identities support
round-trip correlation only. Neither HTTP status sampling nor half an ACK round
trip proves one-way delay. No clock synchronization has yet been demonstrated.

`scripts/controller_clock.py` implements offline conservative bounds for future
four-timestamp probes. Input is a JSON list of integer-nanosecond rows:
`[host_send, peer_receive, peer_send, host_receive]`, with native counter units
converted before analysis. The operator must supply per-clock timestamp errors
and a maximum drift prior. For example, on synthetic or subsequently collected
data, with explicitly justified error/prior values:

```sh
.venv/bin/python scripts/controller_clock.py exchanges.json \
  --error-a-ns 1000 --error-b-ns 1000 --max-drift-ppm 1000
```

The example numbers are assumptions, not measured accuracy. The analyzer bounds
an affine mapping between monotonic clocks using nonnegative forward/reverse
delays and every exchange's send/receive ordering. It permits asymmetric paths,
retains offset and drift uncertainty, and rejects incompatible exchanges or
unhandled wrap/reset. Its bounds are conditional on the stated timestamp errors,
drift prior and affine model; they are not statistical confidence intervals.
No participant's clock is set. Chained mappings must include both uncertainties.

P4 timestamp instrumentation and the eZ80 fine timer remain separate preparation
gates. The nominal MOS clock advances two units per physical VBlank and is too
coarse to attribute millisecond delays. PRT1 can provide finer bounded intervals,
subject to the [timer ownership/wrap rules](game-timing.md); PRT0 belongs to MOS/
AgonDev. An application-owned timer and existing EMOS gateway are preferable to
unplanned resident growth. Do not silently extend existing controller packets.
