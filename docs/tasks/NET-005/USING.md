# Manual Console8 Wi-Fi BBS test

Run Radiotux's unchanged terminal on Console8 and talk to the Pi over the already
wired ESP8266. The Pi understands `help`, `time`, `uptime`, `note TEXT`, `notes`
and `quit`. Host checks do not qualify your module or Console8. No firmware,
startup or wiring change is part of this fixture.

## Copy and launch manually

1. Obtain the generated package and its adjacent SHA256 file from Extender.
   Its manifest identifies the build and every payload. Copy the package's
   `sd/extender/network/net005/` folder to `/extender/network/net005/` on the
   Console8 card. Keep existing files, including `/bin/minicom.bin`, unchanged.
   Extender does not access Console8 remotely. Synchronize writes and leave a
   host-mounted card mounted; Smith controls moving it to Console8.
2. Stop Jukebox yourself and return to MOS. Note your current video mode.
   This terminal needs at least 80 columns and 30 rows. If the current mode
   lacks that space, select an appropriate mode, such as the ordinary mode0:

   ```text
   VDU 22 0
   ```

   Wait at least one second after a mode change. Skip the switch if unnecessary.
   The unchanged terminal clears its workspace but does not select a new mode.
3. Load the fresh, separate file, then run it:

   ```text
   LOAD /extender/network/net005/minicom.bin
   RUN &040000
   ```

   Expect the Agon Terminal screen with `115200 8N1`. Leave capture OFF; Ctrl+F
   would create its upstream `capture.txt` in the current directory and is not
   part of this test. Keep local echo ON initially. Ctrl+Q exits the terminal.

## Identify and connect the modem

Type each command and press Enter, waiting for its reply before continuing.
Start with:

```text
AT
AT+GMR
```

Record the actual firmware/version reply. The historical module version in old
notes is not a current read. If `AT` has no response, stop and report that fact;
do not flash the module or alter its UART settings as a guessed correction.

The following commands use volatile Wi-Fi settings documented by Espressif.
If the module already has an IP on your Wi-Fi, skip station configuration and
association. Keep SSID/password out of captured logs and project documents.
Replace the placeholders locally, including any required AT quote escaping:

```text
AT+CWMODE_CUR=1
AT+CWJAP_CUR="YOUR_SSID","YOUR_PASSWORD"
AT+CIFSR
```

An unsupported `_CUR` command is a compatibility result to report. Do not
silently substitute a flash-persisting `_DEF`, saved auto-connect or firmware
upgrade. Only a successful association/IP permits the next step.

Use the numeric Pi IPv4 address and port from Extender's current private run
record. The supplied template uses port2323; substitute the actual port if the
operator deliberately selected another one. Expect `OK` for configuration,
`CONNECT`/`OK` for opening TCP, then `>` for entering data mode:

```text
AT+CIPMUX=0
AT+CIPMODE=1
AT+CIPSTART="TCP","PI_IPV4",2323
AT+CIPSEND
```

The Pi banner may have arrived during connection setup. Once `AT+CIPSEND` gives
`>`, type `help` and press Enter. This should return readable BBS text and
`bbs>`. It is raw TCP, not a Telnet negotiation or an operating-system shell.
Modem AT commands must not be typed as BBS commands after entering data mode.

## Try something useful

```text
help
time
uptime
note Hello from Console8
notes
```

Expect Pi time in the configured timezone, host/service uptime, and a saved note
number followed by the note in `notes`. Notes support 1–60 printable ASCII
characters; `notes` displays the last three. There is no network echo because the
terminal already echoes your typing. If characters appear twice, use Ctrl+E to
adjust local echo, then record the observed setting. The original terminal has
limited scrolling: Ctrl+L clears its workspace; type `help` again afterward.

The Pi saves notes locally. Leaving a note does not wake or send a message to a
Codex agent. Smith can ask Extender in chat to read or answer the board later.

## Disconnect and restore the CLI

1. Type `quit` and Enter. The Pi says goodbye and closes this TCP session.
   ESP-AT passthrough may reconnect automatically; another banner does not mean
   that the Pi ignored `quit`.
2. Stop typing for at least one second. Send exactly `+++`, **without Enter**,
   then wait at least one second before sending another AT command. Confirm
   command mode with `AT`, then close TCP and disable passthrough:

   ```text
   AT
   AT+CIPCLOSE
   AT+CIPMODE=0
   ```

   Wait for each response. The unchanged terminal sends keystrokes individually;
   recognition of the three-plus escape on this module is a manual compatibility
   check, not an assured feature. If it is not recognized, stop and report that
   result. Smith can restart the separate module manually to clear volatile
   passthrough; this guide does not authorize an agent hardware action or a
   persistent setting change. Ctrl+Q alone does not leave modem data mode.
3. Use Ctrl+Q to return to MOS. If you changed the entry video mode, restore that
   recorded mode and allow at least one second for settling. Restore normal
   text output and a visible flashing cursor:

   ```text
   VDU 4 23 1 1 23 1 3
   ```

4. Confirm visible CLI and normal typing. Reconnect deliberately with the same
   TCP setup and use `notes` to verify persistence, then repeat cleanup. Report
   AT firmware, the first failed command if any, BBS interaction, note persistence
   and actual CLI/modem cleanup. No performance or physical pass is inferred
   from the host tests alone.

## Pi operator commands

Run the packaged `host/wifi_bbs.py` explicitly, using a local data directory and
an available LAN endpoint. The default bind is loopback; it is not reachable from
the ESP8266 until the operator explicitly selects the Pi's LAN address:

```sh
python3 host/wifi_bbs.py --bind "$PI_IPV4" --port 2323 \
  --data-dir "$BBS_DATA" --timezone America/New_York \
  --build-id "$BBS_BUILD"
```

A foreground Ctrl+C or SIGTERM stops the listener and its client and records
actual service/session durations in `events.jsonl`. Notes remain in
`notes.sqlite3`. Extender's private run record gives the actual live service,
ready receipt and stop command when it starts a transient service. No boot
service is installed or enabled. The fixture is a plaintext trusted-LAN board.

## Source and limitations

1. Radiotux [terminal source at the selected commit](https://github.com/Radiotux/Agon-Software/tree/e265db1de57c49142420324945c666049dc1ec53/minicom)
   and the packaged original `Agon-Terminal.man` define the unchanged client.
   The package records exact binary and source identities; it does not claim
   we rebuilt or physically qualified the upstream executable.
2. Espressif [ESP8266 AT instruction set v1.5.4](https://www.espressif.com/sites/default/files/4a-esp8266_at_instruction_set_en_v1.5.4_0.pdf)
   documents volatile Wi-Fi configuration, single-connection passthrough and
   escape/reconnect behavior. Actual command support is a manual gate here.
3. The Wi-Fi module's four-wire UART1 connection has no RTS/CTS. The host sends
   short command responses and no unsolicited stream; this is not a bulk-transfer
   or flow-control qualification. Async/OTIRX remains deferred under NET-002.
