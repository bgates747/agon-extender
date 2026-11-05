# Application-owned network replies — development correction

The Author requests moving the new network state out of EMOS. The application
now owns reply storage, correlation, READY state and expiry; P4 wire bytes stay
unchanged. This replaces the earlier resident-mailbox draft, before deployment.
The existing MOS callback is reused, with no new resident application pointer.

1. The new ext.net OPEN output is7 bytes: token32LE then prior KBvector24LE.
   EMOS copies the existing vector under its ordinary IRQ lock. OPEN leaves NM
   callbacks dormant; the app installs its callback before first SUBMIT.
2. The public C signatures remain begin/submit/take/release. TAKE is app-local,
   never a resident gateway operation. The old operation1 refuses. Callers keep
   the input immutable throughout synchronous SUBMIT; no pointer survives return.
3. The application owns one MOS0x1D callback. Use `include/agon/net_callback.asm`
   with `tests/network/messages/callback_example.c`, or integrate the classifier
   into an already-owned callback. No hardcoded vector address or second handler.
4. EMOS accepts a bounded0x8F frame14..142 bytes with NM/version and an embedded
   length equal to actual frame size. Its private C/assembly bridge borrows the
   UART1 ISR's payload through the existing user vector, without keyboard effects.
5. Callback entry is ADL with DE pointing to the borrowed payload. The maintained
   app wrapper preserves AF/BC/DE/HL/IX/IY and returns normally. Its C helper is
   `unsigned agon_net_callback_packet(const uint8_t*)`, returning1 to consume NM,
   zero to chain through the saved previous vector. Native unsigned returns HL.
6. The classifier reads only four bytes. NM reply kind0x81..0x83 cannot match a
   validated physical KEY's down/up0/1. The app copies matching token/query reply
   into static app RAM before ISR return. No wait, allocation or MOS call in ISR.
   Ignore stale NM without passing it to a historical keyboard-only handler.
7. Chain every non-NM callback to the saved previous vector. Ordinary MOS key
   publication happens after callback, so prior callback payload edits remain
   visible. Mode reply flags use the existing mode packet handler independently;
   the app's router does not consume mode replies. Native VDPL/P3DR/diagnostic
   callback extensions, when present, likewise chain to the previous owner.
8. RELEASE disables NM before restoring the saved vector via MOS0x1D on every
   completion/cancel/fault path. EMOS exit/fault also disables NM. Pointer memory
   remains owned by the existing MOS callback API; there is no second registry.
9. Actual composed host checks, native C/assembly compilation and required EMOS
   linked gates must pass for the corrected checkpoint. Software checks do not
   establish physical timing or current installed compatibility.
