# NET-008 — Short directional UART wire-capture results

The high-rate upload loses bytes after the sampled P4 transmit wire: at1152000
baud the analyzer decodes every P4 frame correctly, while Pi5 receives a stream
with a500-byte gap. The reverse short transfer passes. This removes P4's emitted
UART byte stream as the source of this observed gap, without claiming to identify
an ESP8266 internal buffer or an electrical receiver fault. The prior384000baud
full-minute duplex qualification remains the highest qualified operating point.

## Results

Ranking is highest baud first. Each arm uses a three-second bulk producer;
TCP buffering/draining makes receiver windows differ. These are diagnostic arms,
not sustained-rate qualification. GO/EOS control still travels both ways.

| Nominal baud, bit/s | P4 → ESP8266 → Pi5 | Pi5 → ESP8266 → P4 |
|---:|---|---|
|1152000|Failed: Pi CRC after13 accepted frames; analyzer validates all336 emitted payload frames|Passed:359 frames,367616payload bytes|
|576000|Passed:170 frames,174080payload bytes|Passed:192 frames,196608payload bytes|
|384000|Passed:114 frames,116736payload bytes|Passed:136 frames,139264payload bytes|

All six captures contain exactly288000000samples at selected24MHz,12seconds,
one byte per sample. Acquisition requests only the existing D0/D3 UART pair;
other connected probe wiring is untouched. No credential setup/capture occurs.
D0 samples P4 TX → modem RX; D3 samples modem TX → P4 RX. The sampler's nominal
clock is not externally calibrated. Decoding uses8N1 and the requested baud.

## Localization of the1152000upload failure

1. P4 queues336 deterministic1024-byte payload frames and one EOS. The analyzer
   decodes all349456wire bytes, validates every frame CRC/payload/sequence and
   EOS, with no framing error within that bulk interval. P4 reports UART/FIFO/
   ring/CRC/frame errors0 and normal command cleanup/UART retirement.
2. Pi5's raw TCP capture contains14560bytes:13 valid frames followed by a corrupt
   frame. Its first difference from the sampled UART stream is byte14511,
   counted from the first bulk-frame header. The remaining49captured bytes match
   the UART stream shifted forward500bytes. This is concrete omitted-byte
   evidence, not random corruption inferred only from a CRC number.
3. The gap occurs downstream of the physical probe. A correct digital waveform
   at that sample point does not prove receiver electrical margins, ESP8266 UART
   servicing, its AT/TCP buffering or later software behavior individually.
   No new analyzer capture at the module's internal UART receive point exists.
4. The reverse1152000arm's359frames all decode correctly on the ESP8266 TX wire;
   P4 accepts the same counts and payloads with zero UART/CRC/frame errors.
   This qualifies that short direction only. It is not a full-minute or eZ80 pass.
5. Both576000one-way arms pass here, despite the retained earlier duplex failure.
   That suggests concurrent workload sensitivity or intermittency; a single
   passing short arm cannot establish the cause or promote576000to qualified.

Framing errors while decoding the old-baud AT transition at a new baud are
retained separately. The failing upload has35such pre-bulk errors and zero in
its validated bulk window; do not label those control-preamble decode errors as
physical payload corruption.

## Source, preparation corrections and evidence

Contract47bdaf69 was pushed before implementation. P4 source5df7ae7c builds as
net008-sniffer-r01-b2026-11-10-19-39-46Z,243344bytes, SHA256
1f03ce3bb1e93c96005666d7de2bd7679c14bd0ffa04cab265ade3663d1e5aa1. Existing
duplex command, corrected receive settings and deterministic data/CRC are retained.
UP/DOWN suppress only the opposing bulk producer. Strict P4 build passes; five
native-codec/TCP controls, three synthetic waveform controls, two wire-comparison
controls and four private-packet controls pass. No private credential is used
in a captured exchange.

Offline decoder9b3401fc corrects physical channel bit placement using the retained
real AT capture. Host continuation7e4a09c2 precreates public waveform output for
sigrok's dropped capture account. First baseline transfer and analyzer both pass,
but original wrapper exit1 from postcapture file permissions remains historical;
its existing bytes were ownership-reconciled and hashed, never recaptured. The
1152000upload retains its genuine failed wrapper/endpoint result. All other
original capture wrappers return0. No failed hardware arm is replayed.

Compiler release was issued just before the final build manifest appeared;
subsequent native inspection confirms actual build0/joined and no successor or
compiler overlap. Future releases must inspect the original terminal first.

Ignored evidence: agents/net008/sniffer-r01/{up384,down384,up576,down576,up1152,
down1152}, their original parent supervisors, decoded comparison files and
up1152/localization.json. The build manifest's original host hashes remain
historical; later host-only corrections do not relabel its binary source.

## Cleanup

The normal P4 productd9b was restored through the changed245760-byte prefix
with exact independent readback and retained unchanged suffix provenance. Normal
boot/services/input, startup/listener full-file read/EXIT and a separate fresh
SAVE-only mode0/callback0/backend0/idle/free-port handback pass. Original restore
and fresh supervisors return0; every capture/reader/reset-holder group is joined.
The dedicated scheduler normally released lease171; central state confirms
active=null and no next request. Primary target access remains stopped. No mainboard firmware, startup,
ESP8266 firmware, NVS or persistent modem configuration was changed. The modem
last positively operated at1152000baud in command mode; product restoration
does not silently reset its temporary baud. The P4 diagnostic is retained only
as an artifact and is no longer installed.
