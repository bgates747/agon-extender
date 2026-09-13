# Agon Extender browser video demo — r01

Experimental source sample, 2026-09-13. Try the actual browser page, EVF1 parser
and WebGL2 presenter on your own computer without an Agon or P4. The animated
test pattern is generated locally by the production JavaScript.

## Try it

You need Python 3.10+ and a browser with WebGL2. From this extracted directory:

```sh
python3 -m venv .venv
.venv/bin/python -m http.server 8000 --bind 127.0.0.1 --directory vdp/video/extender/web
```

Open [the local demo](http://127.0.0.1:8000/?demo). You should see an animated
colour pattern, state `local RGB222 test pattern`, a `320×240 RGB222` surface
and increasing Presented count. Stop the server with Ctrl-C. The server serves
only the included browser-asset directory over loopback.

Use HTTP rather than opening `index.html` directly: browsers load its JavaScript
modules through the web server. The **Local test pattern** button restarts the
demo. **Connect** expects a real same-origin `/video` WebSocket service, which
Python's static server does not provide; reload `/?demo` to return to the demo.
If WebGL2 is disabled or unavailable, the page cannot present the pattern.

## Where to experiment

1. `vdp/video/extender/web/frame_protocol.js` validates EVF1 headers/bounds,
   tracks one-frame credit and constructs the synthetic pattern. The current
   parser accepts RGB888 and packed `00BBGGRR` RGB222 frames.
2. `webgl2_presenter.js` in that directory presents the decoded final pixels.
3. `app.js` wires the page to either the local pattern or the `/video` service.
   It sends the next `frame` credit after presentation of the preceding frame.
4. The [maintained protocol](https://github.com/bgates747/agon-extender/blob/main/docs/protocols/browser-video.md)
   describes the 32-byte header, sizes, pixel formats and pacing.

The browser is a pixel display, not a TRS-80 emulator, ANSI terminal or VDP
implementation. It does not capture keyboard input or produce audio. The local
pattern bypasses P4 rendering and the physical link; its FPS is not a hardware
performance measurement. A TRS-OS terminal/keyboard path needs separate work.

The unchanged production UI regression is included as an optional check on a
development host with Playwright and its Chromium runtime already available:

```sh
.venv/bin/python tests/browser_video_ui_test.py
```

That optional test is not required to view the demo. It starts a loopback server,
uses simulated sockets and writes a screenshot under `agents/`. No board is used.

## Provenance and license

Browser assets and the UI test are unmodified Agon Extender files. `manifest.json`
records source HEAD, original paths, SHA-256 and each file's relationship to
that HEAD. This is an experimental source snapshot, not a firmware release. See `LICENSE` and
`LICENSING.md` for the GPL-3.0-only project policy and preserved upstream notices.
