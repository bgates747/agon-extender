# Visible-text P4 candidate deployed

Author explicitly authorized flashing. The factory image was written and
independently verified on the expected P4. Boot reports the exact candidate,
1152000/8N1 pins and an empty receiver with CTS stopped. The HTTP index matches
the compiled source, and one requested startup frame passes EVF1 validation at
640×480. This confirms startup service readiness, not the UART text test.

EMOS v0.7.0 is installed, with its separate smoke/VDPTEXT SD prepared and
unmounted. The paired test awaits the operator's capture invocation and powered
Agon reset at the readiness cue. The browser must independently show the exact
EMOS TO EDP: UART TEXT message.
