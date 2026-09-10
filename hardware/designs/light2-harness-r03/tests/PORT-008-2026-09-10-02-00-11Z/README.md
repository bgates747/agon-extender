# Video-only console rollback deployed

The Author requested restoring the pre-keyboard browser before adding further
functionality, then made the hot bench and SD available for the work. Deployed
console r02 from clean source 840c052; flash readback and native USB startup
pass. EMOS, native USB code and ExCom activation logic are unchanged.

A separate headless-browser connection to the physical P4 verified the exact
restored HTML/JavaScript/CSS bytes, absence of keyboard controls, and advancing
video: Presented 3 to 78 over 15.008 seconds, with no browser execution error
or disconnect during that interval. The observer then closed its connection.
This bounded check does not establish long-run stability or fix/qualify ExCom
activation. The earlier r01 failure remains open.

The returned SD startup matched the existing non-flashing v0.1.11 procedure.
It was safely unmounted without edits. A P4 log was started before the next
Author Agon reset; its USB serial open can restart P4, so no serial reattachment
is needed during the upcoming console attempt. The human ExCom result remains
pending. Exact private command logs are hash-bound by the manifest.
