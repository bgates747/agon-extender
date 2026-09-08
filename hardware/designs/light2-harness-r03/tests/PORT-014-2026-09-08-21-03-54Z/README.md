# PORT-014-2026-09-08-21-03-54Z — counting-test SD ready

The Author reported a successful EMOS v0.1.7 flash and returned the SD. The
consumed payload matches `agon-emos-v0.1.7-b2026-09-08-20-53-57Z`. EMNEW.BIN is absent and
verified rollback images remain unchanged. This is an installation report,
not a paired counting-test pass.

The workstation backed up the old boot files, copied the reviewed candidate
EMBOOT/check file and independently built VTEXT sample, then published the
test-only autoexec last. Every copied file was verified and the SD safely
unmounted. Autoexec selects mode 3, runs SD/CLOCK smoke, then the sample;
there is no flash invocation. The sample retains the accepted 250 ms pauses.

P4 candidate `uart-visible-text-probe-r03-b2026-09-08-20-54-40Z` and its matching 11-transaction,
24 MHz / 288-million-sample capture helpers are staged and hash-verified on
the bench host. A read-only check matched the stable USB identity. P4 remains
on r02; no serial open, reset or flash occurred. Physical deployment requires
its separate authorization before the paired test is handed over.

Exact file hashes are in preparation.yaml. Machine-local backups, destination
and staging logs remain in the private bench record. No board test ran during
this preparation.
