#!/usr/bin/env python3
"""Safely restore Codex's full-access settings in the active user config."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import shutil
import stat
import tempfile

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 and older
    tomllib = None


SETTINGS = {
    "sandbox_mode": '"danger-full-access"',
    "approval_policy": '"never"',
}
ASSIGNMENT = re.compile(r"^\s*(sandbox_mode|approval_policy)\s*=\s*(.*?)\s*(?:#.*)?$")
TABLE = re.compile(r"^\s*\[")


def config_path() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    root = Path(codex_home).expanduser() if codex_home else Path.home() / ".codex"
    return root / "config.toml"


def inspect(text: str) -> tuple[list[str], dict[str, list[int]], int]:
    lines = text.splitlines(keepends=True)
    found = {key: [] for key in SETTINGS}
    first_table = len(lines)
    for index, line in enumerate(lines):
        if TABLE.match(line):
            first_table = index
            break
        match = ASSIGNMENT.match(line)
        if match:
            found[match.group(1)].append(index)
    return lines, found, first_table


def current_values(text: str) -> dict[str, str | None]:
    lines, found, _ = inspect(text)
    values: dict[str, str | None] = {}
    for key, indices in found.items():
        if len(indices) > 1:
            raise ValueError(f"duplicate root-level setting: {key}")
        if not indices:
            values[key] = None
            continue
        match = ASSIGNMENT.match(lines[indices[0]])
        values[key] = match.group(2).strip() if match else None
    return values


def render(text: str) -> str:
    lines, found, first_table = inspect(text)
    for key, indices in found.items():
        if len(indices) > 1:
            raise ValueError(f"duplicate root-level setting: {key}")
        if indices:
            newline = "\r\n" if lines[indices[0]].endswith("\r\n") else "\n"
            lines[indices[0]] = f"{key} = {SETTINGS[key]}{newline}"

    missing = [key for key, indices in found.items() if not indices]
    if missing:
        newline = "\r\n" if "\r\n" in text else "\n"
        additions = [f"{key} = {SETTINGS[key]}{newline}" for key in missing]
        if first_table and lines and lines[first_table - 1].strip():
            additions.append(newline)
        lines[first_table:first_table] = additions
    return "".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="check without modifying")
    args = parser.parse_args()

    logical_path = config_path()
    path = logical_path.resolve() if logical_path.exists() else logical_path
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    expected = {key: value for key, value in SETTINGS.items()}
    values = current_values(text)

    if values == expected:
        print(f"YOLO settings already active in {logical_path}")
        return 0
    if args.check:
        for key in SETTINGS:
            print(f"{key}: {values[key] or '<missing>'} -> {SETTINGS[key]}")
        return 1

    updated = render(text)
    if tomllib is not None:
        tomllib.loads(updated)
    path.parent.mkdir(parents=True, exist_ok=True)
    backup = path.with_name(path.name + ".codex-yolo.bak")
    if path.exists():
        shutil.copy2(path, backup)

    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o600
    fd, temporary_name = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(updated)
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass

    print(f"Updated {logical_path}")
    if backup.exists():
        print(f"Backup: {backup}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
