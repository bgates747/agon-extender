# ESP8266 bidirectional baud ladder and sustained integrity test

Smith selects an actual P4/ESP8266/Pi5 torture test: increase UART baud through
short checked exchanges until an error or the Agon-exact1152000 baud ceiling,
then step down after error and lengthen the successful rate to a full minute.
Extender owns this work. Keep the working wiring, development firmware and
Smith-held bench. C8 comparison and possible UART1 multiplexing are later work.

## Direct authority and scope

1. Smith explicitly authorizes CRC checking in both directions: the Pi5 checks
   incoming P4 data and the P4 checks incoming Pi5 data. This is an exception
   for this test's application transfers through ESP8266/Wi-Fi/TCP, not a blanket
   change to EMOS/P4 control framing or the project's no-CRC default.
2. Physical path: P4 UART2 TX48/orange and RX47/teal, existing4-wire ESP8266,
   its actual AT1.3.0.0/SDK2.0.0 modem firmware, Wi-Fi and a finite Pi5 TCP peer.
   No flow-control pins exist on this modem header; use8N1/noRTSCTS throughout.
3. Adjust current UART baud through AT+UART_CUR only; never save new UART or
   Wi-Fi defaults, flash/reset the ESP8266, change mainboard firmware/startup,
   replace unchanged components or silently use P4 Ethernet as the data path.
   Reuse actual associated Wi-Fi when available. Missing network setup is a
   concrete prerequisite, not a serial-rate failure.
4. The development image remains installed after each iteration by explicit
   instruction. Retire UART drive and stop owned captures/clients after bounded
   cases; record the module's actual current baud for the next command.
   Keep the bench held until Smith explicitly releases it. No automatic rollback.

## Selected sequence and acceptance

1. Rates:115200,230400,384000,576000,1152000 baud. They correspond to integer
   divisors10,5,3,2,1 of the standard Agon18.432MHz clock divided by16. Record
   the actual P4 programmed/readback rate separately; do not equate this source
   arithmetic with physical clock calibration or a successful C8 run.
2. At each rate first establish bounded AT/connection readiness, then run short
   simultaneous upload/download data (at least2s active per direction, with a
   one-second producer margin). Stop ascending on the first CRC, sequence,
   framing, UART overflow/parity/break, missing/truncated data or timeout error.
   Preserve exact error, case, data/counters and trace; do not relabel a failed
   rate or retry it until it happens to pass.
3. Candidate is the immediately preceding successful rate, or1152000 if every
   short rung passes. Run progressively10s,30s,60s active checks, using2s sender
   margin on the final60s check to ensure both receive windows cover a minute.
   A longer-run error backs down one rung and repeats this duration progression.
   A115200 failure means no rate is qualified; stop with the concrete evidence.
4. Success requires both endpoints to verify all received frames, byte counts,
   frame order and CRC32, with no UART faults, drops, resync, omissions or
   incomplete direction. The final receive windows at both endpoints must each
   cover at least60s of ongoing transfer. Test preparation, baud switching,
   connection setup, producer/receiver drainage and cleanup are separate timings.
5. Use deterministic varied binary payloads and explicit frame length/sequence.
   CRC32/IEEE covers header identity/sequence/length plus payload; validate
   implementations against standard vectors and the actual shared codec.
   Distinguish a receiver's CRC check from sender submission or TCP SEND OK.
   Record both endpoint results and useful payload bytes/s separately from
   framed serial bytes and nominal8N1 capacity (baud/10 bytes/s).
6. Record highest qualifying **tested** baud for this exact combination and
   workload, as Smith's requested acceptance result. Do not claim a universal
   physical limit, arbitrary-day reliability or C8 performance. If1152000 passes,
   call it the selected test ceiling, not proof the P4/ESP8266 cannot go higher.

## Progress, bounds and recovery

1. P4 and Pi5 report elapsed time/bytes/frames/errors at least once per second
   during an active test. A sleeping host or unchanged UI is not progress.
2. Each connection/control wait is bounded; data cases have the requested active
   duration plus bounded drain/cleanup. Whole ladder and backoff progression
   have a finite2700s ceiling. No automatic clock extension, application replay
   or firmware restoration follows a timeout.
