# Firmware rollback protocol

Restore the component the Author names to an exact retained, verified working
build. A rollback is not a source reset, a new feature implementation or an
implicit replacement of every component on the bench.

## RB-01 — Select and bound the rollback

1. Identify the named component, the failure being avoided, its last physically
   verified applicable build and the retained image/hash/evidence. “Latest,”
   version labels and a successful compile alone do not identify that build.
   Preserve source changes and experimental artifacts; do not discard Git work.
2. Record current installed components and startup separately. Preserve unknown
   user files, mainboard VDP, wiring and all unnamed components. Use retained
   verified rollback artifacts where available; do not make redundant firmware
   backups merely by habit.
3. Keep mode boundaries explicit. Legacy/ExCom use ordinary UART behavior;
   ExExt parallel activation must not be a prerequisite for their operation.
   Do not call an implementation's unwanted cross-mode coupling a legitimate
   compatibility requirement. An EMOS-only rollback leaves the P4 installed.
4. If another component demonstrably blocks the rollback or ordinary operation,
   record the evidence and report the defect. Do not silently roll it back,
   rewrite it or make the defect disappear through a paired substitution.

## RB-02 — Recover access and install

1. Read the reset protocol before recovering input. Prefer the Author-specified
   established recovery sequence when applicable. Do not require card removal
   before trying the authorized ordinary recovery path. Inspect active startup
   first: a recovery reset must not silently launch a test.
2. At an admitted prompt, restore ordinary startup and disable test auto-start
   before an installation that reboots. Preserve identified test configurations
   for subsequent explicit restoration. If access is unavailable, explain the
   exact blocker before asking for a physical operator action.
3. Follow the installation protocol and the component's exact flash layout.
   Stage/read back the named EMOS image before invoking its flash command.
   For P4, preserve mutable partitions and write only the selected verified
   segments. No blanket erase, unrequested component flash or uncertain replay.
4. Verify the installed image independently, then verify boot, ordinary CLI and
   input readiness separately. Record what was actually proved. A FLASH command
   submission or ready keyboard bit is not a full-ROM verification.
5. Stop with the requested component restored and the actual terminal state
   recorded. Re-running tests, resuming a benchmark or repairing an unrelated
   component requires its own authorized operation.
