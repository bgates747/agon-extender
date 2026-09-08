# UART flow at 1,152,000 baud — PASS

The Author reports all Agon tests passed. P4's exact ordered stages and the
raw serial hash independently recheck successfully, with 70.07 seconds after
first PASS and no later error. The Author subsequently confirmed return to the normal MOS prompt; the run passes.

The analyzer retained all 240,000,000 samples at 24 MHz: 10 seconds, with the
start edge at the intended 0.1-second pretrigger position. Both exact frames
(`FLOW\r\n`, `FLOWACK\r\n`) decode without warnings. Forward/return holds
measure 1.001079 and 0.985915 seconds. Data transitions occur only while each
receiver permits them, and no blocked byte escapes. The final quiet tail is
6.712620 seconds. Bit-edge fits are consistent with nominal 1,152,000 baud in
both directions (20–21 samples per single bit); the analyzer is not calibrated.

No shortened-acquisition exception is needed. This is a short diagnostic
exchange, not sustained-load or analog-margin qualification. The earlier
long-acquisition USB issue is not claimed repaired. Identities remain candidate.
