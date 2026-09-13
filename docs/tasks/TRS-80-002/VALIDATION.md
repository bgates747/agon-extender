# TRS-80-002 sample validation — 2026-09-13

These checks used the extracted ZIP contents, not production files imported
from the surrounding checkout. Package source HEAD is
`5ad7a73d89603ca6647eefa6ebf3191b569c1967`; each archive's manifest identifies
the added task material and the unchanged production sources separately.
Archive SHA-256 values are recorded in [bin/SHA256SUMS](bin/SHA256SUMS).

| Check | Result |
| --- | --- |
| Explicit package contents, ZIP CRC, file size/SHA-256 and byte identity to source | PASS, all three archives; 9 browser, 11 SD and 4 TRS-NET-probe payload files, each plus its manifest |
| Repeat build from identical inputs/HEAD | PASS, identical archive hashes |
| Ten production SD codec/queue/client tests | PASS, macOS x86_64 / Python 3.13.2 and Linux x86_64 / Python 3.14.6; C++ queue test uses address/undefined sanitizers |
| Narrated C++17 queue demo | PASS, both hosts with `-Wall -Wextra -Werror` |
| Included production browser UI regression | PASS, Linux Chromium with WebGL2/SwiftShader: presentation/credit, reconnect, local pattern, no browser key capture |
| README's direct `/?demo` entry | PASS, same browser runtime; `local RGB222 test pattern`, `320×240 RGB222`, at least five presented frames, no page errors or WebSocket connections |
| Browser screenshot | Inspected; generated colour pattern is visible |
| TRS-NET probe against the unchanged pinned upstream script | PASS, Linux / Python 3.14.6; ping, bind/header, reads of sectors 0 and 1, reread of sector 1, echo; exact reply bytes and unchanged temporary volume |
| TRS-NET archive identity checks | PASS, changed-size and same-size/changed-content archives rejected before upstream execution |

Existing development virtual environments were used. No dependency installation
was required. Only the small sample archives and checksum list were copied to the
Linux owned checkout's ignored review area; the upstream reference collection
was not changed. Local scratch output and browser screenshots stay in ignored
`agents/trs80-002-review/` directories.

To repeat the SD checks after extracting its archive, run the commands in its
README. The optional browser regression requires an environment already
containing Playwright and its Chromium runtime; normal demo use only needs
Python's static server and a WebGL2 browser. Package metadata is rebuilt with
`build_packages.py`; changes to packaged files require another build and review
of the resulting hashes.

The TRS-NET probe runs with Python's standard library and a caller-supplied
upstream archive, following its README. The successful run returned byte counts
6, 263, 260, 260, 260 and 256 for the six operations. The original Linux archive's
SHA-256 was checked again after the run and remained unchanged. No archive
image member was extracted, mounted or executed. The probe does not require or
validate a real pyserial installation; its simulated serial module supplies all
input bytes immediately.

These are host checks with synthetic peers. They do not exercise an eZ80
filesystem, physical SD media, UART/flow control, P4 network throughput, guest
boot, a real TRS-NET serial link or unsupported-board firmware. The existing
physical SD acceptance applies only to its separately recorded candidate builds.
