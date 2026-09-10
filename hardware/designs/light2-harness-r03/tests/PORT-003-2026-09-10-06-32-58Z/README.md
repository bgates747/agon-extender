# Coalesced RGB222 frame-request correction deployed

Console r07 from clean source `52479f0` is flashed and independently readback
verified. The identified candidate starts the USB host and HTTP service. A
workstation browser checked the exact served assets and received/presented
104 RGB222 frames, including a continuous 20-second credit interval. The client
then closed and HTTP remained responsive. This is a bounded transport/startup
check, not a slideshow performance benchmark or an ExCom handshake PASS.

EMOS v0.1.12 and the SD contents are unchanged. The agent did not reset Agon.
Keyboard admission and manual `emos excom` with browser video already connected
remain for the operator. A separate bounded serial recording is ready for that
attempt; its private location is recorded in `HARDWARE.local.md`.
