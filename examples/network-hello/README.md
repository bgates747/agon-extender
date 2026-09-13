# Network hello-world demonstration

Two generated `build/message.h` files select different literal messages and
speech filenames, producing two different `hello.bin` executables. Build with
the project-local Python from the repository root:

```sh
.venv/bin/python examples/network-hello/build_demo.py --toolchain /path/to/agondev --output agents/network-hello
```

For fresh speech, install the optional `requirements-speech.txt` and add
`--speech --jukebox /path/to/AgonJukebox`. The converter uses Jukebox's own
`.venv`, ffmpeg and ffprobe. gTTS's English `co.uk` selection produces the
British-English clips; it exposes no explicit gender selector. Saved clips,
prompts and hashes are retained in the local demonstration bundle.
Generated binaries and WAVs belong in ignored `agents/network-hello`.

`--discord` selects the separate filming greeting (stage 3). Use a fresh output
directory so the first two builds and their evidence remain preserved. This
option prepares assets only; it does not upload, launch, reset or play hardware.

The program uses ordinary MOS file access and standard VDP buffer/sample
commands. WAVs are mono unsigned 8-bit PCM at 16000 Hz, converted and validated
by AgonJukebox's maintained `scripts/make_wav.py`. Short clips load completely
before playback. No Jukebox skin, custom VDP, EMOS change or Extender change is
required. A receipt distinguishes executable execution and audio-command
acknowledgements from the Author's actual visual/listening observation.

The finite boot sequence runs hello, then sdserve, then reloads hello after the
host verifies a replacement and sends the existing EXIT operation. It finally
returns to sdserve. The initial installer must run from the ordinary CLI after
the previous service exits, so it never replaces an open autoexec batch.
It renames the original startup to `/extender/before-hello.txt`, copies the
verified `/extender/hello-boot.txt` into `/autoexec.txt` and executes it. MOS COPY
refuses to overwrite an existing file; this explicit rename is necessary.
An error stops the batch, preserving the original startup and local backups.

After staging and full readback, arm the observer:

```sh
.venv/bin/python scripts/run_hello_demo.py --url http://EXTENDER_ADDRESS --bundle agents/network-hello --output agents/network-hello/hardware-run
```

Only after its readiness message, press Escape at the physical Agon and type
`EXEC /extender/hello-start.txt`. The observer confirms the first execution,
installs the different second executable, preserves the first as `.p17bak`,
and requests EXIT to continue the boot batch. The second program speaks and
returns to sdserve. The script does not overwrite autoexec while that batch is
open. On later boots the current hello binary speaks and then waits in sdserve;
the next batch launch happens only when that service exits.

The host requires the expected stage receipt and successful audio commands.
Human visual/audio confirmation remains separate. No firmware bytes or Rally
files change. See [the task record](../../docs/tasks/DEMO-001.md) for acceptance.
