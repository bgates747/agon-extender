# WebDAV usability control

Temporary host server: WsgiDAV 4.3.5 with Cheroot 11.1.2, installed into an
ignored isolated virtual environment. No firmware/server component from the
embedded candidate is used. No Agon or P4 operations occur.

`serve.py` requires an explicitly supplied root containing the synthetic-sandbox
marker. Bind defaults to loopback; LAN binding is an explicit preview choice.
The server uses anonymous access for disposable samples only, not a proposed
production access policy. Do not point it at real project or user directories.

Sample tree: 128 loose binary files, nested text file, empty directory and scratch.
Runtime endpoint, PID, generated files and logs live in ignored agent storage.
Keep user originals; the whole share is disposable. Stop the temporary server
and unmount its shares when review is finished, without touching other mounts.

## Review

Use the native file manager's network location for the trial's `dav://HOST:PORT/`.
Drag loose files and folders between the share and a chosen local directory.
Try creating a folder, renaming it and deleting only synthetic/sample content.
This is the interaction being evaluated, not representative Agon throughput.

## Retained result — 2026-09-27

| Check | Pop!_OS GVfs | Lenovo GVfs |
| --- | --- | --- |
| Mount and list | Pass | Pass |
| 129-file upload/download with SHA-256 comparison | Pass | Pass |
| Nested and empty folders | Pass | Pass |
| Rename, overwrite and recursive sandbox deletion | Pass | Pass |
| Native GUI usability acceptance | Pending | Pending |
| Embedded P4/EMOSlet integration | Not tested | Not tested |

Automated script exercised the GVfs FUSE mount with ordinary byte I/O; it did
not automate GUI drag/drop. Invoked both native file managers to open the share.
Mac Finder remains untested. Recorded script durations 1.58 s (local loopback)
and 13.18 s (remote LAN) are not comparable performance benchmarks and say nothing
about Agon SD throughput.

Initial Python shutil.copytree default copy2 attempted metadata preservation and
failed with EOPNOTSUPP. Repeated the test using explicit byte copies and directory
creation; all byte checks passed. Do not claim full POSIX metadata preservation.
GUI copy behavior under this constraint is part of the pending human review.

The initial Pop!_OS GUI launch lacked display environment and failed. Relaunched
using its existing desktop-session display variables. No desktop configuration
was changed. Lenovo's gio-open request returned successfully; human confirmation
of the visible window remains necessary.
