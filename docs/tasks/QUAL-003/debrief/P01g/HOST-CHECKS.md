# Host checks

All16 legal payload lengths passed receiver validation. Truncation, changed
bytes and out-of-order IDs rejected. Actual candidate header/pattern compiled
with host timer/allocator shims and accepted by Python CRC32 decoder. Admission
allows one send per16667us bucket and resets to normal when disarmed. Isolated
r50 builds successfully using the retained r45 SDK/configuration. No hardware
measurement yet. New checksum work occurs outside the observation window.

Corrected candidate: actual output-isolation stop hook compiled with host timer/
allocator stubs. Tests cover compose-only and sending windows, completed-scope
accounting and disabled ladder before normal output resumes. Exact insertion
asserted in source. Historical P02 accounting stays unchanged; P01g has its own
size-aware parser with all five primary payload sizes host-checked.
