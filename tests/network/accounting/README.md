# Optional message accounting checks

These checks execute the actual message worker, peer and socket code with local
host adapters. They create no external TCP connection, UART access or firmware
installation. Run them through the normal serial compiler reservation. Address,
undefined-behavior and leak sanitizers remain enabled; use native host execution
because LeakSanitizer cannot inspect a process under the sandbox's ptrace.

```sh
.venv/bin/python tests/network/accounting/check.py \
  --output FRESH_OUTPUT --baseline-root INSTALLED_SOURCE_CHECKOUT
```

The baseline source must identify the retained uninstrumented UART carrier. The
checker joins every modified source input in its report, compares enabled/OFF
socket and CONNECT replies, exercises concurrent snapshots, and compares the
actual default-OFF socket object's relocation-bearing disassembly at Os and O2.
Target linking and physical execution are separate evidence.
