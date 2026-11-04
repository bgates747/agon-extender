# Native VDP preservation-read triage r01

Wolf completes69 SD deployments/13928431 bytes, then its first full native-VDP
backup read fails with truncated esptool data at460800 baud. No erase/write
occurred. This self-assigned bench support action helps the consumer preserve
its incoming firmware without taking over its source or physical checkout.

1. Preserve the failed read log and exact no-write disposition. Input admission
   is ready after esptool's ordinary RTS reset; offline SD alone is expected when
   the foreground listener is stopped. Do not call this a parallel-payload fault.
2. Reuse retained verified rollback where applicable. The saved4194304-byte
   incoming image hashes17caa5b0; its selected application1094512B hashes8ade1e7d.
   Host bytes are rehashed now. This does not establish current device equality.
3. Wolf transfers exclusive repair custody; Extender performs one deliberate
   read-only whole-image verification at115200 baud against that retained image,
   with normal setup-only startup, exclusive port and no blanket erase/write.
4. Only a successful fresh complete verify permits reusing the retained full
   image as exact incoming rollback under the existing deployment plan. A
   mismatch/transport failure stops dispatch; preserve differences and arrange
   exclusive repair custody rather than flash or assume mutable sectors match.
5. This advice selects no new firmware and changes no source, wiring, startup,
   SD mount or application-start budget. Full installation and restoration remain
   Wolf's existing authorized finite plan; source changes belong to that owner.

Cause of the truncated USB/stub reply is unknown. Lower speed/short reply
verification is a bounded diagnostic, not proof of hardware noise or a USB fix.

## Outcome

The host rollback rehash passes. One115200-baud esptool verification then
compares every byte of the current4MiB native flash successfully against the
retained exact image. No erase/write or new full host read occurs. This binds
the retained whole image, including mutable sectors, to the incoming device
state and avoids another bulk read. The consumer's existing installation plan
can use it as exact rollback after preserving its hash and verification receipt.

Normal esptool RTS reset occurs; actual CLI/listener/read/EXIT, unchanged startup
and utilities, neutral input, idle worker and free USB endpoints pass afterward.
No P4 reset, firmware change, app start, SD unmount or wiring change occurs.
Central return-repair plus durable mail and immediate steering restore Wolf's
custody with a fresh token. First failed460800 read remains informative evidence.
Because both baud and operation changed, this pass does not identify a baud
limit, electrical cause or permanent USB remedy. Bounded preservation unblock
is complete; no new firmware defect is established.
