# Audio framing repair — execution contract

## Executive summary

The Author confirms muting Rally eliminates HUD/sky corruption and authorizes
repair, deterministic tests and hardware notification. Restore stock audio
command parsing on P4, with unavailable execution returning failure. Audio
synthesis/output stays deferred. Preserve RX06 and NET-001. No numeric audit,
MOS changes, arbitrary upstream fixes or experimental push.

This is the audio-first slice of PORT-003 UC01–UC07 and PORT-004, not completion
of the wider unimplemented-command inventory. Existing broader items remain.

## Checklist

1. [ ] AF01: Pin grammar/source, return values and malformed-input limits; freeze.
2. [ ] AF02: Retain stock dispatcher/reply path, bind bounded unavailable backend.
3. [ ] AF03: Host tests for all branches, lengths, sentinels, truncation and replies.
4. [ ] AF04: Install identified candidate; test unmuted Rally and deterministic
   graphics/audio sentinel streams against unchanged stock mainboard VDP.
5. [ ] AF05: Preserve results/usable startup, hardware voice and review stop.

## Grammar and implementation policy

Official read-only baseline: agon-vdp tag v2.16.0, video/vdu_audio.h,
video/agon_audio.h, video/agon.h; agon-docs docs/vdp/Enhanced-Audio-API.md.
Record exact commits/hashes beside results. Current dispatcher matches stock.

After channel byte and opcode byte:

| Opcode | Payload after opcode | No-op reply status |
|---|---|---|
| 0 play | volume8, frequency16, duration16 | 0 |
| 1 status | none | 255 (disabled/unavailable) |
| 2 volume | volume8 | 255 (failure, not volume0 success) |
| 3 frequency | frequency16 | 0 |
| 4 waveform | waveform8; buffer16 only if waveform=8 | 0 |
| 5 samples | action8, see below | 0 except debug action has no reply |
| 6 volume envelope | type8; see below | 0 |
| 7 frequency envelope | type8; see below | 0 |
| 8/9/10 enable/disable/reset | none | 0 |
| 11/12 seek/duration | value24 | 0 |
| 13 sample rate | value16 | 0 |
| 14 parameter | parameter8, value16 if bit7 else value8 | 0 |

All multibyte integers are little-endian. Sample actions: 0 length24 then that
many raw bytes; 1 none; 2 buffer16+format8+[rate16 if format bit3]; 3 frequency16;
4 buffer16+frequency16; 5/7 position24; 6/8 buffer16+position24; 16 buffer16 with
no reply. Unknown sample action consumes action and replies0, as stock does.
Unknown top-level opcode consumes channel/opcode and sends no reply, as stock.

Volume envelope0 none; 1 attack16+decay16+sustain8+release16; 2 three groups,
each count8 followed by count*(level8+duration16). Frequency envelope0 none;
1 phaseCount8+control8+stepLength16+count*(adjustment16+number16).
Unknown types consume only type and return failure. Preserve conditional field
reads exactly; data bytes that look like VDU controls are still payload.

The stock dispatcher and sendAudioStatus remain shared. Exclude the backend
sample-debug inspection on P4 after reading its buffer ID; that action has no
wire reply. Keep unavailable synthesis types/tasks out of the P4 build.
A64-byte stack sink plus retained readIntoBuffer drains raw samples without
allocating storage proportional to sample length or requiring a heap allocation
merely to discard. Envelope field reads retain grammar without object creation.

The unavailable backend has no enabled channels. Nevertheless, consume envelope
fields by their documented grammar: stock's disabled-channel backend currently
returns before consuming them. Record this inherited framing issue; do not
change the stock path or reproduce its payload leakage in the no-op path.

Reply path stays stock sendAudioStatus/callback/send_packet routed through EMOS.
No forwarding audio to mainboard. Replies report unavailable operation, not
silence-as-success. Missing required header/field bytes use retained timeouts;
outer dispatcher returns without reply and inner backend failures follow stock
failure replies. Timeout is not a framing delimiter: delayed residual bytes can
still be ambiguous. No promise of resynchronizing arbitrary truncated/unknown
commands, no search for apparent VDU markers.

## Validation boundaries

Host tests cover every known command/sample/envelope branch and optional width,
back-to-back commands, control-valued operands, split reads, zero/max counts,
large sample discard, truncation and exact sentinel/reply behavior. Pin the
retained dispatcher against official source so import changes demand review.
Include Wolf3D-style enable/sample/play sequences without claiming full Wolf3D
acceptance (historical exact binary remains unpinned).

Physical paired fixture draws persistent HUD/sky controls, sends Rally's audio
stream including low frequency bytes12/16, then checks pixels via standard MOS
queries. Stock success audio statuses need not equal unavailable P4 failures;
compare framing/graphics and verify P4 failure replies separately. Muted Legacy
and ExCom visual baselines already accepted by Author; retain those limitations.
Do not claim browser FPS is renderer throughput. End for human unmuted Rally
review; no requirement to implement audible P4 synthesis for this tranche.
