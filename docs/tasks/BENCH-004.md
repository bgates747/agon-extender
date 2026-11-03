# BENCH-004 — Cross-machine agent mailbox

## Executive summary

Set up an SSH-accessible durable mailbox and Mac handoff. Reuse the canonical
cross-agent Markdown/front-matter convention. Active agents can read and wait;
idle-session wakeup is not established for the existing VS Code stdio server.
Never start a duplicate agent against this live conversation to simulate delivery.

## Authorized scope and frozen contract

1. [x] A01: Implement immutable messages, idempotent sends, recipient-scoped
   acknowledgement, bounded waiting and explicit reply links on the Linux host.
2. [x] A02: Test retry/conflict handling, recipient isolation and concurrent sends
   using an isolated temporary mailbox; initialize the real topic.
3. [x] A03: Write `agentcoms.md` with exact SSH commands, ownership rules,
   acceptance handshake and the idle-wakeup limitation. Notify on hardware.

No changes to Codex session storage, extension process, daemon or account settings.
No listener exposed, automatic model invocations, firmware flash or reset.
Messages request work; they do not expand the Author's authorization. The Mac
agent must initiate its connection using its existing SSH configuration.

## Verification

Three isolated tests passed, including 16 concurrent identical sends resulting
in exactly one immutable message. Real welcome published. Mac SSH round-trip
remains pending peer setup; no live-session wakeup claimed.

CLI JSON-stdin/wait arrival test also passed. Hardware spoken alert completed
with a fresh stage-6 receipt; left Legacy MOS prompt, startup and firmware
unchanged. Private evidence: agents/agentcoms/notification.json. Local handoff
agentcoms.md contains machine paths and is intentionally not committed.
Next validation belongs to the Mac peer: send and acknowledge a round-trip.


## B04-R01 — Self-assigned mailbox intake repair, 2026-11-03

Extender encounters an actual global mailbox read failure while responding to a
compiler agent's bench/access consultation: a directly written message has
unquoted header values and lacks helper routing/idempotency fields. The helper
raises JSON Extra data while scanning records, blocking valid reads and sends.
Author grants debugging as required with records. Extender owns mailbox intake;
this repair does not access hardware or change consumer source.

1. Preserve the exact invalid source bytes and a relocation/hash receipt under
   the shared mailbox's quarantine area, using the existing mailbox lock. Do not
   rewrite a valid published immutable message or discard the request.
2. Publish the intended request through the maintained helper with its explicit
   author/recipient/thread/request identity and unchanged body. Retain canonical
   publication ID and the original raw-source location in the local receipt.
3. Verify normal recipient read/send returns, reply by durable mailbox plus
   steering and explain the maintained submission command to the sender.
   No parser/protocol expansion, dependency, live bench action or new lease.

State: completed. Exact raw bytes and relocation/hash receipt are retained in
the shared quarantine; the unchanged request body is republished through the
helper. Recipient read, substantive reply/send and acknowledgement all pass. The
compiler agent confirms it will use the helper. Raw/publication receipts remain
in ignored agents/agentcoms-repairs/b04-r01. No parser/protocol or firmware change,
bench access, reservation or scheduler-state mutation. Future structural handling
remains separate from this bounded service-restoration operation.
