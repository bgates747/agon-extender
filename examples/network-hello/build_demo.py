#!/usr/bin/env python3
"""Build two distinct hello executables; optionally synthesize compatible speech.

Run with the Extender project .venv/bin/python. Speech uses gTTS 2.5.4 and the
AgonJukebox project's own converter/environment. No hardware is contacted.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

EXAMPLE = Path(__file__).resolve().parent
STAGES = [
    (1, "Hello world - build one", "The first executable has arrived.",
     "attention", "The host will replace this program shortly.", 25),
    (2, "Hello again - build two", "The executable on the card has changed!",
     "updated", "Same card. New code. No reset for this update.", 15),
]
SPEECH = {
    "attention": "Hello world. Your Agon is speaking. Your attention is required. Please watch the screen.",
    "updated": "Hello again. New program, same card. Updated over the network, without touching the hardware.",
}
DISCORD_STAGE = (3, "Hello, Agon Discord!", "A proper British hello to all our friends.",
                 "discord", "Cheers, lads - and happy hacking!", 35)
DISCORD_SPEECH = ("Hello to all my friends on the Agon Discord! This is a real Agon speaking. "
                  "My voice arrived over Ethernet, straight onto the SD card. "
                  "Cheers, lads, and happy hacking!")
KEYBOARD_STAGE = (4, "Your remote keyboard is ready", "The Agon can now receive host keystrokes.",
                  "keyboard", "Reply in chat when you are ready to watch me type.", 2)
KEYBOARD_SPEECH = ("Your Agon's remote keyboard is ready for inspection. "
                   "Please reply in the chat when you are ready to watch me type. "
                   "I'll wait for you. No need to leave the couch.")
KEYBOARD_FIXED_STAGE = (5, "Keyboard timer fixed", "The corrected firmware passed its hardware tests.",
                        "keyfixed", "Reply in chat when you are back at the bench.", 2)
KEYBOARD_FIXED_SPEECH = ("The clock gremlin is fixed. Your Agon is ready again. "
                         "Please reply in the chat when you're back at the bench.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--toolchain", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--speech", action="store_true")
    parser.add_argument("--discord", action="store_true", help="Build only the filming greeting")
    parser.add_argument("--keyboard-review", action="store_true", help="Build the remote-keyboard review cue")
    parser.add_argument("--keyboard-fixed", action="store_true", help="Build the corrected-keyboard review cue")
    parser.add_argument("--jukebox", type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    (EXAMPLE / "build").mkdir(exist_ok=True)
    manifest = {"status": "unversioned development demonstration", "builds": []}
    if sum((args.discord,args.keyboard_review,args.keyboard_fixed))>1:parser.error('Select one greeting')
    stages = [KEYBOARD_FIXED_STAGE] if args.keyboard_fixed else [KEYBOARD_STAGE] if args.keyboard_review else [DISCORD_STAGE] if args.discord else STAGES
    speech = {"keyfixed":KEYBOARD_FIXED_SPEECH} if args.keyboard_fixed else {"keyboard":KEYBOARD_SPEECH} if args.keyboard_review else {"discord": DISCORD_SPEECH} if args.discord else SPEECH
    for stage, title, message, voice, next_text, hold in stages:
        header = (f'#define HELLO_STAGE {stage}\n#define HELLO_TITLE "{title}"\n'
                  f'#define HELLO_MESSAGE "{message}"\n'
                  f'#define VOICE_PATH "/extender/{voice}.wav"\n'
                  f'#define HELLO_NEXT "{next_text}"\n#define HOLD_SECONDS {hold}\n')
        (EXAMPLE / "build/message.h").write_text(header)
        target = output / f"build-{stage}"
        target.mkdir(exist_ok=True)
        (target / "message.h").write_text(header)
        subprocess.run(["make", "AGONDEV_TOOLCHAIN=" + str(args.toolchain.resolve())],
                       cwd=EXAMPLE, check=True)
        for name in ("hello.bin", "hello.map"):
            shutil.copyfile(EXAMPLE / "bin" / name, target / name)
        data = (target / "hello.bin").read_bytes()
        manifest["builds"].append({"stage": stage, "bytes": len(data),
                                   "sha256": hashlib.sha256(data).hexdigest()})
    if args.speech:
        if not args.jukebox:
            parser.error("--speech requires --jukebox")
        from gtts import gTTS
        audio = output / "audio"
        audio.mkdir(exist_ok=True)
        for name, text in speech.items():
            gTTS(text=text, lang="en", tld="co.uk", timeout=(5, 20)).save(str(audio / (name + ".mp3")))
        jukebox = args.jukebox.resolve()
        subprocess.run([str(jukebox / ".venv/bin/python"), str(jukebox / "scripts/make_wav.py"),
                        *[str(audio / (n + ".mp3")) for n in speech],
                        "-o", str(audio / "wav"), "--sample-rate", "16000", "--compress"], check=True)
        manifest["speech"] = {"engine": "gTTS 2.5.4", "language": "en", "tld": "co.uk",
                              "text": speech, "format": "RIFF/WAVE, PCM u8 mono, 16000 Hz"}
    (output / "builds.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
