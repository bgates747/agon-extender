# Wi-Fi BBS manual-test readiness

The Pi side is implemented, packaged and running. Eight host tests pass; a
separate live host connection exercised all six commands on the packaged
listener. Console8/ESP8266 physical compatibility and clean modem escape remain
unverified. Use [the manual walkthrough](USING.md); do not infer a physical pass.

| Item | Identity / result |
|---|---|
| Plan published before code | `730431f2` |
| Implemented source | `188cfb74717f6810eebef30d2c519513cff72374` |
| Experimental package | `wifi-bbs-r01-b2026-11-06-04-03-51Z` |
| ZIP SHA256 | `48c1a8c7a2000f23a1ff92dd07396e5dfa593eb502622c8d0984471704bc8cbd` |
| Client | Radiotux original `minicom.bin`, 23407 bytes; no local build or patch |
| Package verification | Every generated and ZIP member compared exactly |
| Host tests | Eight actual loopback methods pass, including persistence and CLI/SIGTERM |
| Live listener check | help/time/uptime/note/notes/quit pass; exact banner/PID/source |
| Physical testing | Pending Smith; no remote Console8 access |

The package and adjacent checksum are retained under `dist/wifi-bbs/`. Private
listener endpoint/process/data/stop details remain in `agents/net005/live/`.
Service and session durations are recorded in its append-only event log. Notes
remain in its SQLite file when the explicitly stopped service is restarted.
No production selection, firmware update, Codex bridge or auto-start service was
created.
