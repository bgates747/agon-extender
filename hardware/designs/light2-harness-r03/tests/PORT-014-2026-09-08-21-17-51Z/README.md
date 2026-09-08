# SD-loaded counting receiver deployed

The Author authorized the P4 flash. The workstation rechecked local and staged
hashes and the stable USB identity, then the bench host wrote the frozen r03
factory image and independently verified flash contents. P4 revision v1.3 and
the exact candidate build were observed. Startup shows 1152000/8N1 with
RX22/TX12/CTS23/RTS11 and an empty receiver with CTS stopped. The served browser
page matches the frozen source. No browser video connection was taken.

EMOS v0.1.7 and its prepared EMBOOT/VTEXT SD were unchanged. The workstation
launcher now selects the r03 receiver, 11-transaction counting verdict and
24 MHz / 288-million-sample capture. The previous r02 launcher is backed up.
No paired run has started; Agon smoke, sample PASS, browser count, waveform and
two subsequent Agon-only resets remain operator/capture observations.

Machine-local device details, flash commands and full write/verify/boot logs
remain in the private deployment bundle. Their hashes are recorded here.
