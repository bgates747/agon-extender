# First visible UART text observation

The original r01 capture independently confirms the exact 35-byte text/flush/
poll request and 8001A6 reply at 1152000 baud, valid stop bits, and flow-control
permission through each frame. All 240 million samples are present at 24MHz;
final waveform quiet tail is 9.444288 seconds and serial remained clean for
9.005480 seconds after PASS. P4 stages pass and the Author reports Agon success.

The Author's browser screenshot displays EMOS TO EDP: UART TEXT with a
connected 640×480 display and 217 received/presented frames. The screenshot
was supplied in conversation; this record describes that observation.
Explicit first-run SD/CLOCK and final prompt confirmation remains pending.

A subsequent Agon-only reset timed out because r01 remains completed until
P4 restart. This does not invalidate the captured first exchange. The Author
requested repeatability and approved r02; retain r01 as the tested definition.
