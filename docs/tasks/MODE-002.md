# MODE-002 — Evaluate automatic mode-request retry protection

## State

- Status: Not started — post-beta regression review; conditional v1 target
- Started: --
- Finished: --

## Current boundary

This is deferred investigation of **cross-boot automatic retry**, not a missing
prerequisite for [current console switching](../protocols/excom-console.md).
Its beta design rules below are requirements to assess when this task resumes,
not claims that a persistent circuit breaker is installed. Current bounded
console failure handling retains the committed route on failed admission.

## Namespace

`MODE` identifies operating-mode lifecycle work as defined by
[MODE-001](MODE-001.md). This task is separated because retry-loop evidence and
retained circuit-breaking state are independent of display-state-preserving
transitions.

## Prompting discussion

This task was created while reviewing
[`REMED-001` Work 2.d, `W2D-Q09` item 6](REMED-001/mode-lifecycle-analysis.md#w2d-q09--prohibited-behavior).
Extender MOS (EMOS) can limit its mode-transition coordinator to one attempt
per explicit request. It cannot prevent `autoexec.txt` from issuing a fresh,
identical request after a full eZ80/MOS reset without retained state or
cooperation from the command that `autoexec.txt` invokes.

Cross-boot circuit breaking is not a beta requirement. It may become a v1
target only if regression testing demonstrates a material unattended retry or
restart-loop risk and the Author accepts a concrete mechanism.

## Beta boundary

1. An operator, application, service, or `autoexec.txt` command submits one
   explicit target request to the EMOS mode-transition coordinator.
2. EMOS makes at most one transition attempt for that request.
3. On pre-commit failure, EMOS reports the failure and leaves or restores
   Legacy without autonomously re-arming the request.
4. Beta does not promise that EMOS will recognize the same command as a repeat
   after a full reset and another `autoexec.txt` execution.
5. Beta transition code should avoid causing a reset on ordinary pre-commit
   failure where EMOS can return safely, but regression evidence—not assumption—
   determines whether cross-boot protection is necessary.

## Regression work

M02-R01 [ ] Exercise automatic mode requests with absent P4 hardware, incompatible EDP
   firmware, unavailable transport wiring, timeout, malformed readiness data,
   P4 reset, eZ80 reset, EMOS reset, and reset during each transaction stage.
M02-R02 [ ] Determine whether any failure path causes `autoexec.txt` to reissue the same
   request indefinitely or creates repeated disruptive transitions despite
   successful Legacy fallback.
M02-R03 [ ] Identify which actor causes each reset or retry: EMOS coordinator, EDP/P4
   firmware, eZ80 watchdog/reset path, physical wiring fault, invoked command,
   or operator action.
M02-R04 [ ] Record whether one-attempt-per-request behavior is sufficient for v1.

## Candidate mechanisms if evidence requires one

1. EMOS volatile per-boot attempt state.
2. An EMOS-owned retained failure/circuit-breaker record consumed before a new
   automatic request.
3. A token or generation supplied by the `autoexec.txt`-invoked command so EMOS
   can distinguish a repeated automatic request from an authorized retry.
4. A user-managed configuration or explicit retry command that clears the
   failed-target latch.

Do not select a mechanism before identifying what survives the relevant reset,
when MOS can access the storage, how writes fail safely, and how the operator
recovers from a stale or corrupt latch. EMOS must not parse `autoexec.txt`
separately merely to infer command intent unless later evidence and review make
that design preferable to an explicit API contract.

## Completion criteria

1. Regression evidence proves whether an unattended cross-boot loop exists.
2. Every observed retry/reset names the responsible processor, firmware,
   command, wiring condition, and retained state.
3. The Author either rejects circuit breaking as unnecessary or accepts a
   bounded v1 mechanism and its storage/recovery contract.
4. Any accepted implementation and qualification work is split into reviewed
   tasks before code changes.
