"""Explicitly select a built demo in this profile's CRLF autoexec."""

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("app", choices=("hello", "shapes", "bitmaps"))
    parser.add_argument("--page", type=int)
    args = parser.parse_args()
    if args.page is not None:
        limit = {"shapes":24,"bitmaps":32}.get(args.app,0)
        if not 1 <= args.page <= limit:
            parser.error(f"--page for {args.app} must be in 1..{limit}")
    sd = ROOT / ".emulator/sdcard"
    binary = sd / "extender" / f"{args.app}.bin"
    if not binary.is_file() or binary.is_symlink():
        parser.error(f"Deploy the selected binary first: {binary}")
    startup = sd / "autoexec.txt"
    if startup.is_symlink() or (startup.exists() and not startup.is_file()):
        parser.error(f"Unexpected autoexec path: {startup}")
    mode = 3 if args.app == "hello" else 20
    run = f"run . {args.page}" if args.page else "run"
    data = f"SET KEYBOARD 1\r\nVDU 22 {mode}\r\ncd /extender\r\nload {args.app}.bin\r\n{run}\r\n".encode("ascii")
    if startup.exists() and startup.read_bytes() != data:
        (ROOT / ".emulator/autoexec.previous.txt").write_bytes(startup.read_bytes())
    startup.write_bytes(data)
    print(f"Startup: {args.app}, mode {mode}, page {args.page or 'all'}")


if __name__ == "__main__":
    main()
