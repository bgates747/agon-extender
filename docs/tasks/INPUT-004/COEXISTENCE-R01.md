# Keyboard and controller coexistence

Restore the F310 on the P4-PC onboard USB hub while retaining the working
keyboard on the directly wired full-speed USB port. The installed keyboard-only
selection enables one controller. Espressif supplies a focused dual-host change;
backport that change into generated build output and qualify both input clients.
Keep EMOS, mainboard VDP, startup and existing display behavior unchanged.

## Authority and bounded research

1. On 2026-10-30 the Author directs controller/keyboard coexistence. INPUT-004
   already owns this unfinished integration. This selects implementation and a
   bounded P4 deployment/input check; it does not resume rendering campaigns or
   the separate INPUT-005 application/EMOS deployment.
2. The current direct-FS P4 source is `fd212503e34eb19761d59bc919f68bdda02b3954`.
   Use that matched display/transport composition, not a different renderer at
   repository HEAD. The ignored bench record owns exact artifacts, devices,
   wiring, reservation, URLs and rollback. Preserve an independently verified
   incoming P4 image before changing app sectors.
3. Pinned ESP-IDF 5.5.5 `b774170ff46c393eeb5e495ea37936038d3f4f4f`
   `components/usb/usb_host.c` configures one PHY even though HCD and root-hub
   layers accept multiple peripheral bits. Setting map3 alone is insufficient.
   The [pinned guide](https://docs.espressif.com/projects/esp-idf/en/v5.5.5/esp32p4/api-reference/peripherals/usb_host.html)
   explicitly identifies the one-host limitation.
4. Espressif [PR402](https://github.com/espressif/esp-usb/pull/402), commit
   `48b250fa36e92c64a37c333dc548c84cb48c6eac`, merged as
   `5d6ace9fbf86d00578bbc133e28306e8001ffca7`, adds per-port PHY handles,
   initialization and cleanup, map validation and default FIFO selection for
   dual hosts. It does not replace the USB report clients or require a new
   transport protocol. Adapt these changes to the pinned older source layout;
   do not replace the SDK or fake optional HAL capabilities.
5. The HS-capable port still needs the already reviewed FS/LS-only restriction
   for the onboard hub/F310. That existing HCD backport applies only to the
   HS-capable controller. The separate direct FS PHY retains normal low/full
   speed handling. Both ports use existing interrupt priority/default FIFO
   settings; no speculative custom FIFO or physical rewiring is selected.
6. Official MOS keyboard contracts remain unchanged. P4's existing HID client
   owns keyboard acquisition; its existing XInput client owns F310 acquisition.
   EMOS retains UART input admission and routing. Application controller APIs
   and physical USB acquisition remain distinct responsibilities.

## Implementation and validation gates

1. [ ] Add a source-hash-pinned generated USB host derivative with correct
   per-port cleanup on second-PHY/HCD failure and uninstall. Preserve the SDK
   checkout; record upstream origin, adaptations and removal condition beside
   the recipe. Reject unreviewed source drift.
2. [ ] Add explicit P4-PC/console dual-host build selection, excluding the
   keyboard-only direct-FS selection and requiring the existing HS FSLS remedy.
   Record map3 and the actual compiled host derivative in manifests/validator.
   Reset the onboard hub only for selections that actually service it.
3. [ ] Apply the same bounded source change to the retained matched P4 source,
   preserve all display/transport/board/dependency inputs, and produce a fresh
   clean identified experimental build. Verify actual compile/archive/link
   selection and pre-v3 guards. Run relevant offline input/build checks.
4. [ ] Verify fresh bench state and actual CLI, read unchanged setup-only
   startup, retain rollback, then write only authorized P4 application sectors.
   Independently read back the app and untouched flash, initialize P4 before
   releasing/resetting Agon, and establish fresh input/actual CLI. Do not modify
   EMOS, mainboard VDP, SD startup or an unrelated application.
5. [ ] Verify direct keyboard HID admission and native F310 reports while both
   clients run. Stage the already matched controller viewer if needed; preserve
   its mode lifecycle. Actual physical key/controller exercise and visible
   smoothness require Author review. Ask in chat only for missing attachment or
   physical actions, preserving the keyboard-only rollback if coexistence fails.
6. [ ] Close all unnecessary readers/input sessions, leave a responsive CLI or
   explicitly identified review application, record exact final bytes/results
   and update current bench/task guides. Production/version promotion remains
   governed by later Author acceptance and agreed release identity.

This bounded continuation makes no simultaneous-device pass or byte-saving
claim before measurement. No controller checksum, generic packet tunnel, extra
EMOS diagnostic or application policy is introduced.
