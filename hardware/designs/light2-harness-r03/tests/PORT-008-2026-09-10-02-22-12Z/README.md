# ExCom retained-mode correction deployed

P4 console r03 from clean source `0f10013` passed flash/readback and native USB
startup. The selected keyboard enumerated. Installed EMOS v0.1.11 and the SD
startup remain unchanged. The correction invokes retained VDP context/font
initialization before preparation acknowledgement; it addresses N002's captured
null-font crash. Host boundary tests and the P4 build pass.

A bounded physical browser check verified exact video-only assets and advancing
video (Presented 3→78 over 15.012 seconds), with no browser execution error.
That observer closed its connection. The agent armed a 30-minute P4 serial log
before requesting the Author's Agon reset; no serial reattachment is needed.

Physical ExCom checks were pending at deployment under
`uart-excom-console-r03.md`. The subsequent Author-accepted functional milestone
is recorded in `PORT-008-2026-09-10-02-22-54Z`. Startup/video health alone does not
close the activation defect. This is a P4-only deployment, with no Agon reset,
flash or SD write performed by the agent.
