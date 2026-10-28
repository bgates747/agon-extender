# Mainboard USB serial capture

Use the maintained host opener for Agon Light2 USB capture. The ordinary
pyserial setup that clears DTR and RTS separately can reset the board while
opening an apparently passive monitor. The corrected opener clears both controls
in one driver operation. On the tested Linux/CH341 combination, three open/close
trials preserved input, and one ordinary reset recovered input on its first pulse.
This is bounded host-adapter qualification, not a universal no-reset guarantee.

## Capture command

Read the operation protocol and local bench record first. Select the stable
mainboard USB endpoint from that record, and a new output path:

```sh
.venv/bin/python scripts/serial_monitor.py \
  --port "$MAINBOARD_SERIAL" --output "$CAPTURE_OUTPUT" --seconds 30
```

The host does not send serial bytes, reset, reflash, reconnect or retry. Optional
`--ready-file` marks a successful open; `--stop-file` lets the caller end capture.
All output/marker paths must be new. Opening is an operation requiring bench
ownership; do not start capture during somebody else's unmonitored run.

## Reuse from another project

Add Extender's maintained `scripts` directory to the consumer's Python import
path, using its existing checkout configuration. Then use:

```python
from passive_serial import open_passive_serial

with open_passive_serial(mainboard_port, baudrate=115200, timeout=0.2) as monitor:
    data = monitor.read(8192)
```

Use `read()` directly or retain the consumer's existing collection loop. The
helper returns an already open pyserial object; do not call `open()` again,
override DTR/RTS, or enable hardware flow control. The consumer owns output,
thread/stop lifecycle, error reporting and device identity. It must stop before
another tool flashes or takes the same port. Unsupported joined control updates
fail instead of silently falling back to the unsafe sequence. The advisory
exclusive lock complements, and does not replace, bench ownership.

## Observing Legacy CLI and application text

A mainboard serial capture does not automatically contain MOS CLI or application
`printf` output: those bytes normally go to the mainboard display. Stock VDP
supports a printer mirror to its USB debug serial, enabled by `VDU 2` and
disabled by `VDU 3`. Verify support in the exact installed VDP composition;
the retained F049 mainboard composition includes it. This requires no EMOS
observer, firmware replacement or display-route change.

1. The bench owner establishes an actual CLI, including acknowledged listener
   EXIT if the foreground SD listener was running, then opens the maintained
   passive reader described above.
2. At that CLI, the owner sends `VDU 2`, followed separately by a printable
   sentinel such as `VDU 65 13 10`. Observe its `A` and newline in the capture
   before relying on the channel for any separately authorized diagnostic.
3. The VDP mirrors future printable text and controls8–13. It does not dump
   bitmap/resource payloads or recover text printed before mirroring began.
   Pace any subsequent diagnostic by its actual output; do not send repeated
   Ready keys into an unknown foreground state.
4. After collection, at a verified CLI, the owner sends `VDU 3` to end the
   diagnostic mirror and closes the reader. Exclude the extra serial output
   from claims about uninstrumented performance or input latency.

P4's `/screen/text` endpoint and `scripts/screen_text.py` read the P4-rendered
screen; they do not observe Legacy mainboard video. Stock `VDU 23,0,&83,x;y;`
can recognize a currently drawn character through MOS, but it matches glyph
pixels against the selected font/colours rather than reading a durable text
transcript. Font changes, graphics or later output can prevent recovery.

## Why the old reader reset Agon

Linux's nonblocking tty open asserts both DTR/RTS together. Pyserial's ordinary
False/False setup next clears DTR, then RTS in separate requests. The intermediate
logical DTR=false/RTS=true means physical DTR high/RTS low, which pulls Olimex's
common RST/EN low. Both controls equal avoids either differential reset or boot
selection state. Clearing both in one CH341 operation removes that intermediate.
See [Linux tty handling](https://raw.githubusercontent.com/raspberrypi/linux/rpi-6.18.y/drivers/tty/tty_port.c),
[CH341 modem controls](https://raw.githubusercontent.com/raspberrypi/linux/rpi-6.18.y/drivers/usb/serial/ch341.c)
and [Espressif's reset-circuit explanation](https://docs.espressif.com/projects/esptool/en/latest/esp32/advanced-topics/boot-mode-selection.html).
This is an interaction between host software and a deliberate auto-programming
circuit, not evidence of a defective CH341 driver or Pingo2 keyboard command.

The schematic connects RST/EN to both the eZ80 and mainboard ESP32. USB monitor
opening must not be treated as harmless merely because no reset API was called.
Use the [reset protocol](bench-reset.md) for intentional resets. P4 ready=true
alone is not proof that mainboard keyboard commands execute: qualify recovery
with a harmless actual CLI/service exchange when authorized.

[BENCH-010 repair results](tasks/BENCH-010/SERIAL-REPAIR-R01.md) retain scope and
limits. The public source changes do not alter the selected immutable production
bundle, which still contains its recorded historical tool versions.
