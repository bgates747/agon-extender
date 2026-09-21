# Jukebox input review — 2026-09-21

The observed failure is not a blank or incomplete launch: classic Jukebox
v0.9.6-beta displays its GUI and current directory, then does not respond to
keyboard input in ExCom. Legacy works after reset. Both compared P4 checkpoints
show this symptom. Read-only source review finds no direct interrupt-vector
collision, but does not establish where the tested binary waits.

## Source and limits

An isolated clone was fetched from bgates747/AgonJukebox. Latest tag on fetched
main is v0.11.0-beta, commit9edfba629a2a2934f4bc66ee415d73fe2f32b75f.
The user's working checkout was not changed. Local review copy is retained under
agents/jukebox-status/review. Its docs/development-log.md, Recovery and provenance
context, says the v0.9.6-beta hardware binary came from uncommitted work and
cannot be reproduced from a clean commit. Findings below apply to the reviewed
tag; do not assert identical behavior in the older installed binary.

## Findings

1. src/asm/timer_jukebox.inc::ps_prt_irq_init follows ROM table bytes0x10C/0x10D
   to install its PRT Timer1 handler in RAM. With the installed EMOS map's
   __vector_table at0x100, this selects second-table slot0x18 (handler at0x19).
2. EMOS src/emos_keyboard_io.asm::emos_keyboard_vector owns second-table handler
   offset0x35 (slot0x34), the UART1 vector. These are different slots. Reviewed
   ExCom console code does not replace the Jukebox Timer1 slot. Keyboard source
   and display route are separate; Extender keyboard reception also operates
   in Legacy, where the Author reports this program works.
3. Jukebox src/asm/input.inc uses EI then mos_getkey, followed by DI for command
   handling. This tag does not install a mos_setkbvector callback for ordinary
   input. Its timer ISR clears sysvar_keyascii and calls sample playback code;
   those are relevant to a deeper interrupt/input audit but not proof of the
   observed startup symptom. Timer activation occurs in playback, not merely
   in the timer-vector installation routine.
4. src/asm/app.asm initializes the UI, then audio command buffers, then the
   timer vector, before calling the input loop. A fully drawn GUI does not prove
   execution reached mos_getkey. Startup VDU/audio/buffer processing or a later
   command handler remain possible waiting points; no current PC/register or
   trace evidence selects one.

Reference API: agon-docs docs/mos/API.md, mos_setintvector (0x14) and UART1
interrupt vector0x1A. EMOS src_startup/vectors16.asm defines the table mapping;
current retained ROM map confirms its address. No source patch, flash, reset,
input injection or debugger halt performed for this review.

Author subsequently authorized installing the reviewed v0.11.0-beta binary at `/jukebox/tgt/jukebox.bin` and removing the duplicate `/bin/jukebox.bin`. Both actions verified; older binaries preserved locally. Retesting this tagged version remains pending. Earlier observations remain specific to v0.9.6-beta.

Author retest: v0.11.0-beta reproduces the same ExCom symptom (GUI/directory displayed, no keyboard response). One reset sent at Author request for Legacy comparison; that comparison result is pending.

## Tagged-version Legacy control confirmed

Author confirms Jukebox v0.11.0-beta runs correctly in Legacy after reset.
The tagged version now reproduces the same contrast as v0.9.6-beta: full GUI
and directory display but no keyboard response in ExCom; working in Legacy.
No cause isolated. The inspected tag can now support a reproducible source
investigation of the tested version, unlike the older uncommitted binary.
