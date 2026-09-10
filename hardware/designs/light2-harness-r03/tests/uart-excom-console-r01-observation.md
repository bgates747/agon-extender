# First ExCom console observation — r01

Author report and photograph, 2026-09-09, following deployment of
uart-excom-console-r01-b2026-09-10-01-22-40Z and
agon-emos-v0.1.11-b2026-09-10-01-22-40Z.

1. Startup SD/CLOCK and ordinary USB Legacy CLI (procedure step 2) passed.
2. EMOS EXCOM failed: the photographed screen reports
   `EMOS: display switch failed; current route retained`, followed by
   `EMOS backend unavailable` and the mainboard prompt. No ExCom route was
   published. Root cause and successful keyboard input after the failure are
   not established by the photograph.
3. The Author reports disconnected browser video and obsolete keyboard release
   controls. Read-only HTTP retrieval confirms P4 was serving those controls
   and the timing-instrumented JavaScript; this was not merely assumed cache.
   Original response bytes and their hashes remain in the private failure record.
4. The Author requested rolling the browser back before adding functionality.
   r02 restores the video-only page and removes browser input/timing from the
   shared service. This does not qualify ExCom or establish a common cause for
   the activation failure and browser disconnection. No UART capture was taken
   for the reported attempt, and its exact start time was not recorded.
