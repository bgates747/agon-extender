# SD-loaded visible-text sample

This C application is the sender component of `uart-visible-text-probe-r03`.
Its maintained sample is `src/main.c`; `snprintf` converts the binary counter
1..10 into decimal lines. `VTEXT.BIN` runs from ordinary Agon application RAM.
It submits the banner and each number through existing EMOS API 0x51, never
UART/GPIO APIs. Each completed call is followed by a 250 ms clock-based pause
before the next line; the acknowledgement/quiet interval adds transport time.
Preview uses the same pause. The clock wait has a finite stalled-clock escape.

Build with `scripts/prepare_text_sample.py --output <new-bundle>`. The generated
manifest and application expose their fixture identity, build timestamp and
status independently of the installed EMOS build. Prepare P4 separately with
`scripts/prepare_visible_text.py`. Neither script installs firmware or edits SD.

For a newly prepared test, deploy the identified binary beneath `/extender`
following [SD layout](../../../docs/sd-layout.md), then LOAD its verified path
and RUN. The historical `/bin/VTEXT.BIN` location is not an installation
instruction. This fixture's dedicated P4 peer and idle UART1 prerequisite are
not supplied by the current combined console merely because it displays text.
Already-admitted Extender input can occupy UART1; preserve an independently
usable input/return path when the owning task prepares the test.

The normal run performs the EMOS-owned exchange.
`RUN . preview` writes the same generated text through ordinary MOS VDU on the
onboard display; it is a local rendering check, not UART/P4 evidence.
`RUN . check` exercises the actual gateway's invalid-address/length/output and
unsupported/incomplete-command rejections. Select video mode only in autoexec.

The resident service is `edu.text-probe`, gateway ABI 1.0, operation 2. Its
66-byte request and input must lie wholly in 040000..0AFFFF. The output
pointer/capacity/length are zero. EMOS accepts 1..1024 bytes of printable ASCII,
VDU 8..13, 30, and complete 31,x,y. It rejects mode changes and system commands
before touching UART. EMOS adds flush and General Poll A7, validates the reply,
and releases its transport before returning. Zero status means parser ACK and
quiet interval passed; browser appearance is checked separately. Legacy mode
and an unused UART1 are required. No transient module is loaded.

P4 accepts that bounded grammar without compiling the sample text. Later
sample-only revisions can select unchanged compatible EMOS/P4 builds and
replace just VTEXT.BIN; host capture expectations follow the revised sample.
This diagnostic does not route ordinary application printf to EDP or activate
Exclusive Compatible.
