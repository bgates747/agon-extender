# Audio framing repair results

## Executive summary

The repaired P4 preserves the HUD/sky while processing audio commands.
The paired hardware fixture passed144pixel checks and48audio replies on each
route, with zero pixel differences or failures. Unmuted Rally's captured HUD,
sky and roadway are intact at speed224. Human full-game review remains pending.
P4 synthesis remains unavailable; operations return failure rather than playing
sound. The stock dispatcher and reply function are retained.

## Results

| Check | Stock mainboard VDP 2.16.0 | P4 r21 |
|---|---:|---:|
| Persistent HUD/sky/road pixel checks | 144 passed | 144 passed |
| Audio replies received | 48 | 48 |
| Pixel differences against stock | Baseline | 0 |
| Fixture failures | 0 | 0 |
| Audio execution | Stock behavior | Unavailable; expected failure statuses |

P4 status/volume return255; other supported audio operations return0. Replies
still use stock protocol callbacks and EMOS routing. Receipt of all48replies
verifies the physical return path; success audio statuses are intentionally not
equal across the two devices. See AFLEG1.CSV, AFEXC1.CSV and comparison.json.
Each route receives identical VDU bytes; the fixture's stock/unavailable argument
changes only its reply expectation.

Host tests pass15,120framing/truncation cases plus targeted timeout-reply checks.
They cover all known dispatcher branches, optional widths, maximum envelope
counts,24-bit maximum sample length, split reads, a64-byte maximum discard sink,
back-to-back sentinels and Wolf3D-style enable/sample/play sequences. The source
guard confirms the shared dispatcher/reply function match pinned stock v2.16.0,
except the explicitly excluded unavailable sample-debug backend. This is not
full Wolf3D hardware acceptance.

The documented envelope grammar is consumed even though P4 has no enabled audio
channels. Stock's disabled-channel backend can return without consuming those
fields; that inherited framing issue is recorded, not changed in stock code.
Arbitrary malformed/truncated byte streams are not claimed to resynchronize.
The existing sampleRate unsigned/-1 warning is retained, not opportunistically
rewritten.

## Candidate and observation limits

Installed: `uart-excom-console-r21-b2026-09-15-05-53-11Z`, controlled patch
commit e086893. build.json records all hashes; deployment.json records physical
verification. RX06 road conversion, NET-001 viewer takeover, dependency lock and
post-build DSP matrix derivative match the preceding r20 candidate byte-for-byte.
The historical installed r17 source archive was dirty; this controlled derivative
is exploratory, not a broad release qualification. Mainboard VDP and EMOS were
not flashed. Fixture hash is in staged.json; official baselines are in
../baseline.json.

Unmuted Rally ran from the existing verified deployed game path, with no game
file changes. rally-unmuted.png shows the live final frame at224; the first
received snapshot was a retained prior fixture image, as permitted by the
snapshot service. The20-second observation received314frames. Those are network
observations, **not measured renderer FPS**. Earlier Author muted/Legacy visual
acceptance is retained; this turn's new strict stock comparison is the fixture,
not a full new four-way timed Rally benchmark.

| Operation | Observed wall time |
|---|---:|
| Isolated firmware build |118.51s|
| Fixture/startup deployment and verification |59.87s|
| P4 flash/verification/startup |47.87s|
| Reset-to-collection completion |118.44s|

The last interval includes boot, both fixture runs, local SD writes and network
retrieval. It is useful as an overall repeat estimate, not isolated fixture or
render timing. No reset/retry was needed for that run.

## Remaining scope

Human unmuted Rally/Nurples review, full Wolf3D acceptance, broader unimplemented
command inventory and the numeric audit remain separate. Audio synthesis stays
deferred. Experimental changes remain local until review.


Hardware spoken attention playback replaced a fresh pending marker with
`audio_commands=pass`. Original autoexec was restored and read back unchanged;
the Agon returned to the Legacy MOS prompt. Human hearing/full-game acceptance
is pending. See notification.json. All source/results are committed locally.
