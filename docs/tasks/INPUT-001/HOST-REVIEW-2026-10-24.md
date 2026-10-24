# Host controller review — 2026-10-24

The Author approves the viewer's appearance and supplied a recording exercising
the F310 controls. The recording replays exactly, covers full travel on all six
analog axes and ten buttons, and reports no evdev overflow. All observed stick
values lie on an eight-bit lattice despite the signed16 Linux range. A second recording validates Guide press/release and physical unplug/replug.
Rest calibration remains unobserved.

## First recording and coverage

| Item | Retained observation |
|---|---|
| Duration | 22.455017604 seconds, host monotonic clock |
| Raw events / committed reports | 1,848 / 894 |
| Connection sessions / input gaps | 1 / 0 |
| Replay | Every recorded frame agrees with raw-event replay; clean end marker |
| Four stick axes | Each reaches −32768 and +32767; smallest observed step and step GCD 257 |
| Two independent triggers | Each reaches 0 and 255; smallest observed step 1 |
| Both D-pad axes | Each covers −1, 0, +1 |
| Buttons | A/B/X/Y, LB/RB, Back/Start, left/right stick clicks each have matched press/release edges |
| Guide / centre Logitech button | No event in the recording; not qualified |
| Disconnect/reconnect | No physical cycle in this recording; synthetic coverage only |
| Rest measurement | No calibration action recorded; final resting accuracy not established |

Capture SHA-256:
`4d97e73bbcdeecb1da66d84d5579ea9575b9ec0ee5ed936c0fb9575d3cb94231`.
The raw recording and machine-readable analysis remain in ignored local evidence
under agents/input001. Original capture retained on the review host. No capture
was altered, controller configuration written, application launched or bench
accessed during this processing. The viewer was already closed at retrieval.

## Eight-bit interpretation

Every captured stick value satisfies `(value + 32768) % 257 == 0`. Thus
`byte = (value + 32768) / 257` is exact for these observed values, and
`value = byte * 257 - 32768` reconstructs them. Each stick visited 123–136
unique values in this short recording, not all 256 possible values; this is
strong evidence for an eight-bit delivered lattice, not exhaustive sensor or
future-driver qualification. Triggers already fit one byte. A future bridge
could offer exact device-profile conversion after verifying that lattice,
with defined fallback for other devices/values. No wire format is selected here.

The viewer's existing eight-bit column is a generic range/centre preview, not
this newly identified device-specific inverse mapping. Preserve that distinction
before comparing its quantization or treating it as the final transport encoder.
No source change to its preview was made during result processing.

## Acceptance boundary

The Author's “looks good” accepts the visible host viewer. Travel, D-pad and
ten button channels have this recorded evidence; Guide, actual reconnect and
calibration review remain open. P4/LAN/EMOS delivery, latency and game behavior
have no qualification from this host capture. The first tranche does not select
protocol/axis precision, authorize target development or establish a production
release. Version/publication closeout remains to be agreed before promotion.


## Guide and reconnect follow-up

The Author supplied a second15.033355914-second recording. All242frames replay
from535raw events, with a clean end and no input gaps. Guide reports one press
and one release. The device disconnects at4.809s and reconnects at9.369s, using
a new session and a freshly queried baseline with no buttons held, no inherited
press counts and no inherited preview calibration. Axis movement after reconnect
produces240reports, proving resumed observation rather than enumeration alone.
The interval between disconnect and reconnect includes the operator's unplugged
time and is not a measured host detection or reconnect latency.

Capture SHA-256:
`4f1b124d6492dc01808444ec68472114589932cad4f68ac321aeb6f5de3fa262`.
Combined with the earlier recording, all eleven XInput button channels now have
press/release coverage. A disconnect while a button remains held was not tested;
no claim of all fault/rearm cases follows. Rest-centre measurement remains
synthetically tested only. The host observation tranche is reviewed; LAN/P4/EMOS
work still awaits its own contract and authorization.

The Author subsequently instructed committing and pushing the reviewed host
utility, then proceeding to LAN contract preparation. No release version/tag
is inferred and no installed firmware or production bundle changes.
