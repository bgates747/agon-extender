# Paired graphics P4 candidate deployed

P4 console r04 from clean source `7943789` passed flash/readback verification.
Startup identified the candidate and enumerated the native USB keyboard; the
browser service started without a startup fault. These observations establish
installation only. Physical paired graphics comparisons remain pending under
[the test sheet](../paired-graphics-probe-r01.md).

EMOS `agon-emos-v0.1.12-b2026-09-10-03-50-35Z` is staged on the SD, with SHA256
`2c261e290cd3e9af44a168775eabef4a514cf3262d9391fc4ce3dfe414ed5a77`.
Its 130219-byte image leaves 853 bytes below 128 KiB. The working v0.1.11
payload is preserved as `EMPREV.BIN` and in an off-card backup. The one-shot
MOS installer is the only active startup; the Author must confirm its result
before graphics startup replaces it.

Fixture `paired-graphics-probe-r01-b2026-09-10-03-50-35Z` runtime files and the
matching EMOS boot smoke are staged and hash-verified. The SD was safely
unmounted. No Agon reset, Agon flash or physical graphics pass is claimed.
Full logs, build manifests and SD receipts remain in the ignored local bench
records; their machine-specific paths and device identities are not published.
