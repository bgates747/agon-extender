# Accepted native P4 application update

This local update preserves the exact P4 application and controller viewer that
the Author accepted together. It is an application-only update for the existing
P4-PC combination. It is not a fresh-board installer or a selected production
release; `production/current.yaml` remains the installation selection authority.
The bundle's acceptance record identifies the pending version and canonical
qualification gates.

## Verify and preserve

1. Obtain both runtime and source/support archives from the recorded local
   archive directory. Verify external `SHA256SUMS`, extract into a new directory,
   then run `sha256sum -c SHA256SUMS` in each extracted root. The maintained
   `scripts/package_native_p4.py --verify <root>` independently checks inventory
   and rejects missing, changed or additional files. Extraction invokes nothing.
2. Read the current operation protocol, ignored bench description and installation
   guide before any device operation. Verify the P4-PC identity, incoming
   bootloader/partition composition, compatible EMOS and ordinary startup. Keep
   a freshly verified full backup and exact rollback covering all sectors the
   application can erase. Preserve unknown user files.
3. During separately authorized installation, hold Agon reset independently of
   P4. Write only `p4/firmware.bin` at `0x20000`, keeping flash settings and every
   other component. Independently verify application bytes and bytes outside
   the expanded application sectors. Do not write at zero, erase the device,
   replace bootloader/partitions or change `/autoexec.txt`. No factory image or
   full-device backup is distributed in this bundle.
4. Verify the exact P4 startup identity, direct keyboard and onboard-hub F310
   initialization, then release Agon reset and verify actual MOS commands.
   Stop on the first captured crash/repeated startup; preserve journals and
   reconcile the real state before recovery. Input admission alone is not a
   MOS command-execution oracle.
5. The runtime contains the matched viewer under `sd/extender/controller`.
   Preserve an identical installed copy; if absent, separately deploy it under
   `/extender/controller`, hash its readback and leave the card mounted. The
   preserved EMOS endpoint uses operations0–3. Do not substitute the newer
   application include/viewer that requires the reduced EMOS operations4–7.

From an actual MOS prompt, the operator explicitly invokes:

```text
LOAD /extender/controller/ctrlview.bin
RUN &040000
```

The app captures its entry mode, selects mode20 when necessary, settles the
monitor, and restores that entry mode and CLI on Escape. Tests and transfers
never modify startup. Source archives and original embedded build labels stay
unchanged after acceptance. Physical keyboard wiring and host access remain in
current hardware/local records; the archive is not a wiring instruction.
