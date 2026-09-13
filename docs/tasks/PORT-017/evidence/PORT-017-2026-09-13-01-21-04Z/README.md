# Hardware transfer result — 2026-09-13 UTC

Ten consecutive network/P4/UART1/EMOS/SD upload, verify, activate and readback
cycles pass without card movement or board reset. The previous target is also
read back and compared before backup cleanup. The committed host controller
source hashes still match the inputs recorded at run start; concurrent changes
were confined to separate headless/keyboard fixtures and documentation.

Physical checks also pass for invalid paths/transfers, busy/sequence/session
errors, bad wire CRC, early FINISH, cancellation, file CRC failure and explicit
orphan recovery. One successful HTTP WRITE response was withheld from the host
client before durable acknowledgement; exact saved-request replay passes. This
is host response-loss injection on the physical path, not a severed UART wire.

The unchanged candidate additionally passes actual raw-FAT exhaustion: a
26624-byte partial file remains, FR_DENIED is reported, the old target survives,
and explicit recovery permits another verified upload. Write/close/sync/rename
fault injection remains host-engine evidence. Physical power-loss/media-error
qualification is not claimed.

Native-keyboard interruption and typed restart remain the final physical
observation. Full PORT-017 acceptance is not inferred from these transfer passes.
