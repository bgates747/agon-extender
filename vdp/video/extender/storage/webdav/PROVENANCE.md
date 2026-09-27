# Embedded WebDAV adapter provenance

Protocol idioms adapted from ErikMeinders/webdav, MIT, revision
`8ab2375018047b3c943a3195ffd7948a990b654a` (retained research snapshot).
[Source](https://github.com/ErikMeinders/webdav/tree/8ab2375018047b3c943a3195ffd7948a990b654a).
LICENSE is retained beside this adaptation.

`protocol.hpp` adapts percent encoding/decoding and single-range handling from
`src/esp_webdav_util.c` and `src/esp_webdav.c`. The XML response shape follows
`src/esp_webdav_propfind.c`. Paths use Agon limits instead of POSIX mount paths;
range numbers are checked in full with overflow rejection. No synthetic ETag,
mtime or nominal lock is emitted. HTTP storage work goes through Backend.

The Finder expected-length/dechunking approach in `src/esp_webdav_macos_put.c`
informs the separate bounded body reader. Its session recv override is NOT
installed: it would affect the video server and requires additional lifecycle
validation. Body framing must finish before remote activation, including the
terminal zero chunk. An ESP-IDF binding must deliver the raw encoded body to this
reader, or explicitly indicate a fully decoded/validated fixed-length body.

Protocol references: [RFC 4918](https://www.rfc-editor.org/rfc/rfc4918.html)
sections 9–10 (depth, destination, overwrite, property statuses), and
[RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html) sections 13–14 (conditions,
ranges). The adapter is a development subset, not a DAV class-compliance claim.
