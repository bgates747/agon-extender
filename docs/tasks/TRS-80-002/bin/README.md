# TRS-80-002 sample bin

**Experimental source samples — approved for publication.** These are small source
kits to try on a development computer without Extender hardware. Extract a ZIP
and start with its `README.md`.

| Package | What you can try | Requirements |
| --- | --- | --- |
| [TRS-NET upstream-server probe r01](agon-extender-trs-net-probe-r01.zip) | Six exact-reply read/control checks against Daniel's unchanged server, using simulated serial input and a temporary volume | Python 3.10+, caller-supplied pinned upstream `TRS-NET.zip`; tested on Linux |
| [Browser video demo r01](agon-extender-browser-demo-r01.zip) | Animated local RGB222 pattern through the actual EVF1 parser and WebGL2 page | Python 3.10+ to serve files, WebGL2 browser |
| [Mainboard-SD transport lab r01](agon-extender-sd-lab-r01.zip) | Narrated queue/retry example and ten production codec, queue and client tests with synthetic peers | Linux/macOS, Python 3.10+, C99/C++17 compilers; compiler sanitizer runtimes for the queue test |

All three include source, the full GPLv3 license, the project licensing policy and a
`manifest.json` recording each included file's origin, size and SHA-256. They
contain no firmware or guest disk images. Passing host tests does not establish
TRS-OS interoperability or support for another board. The SD lab does not supply
the separate EMOS/FatFS service or speak TRS-NET; the browser demo is video-only.
The TRS-NET probe requires Daniel's archive separately and does not redistribute
its source or disk images. Its tests do not qualify guest boot, writes or a
physical serial connection.

Verify downloads against [SHA256SUMS](SHA256SUMS), for example with
`sha256sum -c SHA256SUMS` on Linux or `shasum -a 256 -c SHA256SUMS` on macOS.
Rebuild from the repository with an existing Python development environment:

```sh
.venv/bin/python docs/tasks/TRS-80-002/build_packages.py
```

The builder reads only explicit source allowlists, preserves production files
unchanged, and emits deterministic archives for the same input bytes and HEAD.
The task's source README files and queue example are maintained beside it.

See the [community guide](../COMMUNITY-GUIDE.md) for the broader discussion and
[TRS-80-002](../../TRS-80-002.md) for review state and validation evidence.
