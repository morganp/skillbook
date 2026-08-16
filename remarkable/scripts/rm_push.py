#!/usr/bin/env python3
"""Push books onto a reMarkable over the USB web interface.

Plans first, uploads only when told to. The device offers no delete, so the
default is a dry run and --push is required to write anything.

    rm_push.py --list                          show device folders
    rm_push.py --from ~/Downloads --to Books   plan, change nothing
    rm_push.py --from ~/Downloads --to Books --push
    rm_push.py --from "/path/600-Technology" --to Books --match woodwork

Duplicates already on the device are skipped by default; --force overrides.
"""

from __future__ import annotations

import argparse
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from rm_api import SUPPORTED_SUFFIXES, Remarkable, RemarkableError, normalise


def evicted_name(placeholder: Path) -> str:
    """Real filename behind an iCloud placeholder.

    iCloud replaces an evicted file with a plist named ".<original>.icloud",
    so "Book.pdf" becomes ".Book.pdf.icloud".
    """
    return placeholder.name[1:-len(".icloud")]


def collect(
    source: Path, match: str | None, recursive: bool
) -> tuple[list[Path], list[str]]:
    """Find candidate books under source.

    Returns (books, evicted) where evicted names files that iCloud has removed
    from local storage. Those cannot be uploaded until macOS downloads them
    again, and they would otherwise vanish from the plan without explanation,
    because placeholders are hidden dotfiles.
    """
    if source.is_file():
        return [source], []

    walker = list(source.rglob("*") if recursive else source.glob("*"))
    found = [
        p
        for p in walker
        if p.is_file()
        and p.suffix.lower() in SUPPORTED_SUFFIXES
        and not p.name.startswith(".")
    ]
    evicted = [
        evicted_name(p)
        for p in walker
        if p.name.startswith(".")
        and p.name.endswith(".icloud")
        and Path(evicted_name(p)).suffix.lower() in SUPPORTED_SUFFIXES
    ]

    if match:
        needle = match.lower()
        found = [p for p in found if needle in p.name.lower()]
        evicted = [n for n in evicted if needle in n.lower()]

    return sorted(found, key=lambda p: p.name.lower()), sorted(evicted, key=str.lower)


def resolve_folder(device: Remarkable, name: str | None) -> tuple[str, str]:
    """Map a folder name to its device ID. Returns (id, label)."""
    if not name or name.lower() == "root":
        return "", "root"
    folder = device.find_folder(name)
    if folder is None:
        available = ", ".join(f.name for f in device.folders()) or "none"
        raise SystemExit(
            f"No folder named {name!r} on the device.\n"
            f"Available top-level folders: {available}\n"
            f"The USB web interface cannot create folders. Make it on the device first."
        )
    return folder.id, folder.name


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="http://10.11.99.1")
    parser.add_argument("--list", action="store_true", help="show device folders and exit")
    parser.add_argument("--from", dest="source", type=Path, help="file or directory of books")
    parser.add_argument("--to", help="destination folder name on the device (default root)")
    parser.add_argument("--match", help="only files whose name contains this text")
    parser.add_argument("--recursive", action="store_true", help="descend into subdirectories")
    parser.add_argument("--force", action="store_true", help="upload even if already present")
    parser.add_argument("--push", action="store_true", help="actually upload (default is a dry run)")
    args = parser.parse_args()

    device = Remarkable(args.host)
    if not device.reachable():
        print(
            f"No device at {args.host}.\n"
            "Connect it over USB and enable Settings > Storage > USB web interface.",
            file=sys.stderr,
        )
        return 1

    if args.list:
        print("Device folders:")
        for folder in device.folders():
            count = len(device.documents(folder.id))
            print(f"  {folder.name}  ({count} documents)")
        return 0

    if not args.source:
        parser.error("--from is required unless --list is given")
    if not args.source.exists():
        print(f"Source not found: {args.source}", file=sys.stderr)
        return 1

    folder_id, folder_label = resolve_folder(device, args.to)
    books, evicted = collect(args.source, args.match, args.recursive)

    if evicted:
        print(f"{len(evicted)} file(s) are in iCloud but not downloaded locally:")
        for name in evicted:
            print(f"  ! {name}")
        print(f"  Download them first:  brctl download {shlex.quote(str(args.source))}\n")

    if not books:
        print(f"No PDF or EPUB files found under {args.source}")
        return 0

    # Compare against the whole device, not just the target folder, so a book
    # filed elsewhere is not uploaded twice.
    on_device = {normalise(item.name) for _, item in device.walk()}

    queued = [b for b in books if args.force or normalise(b.name) not in on_device]
    skipped = [b for b in books if b not in queued]

    print(f"Source:      {args.source}")
    print(f"Destination: {folder_label}")
    print(f"Found {len(books)} book(s): {len(queued)} to upload, {len(skipped)} already present\n")

    for book in queued:
        size = book.stat().st_size / 1_048_576
        print(f"  + {book.name}  ({size:.1f} MB)")
    for book in skipped:
        print(f"  = {book.name}  (already on device)")

    if not args.push:
        print("\nDry run. Nothing uploaded. Add --push to upload.")
        return 0
    if not queued:
        print("\nNothing to upload.")
        return 0

    print(f"\nUploading {len(queued)} book(s) to {folder_label}. This cannot be undone here.")
    failures = 0
    for index, book in enumerate(queued, 1):
        print(f"  [{index}/{len(queued)}] {book.name} ... ", end="", flush=True)
        try:
            device.upload_to(book, folder_id)
            print("ok")
        except RemarkableError as exc:
            print("FAILED")
            print(f"      {exc}", file=sys.stderr)
            failures += 1

    print(f"\nDone. {len(queued) - failures} uploaded, {failures} failed.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
