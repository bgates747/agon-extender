# Counted-point UART/CTS findings

Run `AUDIT-005-2026-09-10-19-44-52Z`, procedure `uart-path-capture-r01`.
**Waveform, acquisition and Agon SD result pass; W6 measurement is complete.**
The [returned CSV and same-run comparison](evidence/counted-point-trace/sd-completion.json)
confirm the result and successful Legacy return. The
[measurements](evidence/counted-point-trace/analysis.json) and
[collection record](evidence/counted-point-trace/collection.json) preserve
hashes, timestamps and the evidence boundary. Original capture and independent
decoder output remain in the ignored bench record.

## What the wire shows

The analyzer recorded all 720,000,000 samples at 24 MHz. The exact 32,768-byte
counted-point payload, unique marker, black marker reply and white final pixel
reply are present. Independent sigrok and sample-level decoders agree. No
framing errors are found, and every observed payload byte starts with active
CTS permission. Neither firmware image changed.

| Component of payload wire span | Seconds | Share of span |
| --- | ---: | ---: |
| Bytes actually occupying UART TX, estimated from 8N1 framing | 0.284 | 6.4% |
| Inter-byte idle while P4 permits sending, CTS low | 0.764 | 17.2% |
| Inter-byte idle while P4 withholds permission, CTS high | 3.407 | 76.5% |
| Total first-byte start to final payload stop bit | 4.456 | 100% |

Rounding explains the percentage sum. **81.7% of inter-byte idle coincides
with P4 withholding permission.** The ten longest gaps are approximately
151–154 ms each and almost entirely CTS-high. This is direct evidence that
receiver backpressure is the dominant observed idle component in this case.
It does not identify which P4 task, buffer, lock or drawing operation caused
P4 to withhold permission.

The distinct marker query starts at 12.715 s into the acquisition, so the
provisional 12-second window would have missed the measured workload entirely.
Its reply takes 124 ms; payload begins about 151 microseconds after that reply.
The final pixel response finishes 625 ms after the final query ends. Thus
first payload byte through completion reply takes 5.081 s. The six-byte final
reply itself occupies about 95 microseconds including small reverse-direction
flow-control gaps; the long completion delay precedes its arrival. An
[additional reverse-permission check](evidence/counted-point-trace/analysis-reply-permission.json)
finds Agon RTS continuously low during the 624.7 ms wait for the first reply
byte: Agon was permitting reception throughout that delay. Seven directed
waveform tests, including blocking permission before the first reply, pass.
The original analysis is retained alongside this additional check.

## Interpretation and next decision

Prior full-suite counted-point medians were 1.017 s Legacy and 4.550 s ExCom
inside the output calls. This trace has a similar ExCom duration but uses wire
boundaries. The returned `00000004.CSV` is the only new file since SD handover;
its build and case match, and the executable hash is unchanged. Its successful
footer records one completed row and Legacy return status zero. Earlier CSVs
are unchanged. The file's FAT timestamp is not used as a UTC run identity.

| Same-run interval | Agon clock (s) | Wire (s) | Difference (ms) |
| --- | ---: | ---: | ---: |
| Payload send | 4.450 | 4.456 | 6.1 |
| Completion tail | 0.617 | 0.625 | 8.4 |
| Payload through reply | 5.067 | 5.081 | 14.5 |

All differences are within the Agon clock's 16.67 ms quantum. Software and
wire boundaries still differ; this is agreement at that resolution, not a
precise synchronization measurement. Both setup and final reply exceeded the
first ordinary MOS wait but completed within the measurement bound, with the
correct pixel. No stock-deadline compliance or firmware qualification follows.
Do not subtract different runs/boundaries to invent an exact repair speedup.

The immediate performance target is P4 receive/parser/display service during
these CTS-high stalls. The W2 source map already identifies the shared parser,
USB and reply loop, the driver RX buffer, and the high-priority frame service's
primitive/snapshot work. Source boundaries nominate where to investigate;
they do not yet demonstrate a particular scheduling or locking defect.

The EMOS byte-path reuse findings remain valid. They are not established as
the dominant cause of this counted-point slowdown. CTS-low idle can include
caller, IRQ and transmit-service cost; it is not a pure CPU-time measurement.
A faster sender alone cannot transmit while P4 withholds CTS permission.

The Author accepted these findings and authorized the
[formal W7 control](browser-disconnected-control.md) on 2026-09-10: the
same trace with browser video disconnected, keeping the firmware and workload
fixed. That would test whether servicing browser snapshots materially changes
P4 backpressure before choosing a firmware repair or core assignment. It has
not yet been run. No repair is
selected or authorized by this result.
