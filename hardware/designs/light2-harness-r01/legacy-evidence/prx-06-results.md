# PRX-06 minimal-sender performance milestone

On 2026-08-16 the vendor-derived ESP-IDF v5.5.5 PARLIO RX lifecycle received
every record in a seven-profile physical sender sweep. The sender was a narrow
Agondev assembly loop reading the fixed canary from RAM, writing Port C, and
driving inline CLOCK edges. It performed no per-byte READY check, helper call,
shadow update, record construction, or UI work inside the measured epoch.

| Delay NOPs per setup/high/hold segment | Endpoint payload KiB/s, three runs |
|---:|---|
| 24 | 192.4, 192.6, 192.7 |
| 16 | 259.1, 259.1, 259.2 |
| 10 | 349.9, 349.8, 349.7 |
| 6 | 456.2, 456.4, 456.0 |
| 3 | 591.4, 590.7, 590.7 |
| 1 | 735.3, 735.8, 735.3 |
| 0 | 838.9, 836.8, 837.5 |

The independent capture of a fourth zero-delay record measured 876,888.5
falling CLOCK edges per second, equivalent to 856.3 KiB/s of raw eight-bit
payload. It proved one READY_N assertion/release, one VALID_N
assertion/release, exactly 1,024 valid falling edges, and zero mismatches on
the observed D0–D2 bits. The green D3 probe remained constantly High, so this
report does not claim analyzer observation of D3. The P4 nevertheless received
the entire D0–D7 record with exact first/last bytes, sequence 1, counter
pattern, and matching stored/calculated CRC `6474` on all 22 transactions.

The endpoint figure includes receiver completion/notification overhead around
the admitted interval; the analyzer figure measures the actual clocked wire
epoch. This experiment found no failure boundary before the eZ80 sender
reached its zero-delay loop. It therefore establishes approximately 0.84
MiB/s useful payload on the current breadboard, rather than a P4 receiver
ceiling near the earlier cautious 61 KiB/s result.

Authority is the single passing run
`tests/runs/2026-08-16_005754_prx-06-speed/`. Its local manifest covers the
measurements, endpoint transcript, analyzer summary, raw capture, exact source,
and fixture scripts. Reproducible P4 and Agon build outputs remain ignored.
