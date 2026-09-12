#!/usr/bin/env python3
"""Download every document off a reMarkable, mirroring its folder tree.

Plans by default and downloads only with --run, so a first invocation always
just reports. Re-running resumes: a file already on disk with a matching size
is left alone unless --force is given.

What this produces is the device's own export of each document, which is what
the USB web interface serves. Notebooks come back as PDFs of their pages and
annotated PDFs come back with the annotations burned in. The underlying .rm
stroke data is never served over this interface, so the result is a complete
readable archive but not something a device can be restored from.

    python3 rm_backup.py                        # plan only
    python3 rm_backup.py --run                  # download
    python3 rm_backup.py --run --out ~/rm-2026  # somewhere specific
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import date
from pathlib import Path

from rm_api import SUPPORTED_SUFFIXES, Remarkable, RemarkableError

DEFAULT_ROOT = Path.home() / "Documents" / "remarkable-backup"

# Characters a filename cannot carry, plus the ones that make shell work
# unpleasant later. VisibleName on the device has no such restrictions.
UNSAFE = set('/\\:*?"<>|\0')


def safe_name(name: str) -> str:
    """Turn a device VisibleName into a filename that survives a filesystem."""
    cleaned = "".join("_" if c in UNSAFE or ord(c) < 32 else c for c in name)
    cleaned = cleaned.strip().strip(".")
    return cleaned or "untitled"


def plan(device: Remarkable, out: Path) -> list[dict]:
    """Build the download list: one entry per document on the device."""
    entries = []
    seen: set[Path] = set()

    for folder, item in device.walk():
        directory = out.joinpath(*[safe_name(p) for p in folder.split("/") if p])
        stem = safe_name(item.name)

        # VisibleName carries the extension for some formats and omits it for
        # others, so strip a known one rather than saving "book.pdf.pdf".
        if Path(stem).suffix.lower() in SUPPORTED_SUFFIXES:
            stem = str(Path(stem).with_suffix(""))

        # Two documents in one folder can share a VisibleName. Disambiguate
        # with the device ID rather than letting the second overwrite the first.
        target = directory / f"{stem}.pdf"
        if target in seen:
            target = directory / f"{stem} [{item.id[:8]}].pdf"
        seen.add(target)

        entries.append(
            {
                "id": item.id,
                "name": item.name,
                "folder": folder,
                "file": str(target),
            }
        )
    return entries


# The device renders exports on demand and is easily overwhelmed. Its own
# renderer gives up around 15s and returns 408; hammering it past that point
# makes it answer 400 to everything and eventually kills the web server
# outright, which then needs restarting from the tablet's settings. So: pause
# between documents, back off hard between retries, and stop entirely rather
# than keep pushing a device that has started refusing.
ATTEMPT_TIMEOUTS = (120, 300)
RETRY_PAUSE = (30, 90)
BETWEEN_DOCUMENTS = 2
CONSECUTIVE_FAILURE_LIMIT = 3


def fetch(device: Remarkable, entry: dict, force: bool) -> str:
    """Download one entry. Returns "saved", "skipped", or raises."""
    target = Path(entry["file"])
    if target.exists() and target.stat().st_size > 0 and not force:
        entry["bytes"] = target.stat().st_size
        entry["sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
        return "skipped"

    for attempt, timeout in enumerate(ATTEMPT_TIMEOUTS, 1):
        try:
            served, data = device.download(entry["id"], timeout=timeout)
            break
        except RemarkableError:
            if attempt == len(ATTEMPT_TIMEOUTS):
                raise
            pause = RETRY_PAUSE[attempt - 1]
            print(
                f"    failed, resting {pause}s before retrying {entry['name']}",
                file=sys.stderr,
                flush=True,
            )
            time.sleep(pause)
    if not data:
        raise RemarkableError(f"{entry['name']}: device returned an empty file")

    # Honour the extension the device chose; it sends .epub back for some
    # uploads rather than rendering them to PDF.
    suffix = Path(served).suffix.lower() if served else ""
    if suffix and suffix != target.suffix.lower():
        target = target.with_suffix(suffix)
        entry["file"] = str(target)

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    entry["bytes"] = len(data)
    entry["sha256"] = hashlib.sha256(data).hexdigest()
    return "saved"


def write_manifest(out: Path, host: str, entries: list[dict]) -> Path:
    """Write the manifest. Called after every document, not just at the end."""
    manifest = out / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "taken": date.today().isoformat(),
                "source": host,
                "note": (
                    "Device-rendered exports from the USB web interface. "
                    "Annotations are burned in; raw .rm stroke data is not "
                    "included and this cannot restore a device."
                ),
                "documents": entries,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help=f"backup directory (default {DEFAULT_ROOT}/<today>)",
    )
    parser.add_argument(
        "--run", action="store_true", help="actually download; otherwise plan only"
    )
    parser.add_argument(
        "--force", action="store_true", help="re-download files already on disk"
    )
    parser.add_argument(
        "--skip",
        action="append",
        default=[],
        metavar="ID_OR_NAME",
        help="exclude a document by id or name substring; repeatable. Use for "
        "a document that reliably crashes the device's web server.",
    )
    args = parser.parse_args()

    out = args.out or DEFAULT_ROOT / date.today().isoformat()
    out = out.expanduser()

    device = Remarkable()
    if not device.reachable():
        print(
            "No device on 10.11.99.1.\n"
            "Connect it over USB and turn on Settings > Storage > USB web "
            "interface. Wi-Fi does not serve this API.",
            file=sys.stderr,
        )
        return 1

    entries = plan(device, out)
    if not entries:
        print("Device holds no documents.")
        return 0

    if args.skip:
        keep, dropped = [], []
        for entry in entries:
            if any(s == entry["id"] or s.lower() in entry["name"].lower()
                   for s in args.skip):
                dropped.append(entry)
            else:
                keep.append(entry)
        entries = keep
        for entry in dropped:
            print(f"skipping {entry['folder']}/{entry['name']}")
        if not dropped:
            print("warning: --skip matched nothing", file=sys.stderr)

    folders = sorted({e["folder"] or "(root)" for e in entries})
    print(f"{len(entries)} documents across {len(folders)} folders -> {out}")
    for folder in folders:
        count = sum(1 for e in entries if (e["folder"] or "(root)") == folder)
        print(f"  {folder}: {count}")

    if not args.run:
        print("\nPlan only. Re-run with --run to download.")
        return 0

    out.mkdir(parents=True, exist_ok=True)
    saved = skipped = 0
    failures: list[tuple[str, str]] = []

    consecutive = 0
    for index, entry in enumerate(entries, 1):
        label = f"{entry['folder']}/{entry['name']}" if entry["folder"] else entry["name"]
        try:
            result = fetch(device, entry, args.force)
        except RemarkableError as exc:
            failures.append((label, str(exc)))
            entry["error"] = str(exc)
            write_manifest(out, device.host, entries)
            consecutive += 1
            # Connection refused means the device's web server is gone, not
            # that this document is bad. Nothing more will work until someone
            # restarts it on the tablet.
            if "refused" in str(exc).lower():
                print(
                    f"[{index}/{len(entries)}] FAILED {label}: {exc}\n\n"
                    f"The device's web server is down. Restart it on the tablet "
                    f"(Settings > Storage > USB web interface, off then on, or "
                    f"reboot), then re-run to resume.",
                    file=sys.stderr,
                    flush=True,
                )
                break
            print(f"[{index}/{len(entries)}] FAILED {label}: {exc}", file=sys.stderr, flush=True)
            if consecutive >= CONSECUTIVE_FAILURE_LIMIT:
                print(
                    f"\nStopping: {consecutive} documents failed in a row, which "
                    f"means the device's web server has stopped answering rather "
                    f"than these documents being individually bad.\n"
                    f"Restart it on the tablet (Settings > Storage > USB web "
                    f"interface, off then on, or reboot), then re-run to resume.",
                    file=sys.stderr,
                )
                break
            continue
        consecutive = 0
        if result == "saved":
            saved += 1
        else:
            skipped += 1
        print(f"[{index}/{len(entries)}] {result} {label}", flush=True)
        write_manifest(out, device.host, entries)
        if result == "saved":
            time.sleep(BETWEEN_DOCUMENTS)

    manifest = write_manifest(out, device.host, entries)

    print(f"\n{saved} saved, {skipped} already present, {len(failures)} failed")
    print(f"Manifest: {manifest}")
    if failures:
        print("\nRe-run to retry the failures; downloads resume.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