3. For data-mode cleanup stop producers, join owned tasks, retire UART safely
   and use the documented guarded +++ escape/AT close sequence. Keep any failed
   case intact; distinguish cleanup failure from data-integrity failure. Actual
   known baud and command/data state remain explicit between cases.
4. Pi compiler work follows its separate FIFO, expected under120s with600s
   bound/under2GiB. Native codec/host-peer tests precede physical installation.
   The modest Pi TCP peer is part of this authorized bench test, not an emulator
   or unrelated heavy workload. Retain genuine parent waits and close owned
   sockets/readers/reset holders without releasing Smith's hardware hold.

## Optional wire observation selected by Smith

Smith offers spare sniffers; use two receive-only channels on GPIO48/P4TX and
GPIO47/P4RX, plus existing common ground, without power/TX drive. Actual channel
numbers/colours and attachment remain pending his construction report. Keep
existing probe assignments intact. Verify the instrument's input-only mode,
current supported sample rate and host identity before acquisition. Wire traces
can distinguish framing/baud/byte-path faults from endpoint parser/CRC failures;
they do not replace the two endpoint integrity checks. Capture only after any
secret Wi-Fi setup, keep trace data private and record its timing/loading scope.

## Bounded source references

1. Official MOS v3.0.2 reference `src/uart.h` MASTERCLOCK18432000 and
   `src/uart.c::init_UART1`, integer divisor from clock/(16*baud), read-only.
