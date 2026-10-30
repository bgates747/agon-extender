# Keep diagnostic algorithms outside resident EMOS

- Status: Accepted
- Completeness: Complete
- Date: 2026-10-30
- Related task: DIAG-003

EMOS flash is scarce: the retained installed controller composition has only
270 bytes free. The Author requests that diagnostics live in external utilities
where practical, building on the previous UARTTEST/VDPPOLL/UARTFLOW extraction.

SD utilities own diagnostic sequences, validation, timeout policy and reporting.
EMOS retains minimum admitted UART operations, mode/input ownership and cleanup
when a utility exits. Utilities use the existing EMOS gateway, never direct
UART/GPIO access. Fake hardware adapters belong in external test models rather
than ordinary resident mode routing.

This decision authorizes the extraction design, not a production release or
physical qualification. The owning task records compatibility migration,
implementation and measured ROM savings.
