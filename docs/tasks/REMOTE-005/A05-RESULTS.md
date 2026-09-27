# R05-A05 development results

Application-owned resident lease and linked helper implemented. 119 host tests
pass; real eZ80 UART-peer send transfers 1027 bytes, preserves a 4096-byte sentinel
and returns to MOS. Paired physical qualification is being prepared with a strictly
RAM-only diagnostic peer; no production P4 staging or WebDAV claim.

The resident image initially measured 127699 bytes: +207 over the passing A04
image, leaving 3373 bytes below 128 KiB. File-engine code stays in the application.
Host tests exercise both directions, binary boundaries, descriptor fragmentation,
nested calls, busy/unsupported, malformed/stale replies, cancellation, overwrite
refusal and a lost activation acknowledgement. No uncertain mutation is retried.

The retained directory-backed emulator does not implement f_sync and incorrectly
maps CREATE_NEW to nonexclusive create. Its send-only caller result does not
qualify receive-side FAT durability. Hardware verification will supply the missing
paired filesystem evidence; the physical test peer itself stores only RAM bytes.