2. [Espressif AT instruction set v1.5.4 (2016)](https://www.espressif.com/sites/default/files/4a-esp8266_at_instruction_set_en_v1.5.4_0.pdf):
   AT+UART_CUR current configuration, AT+CIPMUX single link, AT+CIPSTART TCP,
   AT+CIPMODE/AT+CIPSEND transparent data, guarded+++ escape. Actual old modem
   support must be checked; never substitute newer AT-firmware assumptions.
3. Pinned IDF5.5.5 source commitb774170ff46c393eeb5e495ea37936038d3f4f4f:
   UART pin matrix, event errors, baud setting/readback, bounded receive and
   UART retirement, plus esp_timer_get_time clock units. Existing task header
   and full diagram retain actual P4 wiring/allocation and3.3V-bank requirements.

## Later work, not this hardware iteration

MechAgon consumes the measured contract after bring-up. Smith selects C8 as the
next comparison after this qualification. He raises rewiring Olimex UART1 through
a small mux as an alternative; no chip, schematic, wiring change or MOS/P4 mux
implementation is selected here. Retain that option for an explicit circuit
choice rather than silently changing the current bench during measurement.

## Concrete implementation contract

1. The P4 and Pi5 use1024-byte deterministic varied payloads, a16-byte header
   (magic,sequence,length,CRC32), and an explicit zero-payload end record. CRC32
   covers the first12 header bytes and payload. A nonce/configuration hello and
   GO precede the test. Both directions stream simultaneously without per-frame
   acknowledgements; each receiver checks every frame and final endpoint counts
   must match. No resynchronization repairs a failing stream into a pass.
2. ESP8266 AT transparent TCP mode carries the binary records. The2016 reference
   specifies20ms/2048-byte transparent packet batching; this is a possible modem
   transport bottleneck to measure, not a guaranteed byte rate. Bulk payloads
   avoid literal '+' bytes so the modem's command escape is not accidental.
   Separate setup includes any expected old/new-rate acknowledgement ambiguity;
   require positive AT at the new programmed rate before data measurement.
3. Actual files: P4 `bandwidth.cpp`/`bw_codec.h` within the task diagnostic;
   Pi5 `scripts/modem_bw.py`, `modem_bw_peer.py`, `modem_bw_protocol.py`.
   Native codec cross-checks compare the exact P4 framing bytes with Python;
   loopback checks exercise the actual duplex peer and false-pass rejection.
   These are host controls, not claimed physical transfers.
4. Smith reports canonical green/orange probes on corresponding wire colours,
   with all existing modem/P4 wiring unchanged since the passing test. Canonical
   instrument colour mapping is D0=green,D3=orange. Signal direction must be
   established from actual known AT traffic, not assumed from the unaudited
   crossover. He also reports old P4 header probe attachments remain; UART
   transmission stays stopped until it is clear these do not join old signal
   nets to the new UART nets. Software channel selection cannot disconnect
   physical wires. Independent source/build preparation may continue.

## Prepared software, physical test not yet started

Source8add6d80 builds the identified P4 appliance
`net008-uart2-bw-r01-b2026-11-09-20-58-31Z`,238032 bytes SHA256
`d1d231484a09e9bf412c5decaf6a6d0ccc22d409c7ef118f57731113fd468365`.
The corrected native build takes41.223 host seconds, genuine parent wait0 and
owned process group join. CRC32 standard-vector, exact native/Python frame
comparison, actual loopback duplex peer and count/short-window false-pass
controls pass. An initial native format-width error was corrected with an
explicit cast, retaining strict compiler diagnostics. Compiler805 was released.

No torture appliance has been installed or invoked. The retained working AT
image is still the actual P4 selection; no benchmark baud or network setting
has changed and no CRC/bandwidth qualification is claimed. Current whole-test
scope remains authorized. Before target transmission, clarify whether Smith's
old-header comment means other independent analyzer channels remain attached
(which does not join the UART nets), or that a green/orange channel still joins
an old signal to its new UART wire (which needs physical separation). Do not
confuse that topology question with asking for the already-given test permission.
Actual Wi-Fi association/IP is also to be observed through bounded INFO before
assuming the TCP data path is ready.

## Probe clarification before physical execution

Smith confirms D0 green and D3 orange connect only to the two new UART wires.
Other analyzer channels remain attached independently to old P4 headers; neither
UART probe joins an old signal net. This resolves the topology question above.
The existing actual164 lease and explicit development-firmware retention remain
in force. Install the identified torture appliance, query actual modem network
state, and then execute the authorized CRC ladder when TCP connectivity is ready.

## Actual installation and network prerequisite

The prepared238032-byte d1d23148 application is now installed on P4, with an
independent exact241664-byte application-sector readback. Partition selection,
bootloader, NVS, mainboard firmware and startup remain unchanged. The retained
incoming e348 image plus known unchanged original suffix define rollback bytes;
no rollback was performed. Boot remains stopped until an explicit USB command.

Two bounded INFO exchanges pass at1152008N1 and retire UART2 afterward. The
modem reports STATUS5 and station IP0.0.0.0: command transport works, but it is
not associated with Wi-Fi. No BENCH/data case or baud change has been issued.
No CRC throughput or maximum baud result is claimed. The earlier working C8
private configuration was kept on its SD card; local private.cfg files are host
test fixtures, not an accepted network profile. A working private SSID/password
profile is required before the Pi5 TCP endpoint can be exercised.

A finite12-second24MHz receive-only capture acquires exactly288000000 samples
from D0 and D3, then is losslessly archived and extraction-hash verified.
Known AT traffic establishes these actual directions, without framing errors:

| Channel / probe colour | Observed traffic | Direction |
|---|---|---|
| D0 / green | AT, ATE0, CIPSTATUS, CIFSR | P4 TX to ESP8266 RX |
| D3 / orange | OK and modem status/address replies | ESP8266 TX to P4 RX |

This establishes observed signal direction, not an independent survey of the
connector-end crossover. Earlier diagram lead-colour assumptions must not
supersede this capture. Other analyzer channels were not acquired or moved.
Both original host supervisors and all owned child groups join successfully;
reset holder is released, UART pins are retired, and the identified development
image remains installed. Product P4 input/HTTP/SD services are absent in this
isolated image. Smith's actual164 hold remains; no bench release is requested.

## Earlier credential provisioning investigation

Smith recalls a bench provisioning script that read private credentials and
programmed them into a module after a button-assisted programming entry. This
report is retained as a lead, not dismissed because the modem is disconnected.
STATUS5/IP0.0.0.0 establishes current disconnection only; it does not establish
absence or erasure of saved credentials. No ESP8266 flash write occurred during
this NET-008 work; the new application writes targeted P4 only.

The archived WROOM reference at commitc200d97fac4027da386c24aecba1f367dd74d329
contains two distinct earlier paths:

1. Commitbcb97cd1f35ff51a5dbfbdee3224c238ffcdf1a1 (August6) compiled a private,
   ignored `wifi_credentials.h` into the ESP32-WROOM Wi-Fi application and
   recorded an actual WROOM flash/connect pass. This fits the remembered
   credentials-in-firmware mechanism but identifies a different processor.
2. `extender/scripts/store_wifi_credentials.py` stores one private packet in
   the desktop login keyring. `run_wifi_join_probe.py` supplies it through the
   WROOM to the ESP8266; `wroom_wifi_join/src/esp_at_core.cpp` uses
   AT+CWJAP_CUR. The August10 retained record explicitly describes temporary
   association followed by verified disconnect, without persistent modem
   setting changes. The later C8 setup also uses AT+CWJAP_CUR.

These findings do not prove no other ESP8266 provisioning ever occurred. The
exact remembered secrets-file-to-ESP8266-flash script has not been located.
Saved modem configuration has not yet been queried by this torture appliance;
its bounded INFO currently queries only connection status and current address.
Do not ask for credentials on the premise that STATUS5 proved they were erased.

## Current Oryx keyring availability

Smith confirms the remembered mechanism was WROOM-mediated provisioning rather
than credentials flashed into ESP8266 firmware. A local SD configuration is a
suitable credential source for later direct-Agon operation; this records the
direction, not a new persistent-modem write or implementation selection.

A read-only metadata check of currently booted Oryx finds its keyring directory,
a nonempty default keyring file, a running Secret Service and an unlocked
default collection. Exact SearchItems attributes from the archived provisioning
script find zero matching MOD-WIFI regression entries, locked or unlocked.
No secret values are retrieved, no keyring is unlocked or written, and no
hardware operation occurs. The Python Secret binding is absent there; direct
standard D-Bus metadata calls complete the check without package installation.

Current Oryx is a different OS installation from the older Pop!_OS environment.
The old credential may remain on that retained installation; its partition was
not inspected or mounted in this check. Existing default keyring presence is
therefore confirmed, while availability of the old credential is unestablished.
The P4 development image,115200 modem setting and Smith-held bench are unchanged.

## Retained Pop!_OS keyring located

Smith identifies the original credential source as the earlier Pop!_OS desktop,
before Pi5 became the central development host. Read-only filesystem metadata
confirms the inactive installation identifies itself as pop-os and retains a
2390-byte login.keyring, last modified October9. A separate user.keystore also
exists. No keyring contents or secret values are read, no collection is unlocked,
and nothing is copied or imported into the currently booted OS.

The partition remains unmounted. Default read-only debugfs directory inspection
avoids mounting, journal replay and cross-installation writes. This establishes
survival of the old keyring file, not presence or validity of the specific
MOD-WIFI entry. Recovering that exact entry remains a distinct next step; do not
claim the old credential was lost merely because current Oryx lacks the entry.
Bench custody, P4 development image and modem settings remain unchanged.

## Credential host correction to always-on Pi5

Smith confirms the new Oryx SSID/password entry checks correctly, then selects
Pi5 as the required credential host because it controls the bench and remains
on. The Oryx-dependent connection step is paused; no modem join or baud case was
submitted. Pi5 metadata confirms keyring software/Python bindings and its user
bus exist, but no keyring files or running Secret Service exist yet.

Prepare a human-run interactive enrollment on Pi5 using the exact archived
MWJ1 entry format. Initialize/unlock an encrypted Pi keyring with hidden human
input, then enroll Wi-Fi SSID/password with the retained helper. No password is
put into a command line, temporary file, capture, tracked source or chat. The
Pi keyring must be unlocked again after a restart before unattended use; merely
being always-on does not itself establish automatic encrypted-keyring unlock.
Do not copy Oryx's complete keyring, silently store an unlock password or create
an unencrypted collection. Actual Pi credential enrollment remains pending the
human interaction; current hardware hold and development image persist.
