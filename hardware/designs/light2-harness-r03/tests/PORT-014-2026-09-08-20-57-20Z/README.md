# PORT-014-2026-09-08-20-57-20Z — guarded EMOS install SD ready

The Author accepted graphical pacing and requested SD deployment. EMOS source
is frozen in `026ac46`; the coordinated sample/P4 source
is frozen in `18024d8`. Clean candidate builds and automatic same-build checks
pass. The mounted SD was prepared and verified with EMNEW.BIN and the
rename-before-flash autoexec, then safely unmounted. No board flash/reset was
performed by the agent.

EMOS: `agon-emos-v0.1.7-b2026-09-08-20-53-57Z`, 122645 bytes,
CRC32 **F61FA518**. The operator inserts the SD, presses powered Agon reset once,
and confirms the updater reports Done. After installation, return the SD for
the separate smoke/counting-test autoexec. P4 deployment remains separate.

Working v0.7.0 is preserved as EMPREV.BIN; v0.6.0 is archived as EMV060.BIN.
Older rollback files remain unchanged. Verified off-card backups and exact
machine-local preparation details are retained privately. The installer uses
`FLASH mos EMDONE.BIN -f`, with the payload renamed first to prevent automatic
reflash on a subsequent reset. The retained test-autoexec file is a later
handover definition; the active card currently runs only the installer.
