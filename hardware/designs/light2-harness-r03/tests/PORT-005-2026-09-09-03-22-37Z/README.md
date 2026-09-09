# Controlled keyboard sender deployed

The Author authorized the P4 flash. The workstation rechecked local/staged
hashes and stable USB identity, then the bench host wrote the frozen candidate
and independently verified flash contents. P4 revision v1.3 and exact candidate
`uart-keyboard-probe-r01-b2026-09-09-03-01-48Z` were observed. Startup confirms
1152000/8N1 on RX22/TX12/CTS23/RTS11 and a clean waiting sender with CTS HIGH.
No keyboard transaction occurred during deployment observation.

EMOS v0.1.8 and its prepared EMBOOT/KBWIRE SD remain unchanged. The workstation
capture launcher now selects this installed sender and the frozen twelve-key
verdict, with 24 MHz / 288-million-sample acquisition. The Author inserts the
prepared card and runs the launcher; Enter arms P4/analyzer before its powered
Agon reset cue. Completion follows acquisition and five clean seconds after
P4 PASS.

Agon smoke, keyboard publication, MOS prompt, waveform and two subsequent
Agon-only reset results remain pending. This record proves deployment and
startup only. Browser focus input is a later increment.

Machine-local identities, commands and full write/verify/boot logs remain in
the private deployment bundle. Their hashes are recorded in deployment.yaml.
