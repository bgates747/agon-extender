# P4-local SD file management

The development firmware provides a sessionless HTTP file manager for the P4's
own card, with a Python CLI and curl interface. Candidate **r57 passed bounded
hardware checks on the local DevKit**, but is not in selected production v0.1.0.
Obtain the current installed-build receipt and bench ownership before connecting;
the historical r57 result does not establish what firmware is running now. See the
[hardware results](tasks/PORT-007/HARDWARE-RESULTS.md) for scope. See [implementation contract and evidence](tasks/PORT-007/NETWORK-CONTRACT.md).

## Ownership and setup

P4 owns SDMMC/FatFS directly; Agon, EMOS, `sdserve` and the parallel pipe do not
participate. The storage HTTP task listens on port **8080**, separate from the
port-80 video/input server. This port is not FTP, SMB or WebDAV. The separate
[staged mainboard WebDAV candidate](mainboard-sd.md) uses port 8081 and the P4
card for private staging; its visible files belong to Agon SD. Shared storage
leases can make P4-local operations temporarily busy during staged jobs.

1. Obtain the P4 address from the operator. Set `P4_SD_URL` to
   `http://P4_HOST:8080`, substituting that address. This is a trusted-LAN service
   without authentication or TLS. The write-intent header is not authentication.
2. Insert the card before boot. The first request attempts mount once; failure
   never formats the card. Correct the problem and reboot to retry. Power down
   before removing the card; hotplug is not supported.
3. A 32 GiB capacity label does not establish the card's partition/filesystem.
   Formatting is never performed by this API. `/status` reports mount status,
   raw card capacity, filesystem size and free bytes (null if unavailable).
4. The server serializes its own requests. No other P4 consumer may write this
   filesystem or use mounted writable disk images concurrently. Future MAME/EMOS
   integration must coordinate ownership explicitly. Read-only guest images are
   not automatically safe either: HTTP may replace/delete their backing files.
   No image-lease API is implemented; detached service tests keep guests disabled.

## Python CLI

Use Python 3.9 or newer (standard library only), using this checkout's virtual
environment on Linux. There are no session state files. Successful commands print JSON; transport, HTTP and client errors exit nonzero.
`status` can exit zero with `mounted: false`: scripts must inspect that field
before treating storage as ready. `--timeout SECONDS` defaults to 120; long searches
or recursive operations may need a larger timeout.

```sh
python3 scripts/p4sd.py --url "$P4_SD_URL" status
python3 scripts/p4sd.py --url "$P4_SD_URL" list / --recursive
python3 scripts/p4sd.py --url "$P4_SD_URL" stat /games/demo.bin
python3 scripts/p4sd.py --url "$P4_SD_URL" mkdir /games/new/assets --parents
python3 scripts/p4sd.py --url "$P4_SD_URL" put local.bin /games/demo.bin
python3 scripts/p4sd.py --url "$P4_SD_URL" put local.bin /games/demo.bin --replace
python3 scripts/p4sd.py --url "$P4_SD_URL" get /games/demo.bin downloaded.bin
python3 scripts/p4sd.py --url "$P4_SD_URL" put ./assets /games/new/assets --recursive
python3 scripts/p4sd.py --url "$P4_SD_URL" get /games/new ./backup --recursive
python3 scripts/p4sd.py --url "$P4_SD_URL" copy /games/new /games/saved --recursive
python3 scripts/p4sd.py --url "$P4_SD_URL" move /games/saved /games/renamed
python3 scripts/p4sd.py --url "$P4_SD_URL" search / --name '*.txt' --contains 'hello'
python3 scripts/p4sd.py --url "$P4_SD_URL" delete /games/renamed --recursive
```

The destination is always the **exact destination path**, not an implicit
"copy into this directory" convention. The Python CLI always searches recursively; HTTP callers can request
`recursive=0`. Recursive host uploads/downloads merge
directory structure; files conflict unless `--replace` is supplied. Directory
copies performed on P4 create a new tree and do not merge existing trees.
Moves/renames require an absent destination. `copy --replace` replaces a file,
not a directory. No symlinks are supported. Downloads stage in the destination's
host directory before installing the completed file; existing files are kept
unless replacement was requested.

## HTTP / curl

All paths are absolute and relative to the card root. `path` selects the source
or entry, `to` selects the destination. Boolean options are `0` or `1`. All
mutations require `X-Extender-Storage: 1` and reject browser `Origin` headers.
Options go in the URL query, not a JSON body.

