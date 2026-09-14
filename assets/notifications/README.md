# Reusable hardware attention audio

`extender-attention.wav` says: **“The Extender agent requires your attention.”**

Requested by the Author as the standard spoken notification. Uses the same
British English gTTS settings as the earlier accepted female-sounding bench
alerts: English, `tld=co.uk`. The service does not expose a stable named voice
or gender selector. Preserve the generated WAV for a consistent recurring cue;
a future synthesis request is not guaranteed to return identical audio.

The WAV is standard AgonJukebox-compatible unsigned 8-bit mono PCM at 16 kHz,
converted with the existing Jukebox tool and its compression filter. Exact
transcript, duration and digest are in `extender-attention.json`.
RIFF headers/chunks must be parsed; do not treat byte 44 as a fixed data offset.

Regeneration uses Extender's `.venv` with gTTS 2.5.4 to save the transcript as an
MP3 with `gTTS(text=..., lang="en", tld="co.uk", timeout=(5,20))`, then the
sibling AgonJukebox `.venv/bin/python scripts/make_wav.py` with the MP3 input,
an output directory, `--sample-rate 16000 --compress`. Keep intermediate MP3s
under ignored `agents/`, and retain previous WAVs before regenerating.

Preparing this asset does not deploy it, alter startup, interrupt an application
or play it. Use the existing hardware playback path when the foreground state
permits it; record actual playback separately. The EMOS supervised review gates
remain in force.

## Installed bench playback

Tested on the physical Agon on 2026-09-14 UTC. From the ordinary Legacy MOS
prompt, `EXEC /extender/attention.txt` runs `/extender/attention.bin`, plays
`/extender/attention.wav` once, then starts the foreground SD service. The host
can collect `/extender/hello-seen.txt` and exit the service to return to MOS.
Do not issue this while an application owns the foreground.

The existing `examples/network-hello/src/main.c` player was reused unchanged,
with generated message constants for stage 6 and zero post-playback hold.
VDP audio acknowledgements passed and the player returned to the service;
human hearing confirmation is pending. Both files were fully read back after
deployment. Root startup and firmware were unchanged. The test then exited
the SD service, leaving the MOS prompt.

Private build, deployment and execution receipts are retained under
`agents/attention-audio-2026-09-14/`. Player SHA-256:
`83db4034a6e955ca56a950f5650991a58a789416f2a81aef793471bc803ffcf2`.
