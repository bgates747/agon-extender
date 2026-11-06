# Wi-Fi BBS host checks

Eight real TCP test methods pass. This qualifies the Pi candidate's text and
persistence behavior only; Console8, Wi-Fi/module AT compatibility, UART input
and manual cleanup still require Smith's test. No emulator or physical target
was accessed.

Command: `.venv/bin/python -m unittest discover -s tests -p test_wifi_bbs.py -v`.
Recorded result: 8 methods, 0.286 seconds, PASS on 2026-11-05 America/New_York.
Python 3.14.6; standard-library server dependencies.

| Check | Evidence |
|---|---|
| Command handling | help, actual clock, host/service uptime and unknown commands |
| UART-like input boundaries | Fragmented CRLF, backspace and multiple pipelined lines over real TCP |
| Persistent notes | Saved notes survive actual server close/restart; last-three display ordered correctly |
| Admission | Second active client refused while first remains usable |
| Input recovery | Overlong/non-ASCII lines refused without saving partial notes; next command works |
| Session exit | quit closes TCP; reconnect and partial EOF handled |
| Service exit | Connected client closes, durations recorded and all handlers joined |
| Actual CLI | Ready receipt binds PID/build; SIGTERM exits cleanly and records service end |

| Selected file | SHA256 |
|---|---|
| `scripts/wifi_bbs.py` | `d979cd4cc7fb0449819b68f029403e787589fc24ea570f35ffc7a47fea9392e7` |
| `scripts/build_wifi_bbs_package.py` | `7808dcb85250a9b11fed5c983ceeb1e08ac266a808655b46bd0826c5945c24e8` |
| `tests/test_wifi_bbs.py` | `fd65f6a86f0d872be81662017926e88a6163f8328bff2ebb611dc30b1af66660` |
| `docs/tasks/NET-005/USING.md` | `c1050cd265fac2f34a126f3d00318fb5624ff757910c679a5cd55e6d8b685fe7` |

The package builder is syntax-checked here; its actual generated/archived-member
comparison is recorded separately after committed source is packaged.
