# P4-local SD card over HTTP

## Status and purpose

Development implementation; compile/host validation is recorded in
[PORT-007](tasks/PORT-007/NETWORK-CONTRACT.md). It is not yet part of the
accepted production v0.1.0 bundle. Do not assume the installed board exposes
these endpoints until the identified candidate is deployed and verified.

This accesses the card in the **Olimex P4 DevKit**, not Agon's card. P4 owns
SDMMC and FatFS; no EMOS, `sdserve`, Agon reset or parallel pipe is involved.
A separate HTTP task listens on port8080, independent of port80 video/input.
There is no browser file manager, FTP, WebDAV or SMB server in this slice.

## Before use

1. Obtain the P4 address and bench/service ownership from the operator. The
   service has no authentication/TLS: use only the trusted bench LAN.
2. Insert the card before P4 startup. The first storage request attempts mount
   once; failure never formats the card. Correct the card/format with the
   operator, then reboot P4 deliberately to retry. Hotplug is not supported.
3. Filesystem support follows the compiled FatFS configuration; a reported
   32 GiB card is not evidence of its partition/format. Preserve existing data;
   no formatting endpoint exists.
4. This service is currently the only P4-local writer. Do not add MAME writable
   images or another filesystem consumer without shared ownership/locking.
   In particular, never upload over an image mounted by an emulator.

## curl use

Set a local URL, for example `P4_SD_URL="http://$P4_HOST:8080"`, where P4_HOST
is the operator-provided host. Quoted query paths are URL encoded by curl.

```sh
curl --fail-with-body "$P4_SD_URL/status"
curl --fail-with-body --get --data-urlencode 'path=/' "$P4_SD_URL/list"
curl --fail-with-body --get --data-urlencode 'path=/example.bin' \
  "$P4_SD_URL/file" --output downloaded.bin
curl --fail-with-body -H 'X-Extender-Storage: 1' -H 'Expect:' \
  --upload-file local.bin "$P4_SD_URL/file?path=/new-file.bin"
```

For upload filenames containing spaces, encode them (`%20`); only absolute ASCII
paths are supported. Parent directories must already exist. Upload uses fixed
Content-Length (curl supplies it for a regular local file); chunked uploads and
files larger than512 MiB are rejected. Uploads are **create-only**: an existing
file or directory returns409, never an overwrite. Choose a new filename.
No mkdir, rename, deletion, overwrite or resume endpoint is provided yet.

Successful upload returns201 only after checked flush/sync/close and rename.
Download the file and compare a SHA-256 hash with the source for end-to-end
verification (`sha256sum` on Linux, `shasum -a 256` on macOS). An uncertain
network response is not proof of failed commit: inspect/download the destination
before retrying. Do not blindly remove a file to retry an upload.

## Responses, failures and final state

| Request | Result |
|---|---|
| GET /status | JSON mounted, mount_error, capacity_bytes and format_enabled:false;200 even when mount failed, inspect mounted |
| GET /list?path=… | JSON array of name, directory and size; root is `/` |
| GET /file?path=… | Binary streamed download |
| PUT /file?path=… |201 newly committed file;409 existing target/scratch;403 missing intent/browser Origin;411 missing fixed length;413 upload too large |
| Invalid path |400; traversal, control characters, backslashes and reserved scratch names rejected |
| Card unavailable |503 for file/list operations; status records mount error |
| Missing file/directory |404; upload parent/open/write/commit failure reports500 |

The single storage-server task serializes requests; a slow transfer delays other
storage requests, not the HTTP video task. Socket receive/send waits are bounded
at five seconds. There is no measured throughput or total-transfer-time promise.
A disconnected incomplete upload removes only its own temporary file. A power
loss may leave `<destination>.ext-upload`; an existing scratch file blocks reuse
and is never blindly deleted. Inspect it offline after stopping/powering down
P4. Card power-loss guarantees and read/write errors require physical testing.

After a successful request the card remains mounted and the server stays
available. Close host requests and power down before removing the card. Stopping
Agon's foreground SD listener has no effect on this separate service.
