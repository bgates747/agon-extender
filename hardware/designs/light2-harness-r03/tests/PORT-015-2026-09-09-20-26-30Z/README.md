# Native USB acquisition candidate deployed

The Author reported completed wiring with passing continuity, short and supply
voltage checks, both boards powered/connected, and no keyboard attached. The
workstation verified the candidate's clean source and local/staged hashes and
the bench host verified the stable P4 identity before writing and separately
verifying flash contents. Exact candidate identity and `USB HOST READY` were
observed; counters remained at zero with no attached keyboard or startup fault.

This is deployment/startup evidence only. Physical USB enumeration and key
acquisition remain pending; keyboard/load particulars remain to be recorded.
Agon, its SD media and installed EMOS were not modified or reset. The displayed
emulator browser-typing result was an attention cue, not USB qualification.

Full device-identifying commands and logs remain in the private deployment
bundle indexed through HARDWARE.local.md; their hashes are in deployment.yaml.
