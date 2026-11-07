# Optional message accounting reader

The P4 can expose local message counters to locate work and waiting in a later
matched diagnostic run. They measure inclusive elapsed time, including
preemption and recorder overhead. They do not measure exclusive CPU use. The
option defaults OFF and is limited to the existing UART message composition.
Enabling it is a new experimental firmware build, not a runtime switch.

The P4 HTTP task serves read-only `GET /diagnostics/nm-accounting` with no-store
caching only when built with `--network-messages --nm-accounting`. There is no
reset, clear or start endpoint. No software checksum or wire field is added.
The P4 console retains UART ownership and the message worker retains socket and
peer ownership. This observer does not acquire either transport.

The response identifies `p4-nm-accounting-r01`, full local ESP Timer microseconds,
first event epoch, snapshot time and explicit non-additive/CPU/CTS/quiescence
limits. The reader copies the fixed recorder under one private critical section,
then formats outside it. Existing mailbox code can acquire recorder after its
own lock; the recorder and HTTP reader never acquire a mailbox, driver or socket
lock. A new P4 boot starts a new epoch; retained samples must also identify the
exact build and boot. No HTTP call creates a message measurement event.

| Row | Actor | Counted units | Meaning of inclusive interval |
|---|---|---|---|
| submit | P4 console | Accepted NM body bytes | One mailbox admission call, including rejected calls |
| take_reply | P4 console | Retrieved reply body bytes | One take call, including empty polls |
| queue_wait | P4 message worker | Dequeued NM body bytes | Accepted mailbox submission to worker dequeue |
| work_complete_attempt | P4 message worker | Candidate reply bytes | Attempt to retain a result; generation replacement may discard it |
| peer_request | P4 message worker | Produced reply body bytes | Entire peer request call, including nested socket operations |
| peer_tick | P4 message worker | None | One peer tick call, including nested socket operations |
| socket_read/write | P4 message worker | Actual progress bytes | One nonblocking socket operation |
| tx_enqueue | P4 shared UART console | Accepted UART bytes | One UART batch enqueue call |
| tx_idle_poll | P4 shared UART console | None | One nonblocking TX-idle query, not duration of wire occupancy |

Each row exports completed calls, units, outcome counts, inclusive sum/max in
microseconds, sampled highwater and currently active scopes. Socket WouldBlock,
EOF/Closed and Error are distinct; no failed bytes are counted as progress.
Highwater is the largest sampled body/backlog byte count at that observation
point, not a full FIFO or queue occupancy history. The UART rows also include
keyboard, SD and other console traffic, so they are not exclusively NM traffic.

Unsigned totals saturate and set `saturated`. Backwards elapsed intervals set
`clock_invalid`; mismatched scope completion sets `lifecycle_invalid`. These
flags persist for the boot. A sample with any flag is not silently accepted as
an ordinary timing result. Subtract only unsaturated, coherent samples from the
same boot/build. Elapsed sums include completed scopes, so a scope crossing a
sample boundary contributes its full duration when it completes. Active counts
make that limit visible; zero active scopes alone does not prove application or
transport quiescence. Overlapping row sums must never be added to derive CPU or
whole-request latency. The 64-bit diagnostic clock does not alter protocol
32-bit millisecond deadlines or their wrap behavior.

A later comparison needs independent workload start/end and positive transport
retirement evidence, identified OFF/ON builds and matching payload/results.
Physical CTS/STOP tail, IRQ blackout, task CPU utilization and complete wire
transfer latency remain outside this reader's observations. Frequent HTTP reads
and enabled accounting perturb scheduling; reader activity must be declared.
