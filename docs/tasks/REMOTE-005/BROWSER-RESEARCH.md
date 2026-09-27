# Browser file-manager investigation

Initial discovery: 2026-09-27. Research only; no library selected or tested.

## Accepted direction

Browser transfers, bulk loose-file selection with select/deselect all, and
whole-directory operations. The browser should orchestrate the existing P4 HTTP
and EMOSlet service; EMOS retains transport ownership. Lifecycle remains open.
Authoritative checklist: [REMOTE-005](../REMOTE-005.md), R05-B01–B06.

## Initial shortlist

These are upstream README claims, not source-verified feature guarantees.
Repository API license labels are preliminary; inspect actual license texts and
bundled dependencies before reuse. No source has been vendored into the product.

| Candidate / pinned revision | Relevant claims | Initial integration question |
| --- | --- | --- |
| [ESPFMfGK](https://github.com/holgerlembke/ESPFMfGK/tree/ac3b699c35705d34df06ed4a978fb5add4310463) | ESP32 file manager, multiple filesystems, file operations and recursive ZIP download | Attractive embedded UI lead; license API returns NOASSERTION, so actual terms need inspection. Replace local filesystem assumptions with remote service adapter. |
| [esp-fs-webserver](https://github.com/cotestatnt/esp-fs-webserver/tree/502f2f3438f076e70c8563a5f7ec5c36b0feea89) | Embedded file/folder browser and editor; synchronous Arduino WebServer | Apache-2.0 API label; examine frontend separation. Includes unrelated Wi-Fi/OTA facilities; do not import these wholesale. README refers to externally maintained page sources: establish rebuild provenance. |
| [ESP32-File-Server](https://github.com/CyberXcyborg/ESP32-File-Server/tree/63708837464d3d5587761f7584d4e796dc1f30f4) | Folder upload, multiple-file ZIP download, file/folder create/move/copy/rename/delete | MIT API label; closest advertised operations. Verify implementation, dependencies and resource bounds before ranking as a recommendation. |

## Mainboard service gap

The [current wire contract](../../protocols/mainboard-sd.md) exposes listing,
stat, file reads, staged writes/activation, cancellation/recovery and exit.
It does not expose general mkdir, rename, unlink or rmdir commands. A browser
can queue existing file transfers, but uploading a new directory tree and wider
directory management need additional mainboard service operations. Internal
rename/delete used by write recovery are not general client operations.

Current limits include ASCII paths of 120 bytes and staged targets of 112 bytes.
Any reused UI must report these limits instead of promising unrestricted desktop
filesystem semantics. Bulk operations need per-file results; current transaction
handling does not make an entire directory transfer atomic.

## Next evidence needed

Complete R05-B03–B06 before choosing a framework. In particular verify actual
select-all semantics, recursive transfer coverage, empty folders, browser download
permissions/fallbacks, cancellation and memory use. No performance or browser
compatibility tests have yet been performed. D03 is deliberately unanswered.
