# Browser-video protocol authority

The maintained wire, codec, credit and viewer-ownership contract is
[docs/protocols/browser-video.md](../../../../docs/protocols/browser-video.md).
Do not maintain a second RGB888-only specification here. The browser presents
P4-composed pixels; it does not interpret VDU commands or implement VDP semantics.

The [source README](README.md) distinguishes this base checkout from deployed
codec/browser overlays. Select the exact candidate before assuming a negotiated
format is implemented. Historical EVF1-only instructions remain in Git; they are
not the current protocol or a deployment recipe.
