# Performance core and collector — offline r01

This dedicated source generates identical byte workloads and validates explicit
timer intervals. `scripts/comms_performance_report.py` analyses only dedicated
matched performance records. It does not accept accuracy journal records and
does not implement fault injection, retries or an endurance schedule.

1. `core.hpp` generates sink bytes, short colour commands, medium plot batches
   and standard VDU buffer clear/write streams. A later appliance must actually
   own its buffer ID, target route and parser completion; generation alone does
   not reserve resources or execute VDU commands.
2. Timer arithmetic requires counter width and an independently established
   upper interval bound below half the wrap period. Zero/sub-tick and ambiguous
   intervals are refused; a native caller must supply an atomic timer sample.
3. Samples use schema `comms-performance-sample-r01`; each names `pair`, `case`,
   `arm` (`uart1` or `parallel`), `scope`, `observer`, `clock`, `clock_hz`,
   `timer_bits`, `start`, `end`, `upper_bound_counts`, `passed`,
   `workload_sha256`, `renderer_sha256`, `logical_configuration_sha256`,
   `ez80_hz`, `p4_hz`, `iterations` and `bytes_per_iteration`.
4. Every pair must contain exactly one arm of each kind with equal logical
   identities/rates. Failed, missing, duplicated, differently configured or
   truncated samples refuse a clean speed report. All rows of one case label
   must retain the same scope/identity, including batch size.
5. The collector produces separate scope/observer/clock rows and explicit
   UART1 baseline changes. It never adds overlapped scopes or invents CPU
   utilisation. Its table ranks the longest UART1 median batch first and states
   milliseconds per batch; divide by the declared iteration count only when
   that interpretation fits the chosen workload.
6. `selfcheck.cpp` proves stopped eZ80 compilation/link syntax only. No timing,
   hardware invocation or speed result follows from running host unit tests.

The [task](../../../docs/tasks/COMMS-002.md) owns actual API/timer/firmware binding
and the later finite matched hardware comparison.
