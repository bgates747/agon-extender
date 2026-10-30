# Native P4 update source and notices

This is a local-only archive of accepted application bytes, with their exact
native source snapshot and build records. It is not a public binary release or
complete public corresponding-source offer. The P4 image embeds the existing
private reset endpoint. Do not publish it or private build manifests/logs.

1. Extender code retains its GPLv3 LICENSE. The native source snapshot preserves
   selected VDP/vendor/managed-component source and their original notices.
2. Espressif USB1.6.0 is retained as its exact original archive, license, pinned
   component inventory and local derivative recipes in the source snapshot.
   Selected IDF5.5.5, PHY/HAL and compiler identities remain in the build manifest;
   compilers are obtained separately. Do not claim this archive replaces every
   external SDK/tool prerequisite.
3. The included old-ABI viewer is the exact matched AgonDev fixture. Its source
   commit is recorded independently; EMOS/listener/mainboard VDP are preserved
   prerequisites and are not new payloads in this P4 application update.
4. No bootloader, factory image, mutable NVS/OTA content, startup, full-device
   backup, credentials, sudo configuration or compiler is distributed here.
5. Preserve both runtime and source/support archives. Broader publication requires
   source/license review; existing production notices retain the separate
   historical installation's review and obligations.