| Method / endpoint | Parameters | Behavior |
|---|---|---|
| GET `/status` | none | Mount/error, capacity and free space; inspect `mounted` even on HTTP 200 |
| GET `/stat` | `path` | Path/name, directory flag, byte size, modification timestamp |
| GET `/list` | `path`, `recursive=1` optional | JSON array of entries; recursive paths identify each entry |
| GET `/search` | `path`, `name`, `contains`, `recursive=0` optional | Recursive by default; case-insensitive basename `*`/`?` glob and optional case-sensitive literal ASCII content; both filters must match |
| GET `/file` | `path` | Stream file bytes |
| PUT `/file` | `path`, `replace=1` optional | Stream a new or replacement file; default rejects existing file |
| POST `/directory` | `path`, `parents=1` optional | Create directory; parents mode also succeeds if already a directory |
| POST `/copy` | `path`, `to`, `recursive=1`, `replace=1` optional | File copy or new directory tree; recursive required for directories |
| POST `/move` | `path`, `to` | Move/rename file or directory, no overwrite |
| DELETE `/entry` | `path`, `recursive=1` optional | Delete file/empty directory; recursive removes a tree |

```sh
curl --fail-with-body "$P4_SD_URL/status"
curl --fail-with-body -G --data-urlencode 'path=/' --data 'recursive=1' "$P4_SD_URL/list"
curl --fail-with-body -G --data-urlencode 'path=/' --data-urlencode 'name=*.txt' \
  --data-urlencode 'contains=hello world' "$P4_SD_URL/search"
curl --fail-with-body -G --data-urlencode 'path=/games/demo.bin' \
  "$P4_SD_URL/file" --output downloaded.bin
curl --fail-with-body -H 'X-Extender-Storage: 1' -H 'Expect:' \
  --upload-file local.bin "$P4_SD_URL/file?path=/games/demo.bin&replace=1"
curl --fail-with-body -X POST -H 'X-Extender-Storage: 1' \
  "$P4_SD_URL/directory?path=/games/new/assets&parents=1"
curl --fail-with-body -X POST -H 'X-Extender-Storage: 1' \
  "$P4_SD_URL/copy?path=/games/new&to=/games/saved&recursive=1"
curl --fail-with-body -X POST -H 'X-Extender-Storage: 1' \
  "$P4_SD_URL/move?path=/games/saved&to=/games/renamed"
curl --fail-with-body -X DELETE -H 'X-Extender-Storage: 1' \
  "$P4_SD_URL/entry?path=/games/renamed&recursive=1"
```

Percent-encode special characters/spaces in manually constructed URLs. The Python
client handles that automatically. curl download writes directly to its output;
use the Python client if preserving an existing host file until success matters.

## Limits, errors and recovery

1. File paths accept printable ASCII, up to 240 decoded bytes; no traversal,
   empty components, trailing slash (except `/`), trailing dot/space or FAT-invalid
   punctuation. FatFS uses heap-backed long filenames. Recursive traversal is
   limited to 16 levels below the requested directory; it is not an index.
   Searches inspect file bytes directly, including binary files. Patterns/content
   are limited to 128 printable ASCII bytes; content search returns matching
   file metadata, not matching lines. Empty `contains` disables that filter.
2. PUT requires fixed Content-Length, supplied by curl for a regular local file.
   Chunked PUT is unsupported; the upload limit is 512 MiB. Existing parent
   directories are required. File download/copy streams fixed-size chunks.
   Modification timestamps reflect the P4 clock/FAT conversion and are not a
   guaranteed wall-clock authority or preserved upload timestamp.
3. Root delete/move/copy-source operations are rejected, as are moves/copies
   into themselves, descendants or ancestors (case-insensitive FAT comparison).
   A directory can be copied only to a new name. Recursive operations are **not
   transactions**: errors or interruption may leave copied entries or already
   deleted entries. A timed-out client must inspect state before retrying; the
   server may still finish an operation after the client disconnects.
4. Upload writes `name.ext-upload`, flushes, syncs and closes it, then installs
   it. Replacement first moves the old file to `name.ext-backup`; a failed
   installation attempts restoration. The backup is deleted only after the new
   file is installed. FAT cannot make this sequence power-loss atomic. A failure
   cleaning up a backup can report failure even though the new file is present.
5. Stale staging/backup names block another upload rather than being erased.
   They are visible to listing/stat/download/delete so the operator can recover
   their contents and deliberately clean them up. Creating/copying/moving names
   containing these reserved suffixes is forbidden. Recursive deletion explicitly
   removes everything inside its target, including staging/backup files.
6. Typical errors: 400 invalid path/options/type/depth, 403 root mutation, missing write intent, or FatFS refusal to remove a
   nonempty directory; 404 missing entry; 409 existing destination/stale staging; 411 missing upload length, 413 oversized upload,
   503 mount unavailable, 507 no space, 500 filesystem failure. Error responses
   close the HTTP session. Streaming list/search failures terminate the response
   before valid JSON completion; callers must reject truncated results.
7. Verify valuable transfers by downloading and comparing bytes/hashes.
   Checked flush/close is not a claim of immunity to power loss. No physical
   throughput or coexistence qualification is claimed by host tests.
