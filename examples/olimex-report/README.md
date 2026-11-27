# Olimex report writer example

This example writes a short report using the proposed BENCH-025 protocol.
It is a host-qualified reference for fixture authors. Physical qualification
and the Nurples pilot are separate.

Build the executable using the project AgonDev SDK and inspect its linked
map. Call `olx_report_token(argv[1])` before starting the workload. Call
`olx_report_save()` outside the timed region. The helper exclusively opens
the absolute path, writes the attempt envelope and the payload, closes the
file, and prints the status line. It needs no firmware changes.

```bash
make -C examples/olimex-report AGONDEV_TOOLCHAIN=/path/to/agondev
```

See the [packet contract](../../docs/operations/olimex-bench/REPORT-LIFECYCLE.md)
for the manifest, serial grammar, validator arguments and recovery commands.
Use the installed firmware receipts from the actual approved pilot when
preparing its manifest. Keep build outputs and physical evidence outside Git.
