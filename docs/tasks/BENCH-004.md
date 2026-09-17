# BENCH-004 — Cross-machine agent mailbox

## Executive summary

Set up an SSH-accessible durable mailbox and Mac handoff. Reuse the canonical
cross-agent Markdown/front-matter convention. Active agents can read and wait;
idle-session wakeup is not established for the existing VS Code stdio server.
Never start a duplicate agent against this live conversation to simulate delivery.

## Authorized scope and frozen contract

1. [ ] A01: Implement immutable messages, idempotent sends, recipient-scoped
   acknowledgement, bounded waiting and explicit reply links on the Linux host.
2. [ ] A02: Test retry/conflict handling, recipient isolation and concurrent sends
   using an isolated temporary mailbox; initialize the real topic.
3. [ ] A03: Write `agentcoms.md` with exact SSH commands, ownership rules,
   acceptance handshake and the idle-wakeup limitation. Notify on hardware.

No changes to Codex session storage, extension process, daemon or account settings.
No listener exposed, automatic model invocations, firmware flash or reset.
Messages request work; they do not expand the Author's authorization. The Mac
agent must initiate its connection using its existing SSH configuration.
