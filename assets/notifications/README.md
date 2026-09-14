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
