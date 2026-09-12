#!/usr/bin/env python3
"""Client for the reMarkable USB web interface.

The device serves a small HTTP API on 10.11.99.1 while connected over USB with
"USB web interface" enabled in Settings. This module wraps the parts of that API
that are useful for pushing books onto the device.

Capabilities and hard limits, established by reading the device's own JavaScript
and by testing against a device:

    list      GET  /documents/          root listing (JSON array)
    list      GET  /documents/<id>      folder listing
    upload    POST /upload              multipart, field name "file"
    download  GET  /download/<id>/placeholder

Folder targeting is stateful and undocumented. The upload request carries no
parent field. Instead the server remembers the last folder listed on the
connection, so a GET of the target folder immediately before the POST places the
file in that folder. upload_to() implements that sequence.

There is no delete endpoint and no folder-creation endpoint. Uploads cannot be
undone through this interface; removing a document needs the device UI. Folders
must already exist on the device. Treat every upload as permanent.
"""

from __future__ import annotations

import json
import mimetypes
import urllib.error
import urllib.parse
import urllib.request
import uuid
from dataclasses import dataclass
from pathlib import Path

DEFAULT_HOST = "http://10.11.99.1"
TIMEOUT = 60

# Formats the device accepts. Anything else must be converted first.
SUPPORTED_SUFFIXES = {".pdf", ".epub"}


class RemarkableError(RuntimeError):
    """Any failure talking to the device."""


@dataclass(frozen=True)
class Item:
    """One document or folder on the device."""

    id: str
    name: str
    is_folder: bool
    parent: str

    @classmethod
    def from_json(cls, raw: dict) -> "Item":
        return cls(
            id=raw.get("ID", ""),
            name=raw.get("VisibleName", ""),
            is_folder=raw.get("Type") == "CollectionType",
            parent=raw.get("Parent", ""),
        )


