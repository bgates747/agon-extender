# Private direction-isolation MOSlet

Adapted from the retained parcheck fixture; unchanged EMOS API51h request and
assembly binding. Only EMOS owns transport/GPIO operations. No display-mode
change, startup modification, timing hooks or direct GPIO access.

Build with the selected AgonDev toolchain:

```sh
make AGONDEV_TOOLCHAIN=/path/to/agondev/release
```

After deliberately installing the matched independent-direction P4 comparison
build and prior EMOS admission, invoke at the MOS CLI:

```text
EMOS pariso forward /agents/extender/results/FRESH-FORWARD.CSV
EMOS pariso reverse /agents/extender/results/FRESH-REVERSE.CSV
```

Install `bin/pariso.bin` as `/emos/pariso.bin`; verify the deployed bytes. Each
invocation performs exactly one1024byte operation. Forward CSV reports completion
and guards only; P4's post-receipt USB record establishes received-byte integrity.
Reverse uses a locally generated P4 source and compares every received Agon byte.
An existing result is refused. Invoke the second direction only after verifying
completed transport cleanup/readiness from the first. Never automatically replay
an uncertain operation. This is not a production interface or routine SD service.
