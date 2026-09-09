# Diagnostic preparation failure — 2026-09-09

After the verified r02 deployment, the agent's browser failed to receive the
expected frames. The separate diagnostics request reset its TCP connection.
This check never reached operator typing and has no separately recorded start
timestamp. It is not a reproduction of the Author's original r01 failure.

Passive serial capture shows a P4 stack-protection panic during snprintf:

```text
Guru Meditation Error: Core 1 panic'ed (Stack protection fault).
MEPC: 0x400d0110  RA: 0x400c67ce
```

The exact r02 ELF resolves those addresses to newlib `_svfprintf_r` and
`snprintf`. Disassembly shows the diagnostic handler reserving 208 + 2032 =
2240 bytes on the default 4096-byte HTTP stack. The 2048-byte automatic export
buffer is allocated even on early control-request paths. The r03 correction
moves it into checked heap storage only for after-run export; its handler
reserves 208 stack bytes. Ordinary HTTP task size and measured-path timeout,
UART and snapshot policies stay unchanged.

Keep the exact r02 candidate and passive capture in the ignored local timing
record. This informative instrumentation failure must not be silently dropped
or counted as an operator setup mistake. Recheck the actual P4 handler and
video before handing the replacement measurement candidate to the Author.