class Remarkable:
    """Talks to one device.

    The connection is deliberately kept on a single opener so the server's
    notion of the current folder survives between the list and upload calls.
    """

    def __init__(self, host: str = DEFAULT_HOST, timeout: int = TIMEOUT):
        self.host = host.rstrip("/")
        self.timeout = timeout
        self._opener = urllib.request.build_opener()

    # -- reading -----------------------------------------------------------

    def reachable(self) -> bool:
        """True if the device answers. False for any connection failure."""
        try:
            self._get("/documents/")
            return True
        except RemarkableError:
            return False

    def list(self, folder_id: str = "") -> list[Item]:
        """List a folder. Empty folder_id lists the root."""
        path = f"/documents/{folder_id}" if folder_id else "/documents/"
        return [Item.from_json(x) for x in self._get_json(path)]

    def folders(self, folder_id: str = "") -> list[Item]:
        return [x for x in self.list(folder_id) if x.is_folder]

    def documents(self, folder_id: str = "") -> list[Item]:
        return [x for x in self.list(folder_id) if not x.is_folder]

    def find_folder(self, name: str, parent: str = "") -> Item | None:
        """Find a folder by exact name, case-insensitively, in one parent."""
        target = name.strip().lower()
        for item in self.folders(parent):
            if item.name.strip().lower() == target:
                return item
        return None

    def walk(self, folder_id: str = "", prefix: str = "") -> list[tuple[str, Item]]:
        """Every document on the device, paired with its folder path.

        Returns (path, item) where path is like "Books/Reference". Recurses
        through the whole tree, so on a full device this makes one request per
        folder.
        """
        found: list[tuple[str, Item]] = []
        for item in self.list(folder_id):
            if item.is_folder:
                child = f"{prefix}/{item.name}" if prefix else item.name
                found.extend(self.walk(item.id, child))
            else:
                found.append((prefix, item))
        return found

    def download(self, item_id: str, timeout: int | None = None) -> tuple[str, bytes]:
        """Fetch one document's export, as (filename, bytes).

        The device renders the export itself: a notebook comes back as a PDF of
        the pages, and an annotated PDF comes back with the annotations burned
        in. The raw .rm stroke data is not served here, so this is a readable
        copy, not a restorable one.

        The filename comes from Content-Disposition when the device sends it,
        which it does inconsistently across firmware versions; callers should
        be ready to fall back to the document's VisibleName.
        """
        path = f"/download/{item_id}/placeholder"
        try:
            with self._opener.open(
                f"{self.host}{path}", timeout=timeout or self.timeout
            ) as r:
                disposition = r.headers.get("Content-Disposition", "")
                return _filename_from(disposition), r.read()
        except OSError as exc:
            # URLError and TimeoutError are both OSError. Catching only the
            # former lets a slow render crash the caller mid-backup.
            raise RemarkableError(f"download {item_id} failed: {exc}") from exc

    # -- writing -----------------------------------------------------------

    def upload_to(self, path: Path, folder_id: str = "") -> None:
        """Upload one file, into folder_id when given.

        Ordering matters and is not incidental. The GET sets the server's
        current folder; the POST that follows lands there. Splitting these
        across connections or reordering them sends the file to the root.

        This cannot be undone from this interface. Check for duplicates before
        calling it.
        """
        if path.suffix.lower() not in SUPPORTED_SUFFIXES:
            raise RemarkableError(
                f"{path.name}: unsupported format {path.suffix!r}, "
                f"expected one of {sorted(SUPPORTED_SUFFIXES)}"
            )
        if not path.is_file():
            raise RemarkableError(f"{path}: not a file")

        # Select the destination folder, then upload into it.
        self._get(f"/documents/{folder_id}" if folder_id else "/documents/")

        body, content_type = _multipart(path)
        request = urllib.request.Request(
            f"{self.host}/upload",
            data=body,
            headers={"Content-Type": content_type},
            method="POST",
        )
        try:
            with self._opener.open(request, timeout=self.timeout) as response:
                if response.status != 201:
                    raise RemarkableError(
                        f"{path.name}: upload returned {response.status}, expected 201"
                    )
        except urllib.error.URLError as exc:
            raise RemarkableError(f"{path.name}: upload failed: {exc}") from exc

    # -- plumbing ----------------------------------------------------------

    def _get(self, path: str) -> bytes:
        try:
            with self._opener.open(f"{self.host}{path}", timeout=self.timeout) as r:
                return r.read()
        except urllib.error.URLError as exc:
            raise RemarkableError(f"GET {path} failed: {exc}") from exc

    def _get_json(self, path: str):
        raw = self._get(path)
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RemarkableError(f"GET {path} returned invalid JSON") from exc


def _multipart(path: Path) -> tuple[bytes, str]:
    """Build a multipart/form-data body with the single field the device wants."""
    boundary = uuid.uuid4().hex
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    head = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{path.name}"\r\n'
        f"Content-Type: {mime}\r\n\r\n"
    ).encode()
    tail = f"\r\n--{boundary}--\r\n".encode()
    return head + path.read_bytes() + tail, f"multipart/form-data; boundary={boundary}"


def normalise(name: str) -> str:
    """Reduce a filename to a key for duplicate detection.

    The device drops the extension from VisibleName for some formats and keeps
    it for others, so comparisons ignore the suffix, case, and punctuation.
    """
    stem = Path(name).stem.lower()
    return "".join(c for c in stem if c.isalnum())


def _filename_from(disposition: str) -> str:
    """Pull the filename out of a Content-Disposition header, or return "".

    Handles both filename="x.pdf" and the RFC 5987 filename*=UTF-8''x.pdf form.
    """
    for part in disposition.split(";"):
        part = part.strip()
        for key in ("filename*=", "filename="):
            if part.lower().startswith(key):
                value = part[len(key):].strip().strip('"')
                if key == "filename*=" and "''" in value:
                    value = urllib.parse.unquote(value.split("''", 1)[1])
                return Path(value).name
    return ""
