# Project Tasks

This directory contains the tracked detail record for every item in `TODO.md`.
Task files hold scope, instructions, state, decisions, evidence, gotchas, and
validation requirements; `TODO.md` remains the authoritative task index.

Keep private network and filesystem topology, credentials, account data, and
unique device identifiers out of tracked tasks. Refer to an ignored local
record when such details are operationally necessary.

## Task silos and durable promotion

Use task directories as bounded work and review silos while scope, evidence,
and implementation shape are still emerging. Keeping each task's generators,
schemas, evidence, and provisional outputs together makes its contribution
discrete and auditable without prematurely declaring project-wide structure.

When a task-local result becomes recurring infrastructure or documentation,
promote it into a durable role-named location rather than leaving production
users dependent on a historical task number. Promotion preserves the task
record and accepted evidence, but the maintained interface, procedures, tools,
and canonical artifacts move under the subject they serve.

A durable construct may synthesize accepted work from several task silos. The
promotion task must identify the contributing authorities, remove competing
machine-readable sources of truth, update routine references, and preserve
traceability without copying task history into the production interface.

## Actor-explicit proposals

The `TRS-80-NNN` namespace owns Extender integration work for TRS-80-derived
software and systems. `TRS-80-001` begins with TRS-OS on Agon; the namespace
does not imply that physical TRS-80 hardware or every TRS-80 model is supported.
`TODO.md` remains the sole authoritative unfinished-task index.

Every proposed contract, decision, task, procedure, and failure path must name
the actor performing each material action. Identify the applicable eZ80/MOS
component, onboard VDP/Pico-D4 firmware, EDP/P4 firmware, hardware circuit,
physical wiring, host tool, resident service, application, or operator rather
than assigning behavior vaguely to “the system” or “firmware.”

For communication, name the sender, receiver, transport owner, and physical
wiring where known. Distinguish the actor requesting an action from the actor
authorizing, executing, recording, observing, and recovering it. If ownership
is genuinely unresolved, say so explicitly and assign the decision to a
tracked task.
