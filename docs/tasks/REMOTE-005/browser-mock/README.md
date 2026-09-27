# Browser file-manager mock — R05-P01

Local, static usability preview. No P4/Agon connection, firmware changes, actual
transfers or file-content reads. File pickers inspect only names, sizes and
relative paths. Queue progress and service states are simulated. Reload resets
all state. New folders affect only the synthetic tree.

## Run

From the repository root:

```sh
.venv/bin/python -m http.server 8765 --bind 127.0.0.1 --directory docs/tasks/REMOTE-005/browser-mock
```

Open http://localhost:8765. For another LAN machine, explicitly bind the server
to an appropriate host interface; serve only this mock directory. This is a
short-lived development preview, not a deployed service.

## Review

1. Open `stress`: 128 files and an empty folder. Filter and select/deselect all.
2. Select a folder from its parent and download: queue includes the folder tree
   and empty directories. It represents a future ZIP download; creates no ZIP.
3. Cancel remaining work, then retry incomplete. Completed entries stay complete.
4. Under Preview controls, simulate busy/offline or fail the next item once.
5. Choose local files/folder to inspect the simulated upload queue. Browser folder
   input lists files; empty folders cannot be inferred. The UI discloses this
   limitation; complete directory import remains later implementation work.

Filtering and navigation clear selection to avoid invisible selections. Select
all applies to all matching entries in the current fully loaded directory.
The mock intentionally loads the entire 129-entry stress listing; paginated
backend loading will need to preserve this visible contract.

## Provenance and reuse boundary

Layout/interaction adaptation informed by Holger Lembke's ESPFMfGK, revision
ac3b699c35705d34df06ed4a978fb5add4310463, particularly filemanager/fm.html,
fm.css and fm.js (path navigation, file list, status and serial upload idioms).
Upstream: https://github.com/holgerlembke/ESPFMfGK/tree/ac3b699c35705d34df06ed4a978fb5add4310463
Full upstream notice retained in LICENSE.upstream.md.

This mock rewrites presentation and orchestration for synthetic data; it does
not integrate the upstream runtime or claim framework integration is complete.
No upstream C++ server, optional gzip-js, CDN assets or other library is loaded.
CSP disallows fetch/WebSocket connections. Production service adapter, archive
library, real mkdir/move/delete, lifecycle and ownership policy remain outside
P01. See ../BROWSER-RESEARCH.md for the subsequent proposed work.

## Validation — 2026-09-27

`test_mock.py` passed using Playwright Chromium 151.0.7922.34 on Linux:
129-entry listing, filtered select/deselect, recursive queue including empty
directory, cancellation/retry, offline/busy pause, injected failure/retry,
synthetic upload metadata, filename text rendering, and 390-pixel mobile width.
No JavaScript exceptions. Desktop and mobile screenshots retained locally;
desktop rendering visually inspected. No Firefox/Safari or physical-browser
acceptance claim. Timers simulate progress, not transfer performance.

Run with the static preview above:

```sh
.venv/bin/python docs/tasks/REMOTE-005/browser-mock/test_mock.py
```

License clarification: the retained upstream notice includes a Siemens exclusion
and is not standard MIT. This mock has new implementation code; production reuse
of upstream code is not approved by this preview. See the research correction.
