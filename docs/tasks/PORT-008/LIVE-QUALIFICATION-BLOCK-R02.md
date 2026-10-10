# PORT-008 LC03-B — First physical block attempt

The first one-byte Agon-to-P4 case failed with EMOS status35
(`EMOS_UNAVAILABLE`) after604 nominal120Hz MOS ticks, approximately5.03seconds.
The P4 received its control request but recorded no completed probe receipt.
The other19 cases did not run. Input was recovered by a separate Agon reset;
startup and installed firmware are unchanged. LC03-B and F03 remain open.
[Receipt and artifact hashes](LIVE-QUALIFICATION-BLOCK-R02.json) preserve the
run, saved Agon CSV and recovery. Pause before further instrumentation or tests.

## Observations and limits

| Check | Observation | Interpretation |
|---|---|---|
| Raw USB capture | Existing POSIX raw method, no modem-control ioctls, `HUPCL` cleared; keyboard epoch unchanged on opening and recovery close | Avoided the previous capture-associated reset in this attempt |
| Boot release/input | Passed after one initial Agon reset with capture held open | Permitted fixture setup and invocation |
| First case | Agon→P4,1byte; service35, guards intact, pattern check failed | Failed operation; no completed payload qualification |
| P4 control observations | Version2 operations1,3,2; no completed probe receipt | Request reached P4; does not prove acknowledgement reached EMOS or native payload ran |
| Remaining cases | 19 not run | MOSlet stopped on first failure; no reverse-direction evidence |
| Recovery | One separate Agon reset, no block replay; CSV retrieved through listener | Input ready/neutral, held0/pending0; listener subsequently stopped |
| Startup/firmware | Original startup read back exactly; no flash or startup change | Installation identity remains the prior verified pair |

The CSV descriptor is `455802027d0c397701000100000038b6`. An intact guard
region does not prove that the transmitted byte arrived. Current logs cannot
separate offer acknowledgement, handover, native payload and reciprocal return.
The roughly5second delay is a clue, not proof of a particular timeout owner.
No PARLIO/DMA, clock or VALID-edge defect is established by this run.

## Timing scopes

| Scope | Measurement | Limit |
|---|---|---|
| Failed service call | 604 MOS ticks ≈5.03seconds | Nominal120Hz, uncalibrated; includes failure waiting, not useful throughput |
| Complete MOSlet attempt | 720 MOS ticks ≈6seconds | One failed case, not20cases |
| Host runner | 147.23seconds | Capture/setup, invocation and bounded120second listener wait; not link timing |
| Recovery/retrieval | Separate operation; no retained duration | Do not infer duration from fixture or host runner |

The MOSlet's nonzero return aborted the batch before its follow-on listener
command. The host's listener-readiness timeout is therefore a downstream symptom,
not the original transfer failure. The host did not automatically retry or reset.
A deliberate later reset was used only to regain input and retrieve the result.

## Capture control and recovery

The prior [preflight](LIVE-QUALIFICATION-BLOCK-R01.json) logged a fresh P4 ROM
boot after capture opening, then stalled release. Pyserial opening still updates
DTR/RTS when initialized false; closing can also affect modem state with `HUPCL`.
The exact triggering edge was not isolated. Reuse of the existing raw POSIX
collector avoided those ioctls and kept capture open throughout this attempt.
No P4 reboot or fatal backtrace was observed in the raw capture.

The `boot` field of `/keyboard/status` is a keyboard transport epoch. The ignored
runner calls it `capture_open_same_P4_boot`; interpret that frozen key as an
unchanged input epoch, not an independent physical-boot measurement. The older
ROM log's saved idle PC and pre-existing core dump do not establish a new crash.

EMOS intentionally fences shared pins and withdraws Extender input after an
uncertain transaction. Current boot reconnection requires foreground startup;
no timed UART fallback was added. Recovery reset only the Agon, retained the P4
collector, started the existing listener, read the CSV, verified original startup,
and stopped the listener. Input remained ready/neutral after closing capture.
Mainboard Pingo VDP was untouched; no prior-firmware backup was taken.

The SD result is `/agents/extender/results/P8R01.CSV`; its retained batch is
`/extender/install/p8run01.txt`. Both were absent before this run. The exact
MOSlet was verified at `/emos/parprobe.bin`. No application assets were changed.
The batch is not an instruction to overwrite or replay the existing result.

## Next review boundary

LC03-B remains incomplete. Before another physical block, propose bounded
observations identifying the last successful phase and failure owner on P4 and
EMOS. Prefer existing USB tracing, host tools and the diagnostic MOSlet; private
EMOS has only88 ROM bytes free. Reuse the one-byte case before returning to the
20-case suite. No new instrumentation, retry, firmware change or broader reset
qualification is authorized by this result document itself.
