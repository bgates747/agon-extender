# A04 physical admission check

Author released the idle bench and requested deployment/testing on 2026-09-27.
This authorizes hardware review in place of the pending graphical emulator gate
and the candidate freeze needed for deployment. It does not accept production
promotion or authorize implementing the full file service.

H01 [ ] Preserve actual P4 image; restore known normal Extender service to regain
keyboard control. Preserve actual EMOS ROM, SD startup and any colliding files.
H02 [ ] Freeze/build EMOS v0.1.20 and optional r58 admission peer under existing
version preapproval. Normal r58 builds omit the diagnostic; identified peer builds
require explicit --admission-probe, recorded in their manifest. Verify full EMOS
ROM after flash and keep tested v0.1.19 rollback available.
H03 [ ] On hardware with normal P4, prove prompt/input and manual SD operation;
new discovery must not disrupt the old peer. Preserve startup; no root clutter.
H04 [ ] Install temporary P4 peer. It responds only to EMOS-initiated controls in
Legacy, never does filesystem work. HTTP may arm one synthetic offer only after
a fresh idle poll; armed intents expire in one second. Check corrupt offer,
missing utility, valid finite probe, key-before-ack cancellation. The race probe
injects one virtual-code-zero key-down; host Escape/key-up ends that test.
H05 [ ] Verify 4096-byte application sentinel, ordinary public application editor,
return to prompt and unchanged manual listener. Capture independent evidence;
input delivery counters alone are not command completion proof.
H06 [ ] Remove temporary probe/startup changes and restore normal P4 firmware.
Leave responsive keyboard and normal CLI. Record firmware identities, exact
rollback locations privately, retained results and any untested boundary.

No ExCom automatic-transfer claim: paired active parser is not implemented.
No file mutations under new admission: finite utility only exercises the
loader/editor/memory boundary. Existing manual listener handles deployment.
All host output, reset/flash actions and SD paths follow maintained guides.
