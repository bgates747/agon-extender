# Browser interface for mainboard SD file access

- Status: Accepted
- Completeness: Partial
- Date: 2026-09-27
- Related task: REMOTE-005
- Open-decision tracker: REMOTE-005

## Decision

Use a browser interface for the next human-friendly mainboard SD access work.
Support bulk loose-file transfers with select/deselect all and whole-directory
operations. Prefer reusable embedded-oriented file-manager components where
investigation establishes suitability. No particular library is selected.

The host browser requests operations through P4 HTTP; the foreground EMOSlet
performs mainboard SD operations under EMOS transport ownership. This decision
does not add background access or change the currently required Legacy service.

## Consequences

Preserve the working CLI service. Investigate frontend reuse and mainboard API
gaps before implementation. FTP, SMB and WebDAV remain alternative research,
not selected interfaces. Remaining decisions belong to the linked task.

## Amendment — 2026-09-27 usability review

The browser-first trial produced a mock that the Author found clunky for transfers.
Retain the mock as a fallback; browser backend implementation is not selected.
Final interface selection is reopened in REMOTE-005. Bulk loose-file selection
and whole-directory operation requirements remain applicable to alternatives.
