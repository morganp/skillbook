---
name: remarkable
description: >
  Push books and documents onto a reMarkable tablet over its USB web interface,
  into a chosen folder on the device, skipping anything already there, and
  manage the tablet's files through rmapi against the self-hosted rmfakecloud.
  Use this skill whenever the user wants to copy, send, push, sync, or load PDFs
  or EPUBs onto a reMarkable, organise, move, rename, delete, or create folders
  for reMarkable files, back up documents, or check what the device already
  holds. Also trigger on mentions of rmapi, rmfakecloud, rmcloud, pairing rmapi,
  the daily brief upload, 10.11.99.1, the reMarkable USB web interface, or moving
  books from a downloads folder or a library share onto the tablet.
---

# reMarkable

Pushes PDFs and EPUBs onto a reMarkable over USB, into a named folder, without
creating duplicates.

## Before anything else

The device must be connected over USB with the web interface enabled in
**Settings > Storage > USB web interface**. Wi-Fi does not serve this API.

```bash
python3 scripts/rm_push.py --list
```

This prints the device's folders and their document counts. If it reports no
device, stop and tell the user to check the cable and that setting. Do not
proceed on the assumption it will come back.

## What this interface can and cannot do

Read this before promising anything. The limits are the device's, not the
script's.

| Action | Supported |
|---|---|
| List folders and documents | Yes |
| Upload a PDF or EPUB into an existing folder | Yes |
| Download a document | Yes |
| Delete a document | **No** |
| Create a folder | **No** |
| Move or rename anything | **No** |

Everything marked No here is available through `rmapi` against the self-hosted
rmfakecloud; see [rmapi and the self-hosted rmfakecloud](#rmapi-and-the-self-hosted-rmfakecloud).
The tablet is already paired with it, so reach for `rmapi` first for deleting,
creating folders, moving and renaming, and treat this interface as the fallback.

Two consequences shape every task:

**Uploads are permanent from here.** Nothing in this interface removes a
document. A mistaken upload has to be deleted by hand on the tablet. Always show
the user the plan before uploading, and never pass `--push` on a first run.

**Folders must already exist.** When the user asks for a destination that is not
on the device, do not invent it or fall back to the root silently. Say the
folder does not exist, list what does, and ask them to create it on the tablet.

Only `.pdf` and `.epub` upload. A `.mobi`, `.prc`, `.azw3`, or `.cbz` needs
converting first, which this skill does not do.

## Pushing books

Always plan first. Without `--push` the script only reports.

```bash
# Plan: what would go, what is already there
python3 scripts/rm_push.py --from ~/Downloads --to Books

# Upload, once the user has seen the plan
python3 scripts/rm_push.py --from ~/Downloads --to Books --push
```

Useful flags:

- `--match <text>` keeps only files whose name contains the text, which is the
  usual way to pick a handful out of a large folder.
- `--recursive` descends into subdirectories, needed for a library organised
  into category folders.
- `--force` uploads even when a match is already on the device.
- `--to` takes a folder name, not an ID. Omit it to target the root.

Duplicate detection compares against every document on the device, not only the
target folder, so a book already filed elsewhere is not sent twice. Matching
ignores case, punctuation, and the file extension, because the device stores
`VisibleName` inconsistently between formats.

## Where books live

When the user says "my downloads" or names no path at all, check these before
concluding a book is missing. More than one is usually in play, and the obvious
one is often not where the file is:

| Location | Path |
|---|---|
| iCloud Drive downloads | `~/Library/Mobile Documents/com~apple~CloudDocs/Downloads` |
| Local downloads | `~/Downloads` |
| A library share | wherever the user mounts it, such as `/Volumes/<share>` |

**Check iCloud Drive first on macOS.** Browser and app downloads land there
whenever the user has Desktop and Documents syncing enabled, so `~/Downloads`
can be empty or stale while the real files sit in iCloud. Searching only
`~/Downloads` and reporting "no matching books" is a wrong answer, not an empty
result.

### Files iCloud has evicted

macOS removes local copies of iCloud files to reclaim space and leaves a hidden
placeholder named `.<filename>.icloud`. The file still appears in Finder but has
no local content, and a plain directory listing does not show it at all.

`collect()` detects these and reports them separately rather than skipping them
silently. When the script lists evicted files, ask macOS to fetch them and run
the plan again:

```bash
brctl download "~/Library/Mobile Documents/com~apple~CloudDocs/Downloads"
```

Download completes in the background, so a large file may need a second attempt.

## Choosing what to send

When the user names a source vaguely, such as "my books" or "the woodworking
ones", resolve it before uploading rather than guessing:

1. Run the plan and show the list of titles.
2. Ask which to send when the list is long or clearly mixed.
3. Upload only what they confirm.

A large source directory is the normal case. `~/Downloads` holding a hundred
books is not a reason to send a hundred books.

## Backing up the device

`scripts/rm_backup.py` pulls every document off the tablet into a mirrored
folder tree on disk. Plan first, as always:

```bash
python3 scripts/rm_backup.py              # what would be downloaded, and where
python3 scripts/rm_backup.py --run        # download it
```

Default destination is `~/Documents/remarkable-backup/<today>`; `--out` picks
another. Re-running resumes, skipping files already on disk, so an interrupted
backup is restarted by running the same command again. `--force` re-downloads
everything.

Each run writes a `manifest.json` beside the files listing every document's
device ID, folder, saved path, size, and SHA-256.

**This is a readable archive, not a restorable one.** The interface serves the
device's own export of each document: a notebook comes back as a PDF of its
pages, and an annotated PDF comes back with the annotations flattened into it.
The raw `.rm` stroke data is never served over USB, so nothing here puts
layers, or the documents themselves, back onto a device. Say this plainly
before anyone wipes a tablet on the strength of a backup from this script.

If the device has developer mode and a self-hosted cloud (rmfakecloud), prefer
`rmapi` over this script. `rmapi get` returns a `.rmdoc` carrying the raw `.rm`
stroke files and the untouched source document, which is a genuinely restorable
backup, and it can also create folders, move and delete. See
[rmapi and the self-hosted rmfakecloud](#rmapi-and-the-self-hosted-rmfakecloud)
for the invocation. These USB scripts stay the only option before developer mode
is enabled.

### Pacing, and the document that kills the server

The device renders every export on demand, and it is easily overwhelmed. All
three of these were observed on a reMarkable Paper Pro:

- Its own renderer gives up around 15 seconds and returns **HTTP 408**. A longer
  client timeout does not help: the timeout is the device's, not the client's.
- Pushed past that it answers **HTTP 400 to everything**, including documents
  that downloaded fine moments earlier.
- Pushed further the web server **dies outright** (connection refused) and has
  to be restarted from the tablet: Settings > Storage > USB web interface off
  then on, or a reboot.

So `rm_backup.py` paces itself: two seconds between documents, 30s and 90s rests
between retries, and it stops after three consecutive failures rather than
hammering a device that has already given up. Do not remove that pacing to make
a backup finish faster; it is what makes it finish at all.

A single malformed document can take the whole session down. One PDF reliably
killed the web server on every attempt, which then failed every document after
it and looked like a general fault. Exclude it and continue:

```bash
python3 scripts/rm_backup.py --run --skip deadsimplepython
```

`--skip` matches a device ID or a substring of the name, and repeats. When a run
ends with many consecutive failures, suspect one poisonous document rather than
a broken device: check whether the failures start at a particular file, skip it,
and re-run. Failed entries are recorded in `manifest.json` with an `error`
field, so the outstanding set explains itself.

Connection refused is treated differently from a document-level failure. It
means the server is gone rather than the document being bad, so the script stops
immediately and tells you to restart the interface.

## Reading the device

`scripts/rm_api.py` is importable for anything the command line does not cover:

```python
from rm_api import Remarkable

device = Remarkable()
for path, item in device.walk():
    print(f"{path or 'root'}: {item.name}")
```

`walk()` returns every document with its folder path, which answers "what is
already on the tablet" and "where does this book live". It makes one request per
folder, so it is slower than a single listing.

## How folder targeting works

Worth knowing, because it looks wrong and is easy to break. The upload request
carries no parent field. The device remembers the last folder listed on the
connection and puts the upload there, so `upload_to()` issues a
`GET /documents/<id>` immediately before the `POST /upload`.

Keep those two calls together, on the same `Remarkable` instance. Reordering
them, or splitting them across instances, silently sends the file to the root
instead of failing.

## rmapi and the self-hosted rmfakecloud

The tablet syncs to a self-hosted rmfakecloud rather than reMarkable's cloud.
`rmapi` talks to that server, and it does everything the USB interface cannot:
create folders, delete, move and rename, and pull restorable backups. It works
over the network, so no cable is needed.

### The server

rmfakecloud v0.0.31 runs in LXC 123 ("rmcloud") under Docker Compose at
`/opt/rmfakecloud`, listening on port 3000. `STORAGE_URL` is deliberately unset
so that both of the URLs below work. Leave it unset.

| Reach it from | URL |
|---|---|
| LAN: the web UI, and rmapi on LXC 117 | `http://192.168.100.123:3000` |
| Tailnet: the tablet and the Mac | `https://rmcloud.tail48dece.ts.net` |

The tailnet URL is published with `tailscale serve` and has a valid Let's
Encrypt certificate. Always use the hostname, never the tailnet IP, or the
certificate will not match.

### Install

Use the ddvk/rmapi fork (latest v0.0.35).

- **LXC 117:** `/usr/local/bin/rmapi`, with its config at
  `/root/dotfiles/config/rmapi/rmapi.conf`. rmapi finds it through
  `XDG_CONFIG_HOME=/root/dotfiles/config`.
- **Mac:** installed and paired against the tailnet URL.

### Pairing

1. Set `RMAPI_HOST` to the server URL for this machine.
2. Run `rmapi`. It asks for a one-time code.
3. Open the rmfakecloud web UI, go to the **Connect** page, and generate a code.
   It is valid for 5 minutes.
4. Enter it. The token is written to the config file.

### The trap: the config does not know its server

**The config file does not record which host it was paired against.** Run
`rmapi` without `RMAPI_HOST` and it talks to the real reMarkable cloud and
overwrites the stored token. This has happened, and the fix was a
fresh pairing.

So:

- **Always set `RMAPI_HOST`**, on every invocation, including one-off checks.
- Prefer `RMAPI_CONFIG=<path>` with one config file per server, so a mistake
  can only damage the config for the server it was aimed at.

The canonical invocation from the PVE host:

```bash
pct exec 117 -- env HOME=/root XDG_CONFIG_HOME=/root/dotfiles/config \
  RMAPI_HOST=http://192.168.100.123:3000 /usr/local/bin/rmapi <cmd>
```

### Commands

Verified working against this server:

| Command | Does |
|---|---|
| `ls [folder]` | List a folder |
| `mkdir <path>` | Create a folder |
| `put <file> [folder]` | Upload a PDF or EPUB into a folder |
| `get <path>` | Download as a `.rmdoc`, a restorable backup with the raw `.rm` strokes |
| `rm <path>` | Delete a document, or a directory (there is no `rmdir`) |
| `mv <src> <dest>` | Move into a folder, or rename by giving a new name |

Useful environment variables:

- `RMAPI_TRACE=1` logs every request, the first thing to reach for when a
  command fails silently.
- `RMAPI_CONCURRENT` sets how many transfers run in parallel.
- `RMAPI_FORCE_SCHEMA_VERSION` pins the sync schema version rather than letting
  rmapi detect it.

### Before any server-side move or delete

rmapi edits the server copy. If the tablet holds annotations it has not synced
yet, a server-side move or delete conflicts with them, and the annotations can
be lost.

- **Let the tablet sync first.** Wake it, confirm it is online, and wait for it
  to settle before running `mv` or `rm`.
- **Never delete or replace a document as cleanup** without first checking the
  tablet for unsynced annotations on it. A duplicate that looks redundant may be
  the copy the user has been writing on.

### The web UI cannot move or rename

The rmfakecloud web UI (v0.0.31) has no move or rename. The backend does
implement it, as `PUT /ui/api/documents` taking `{documentId, parentId, name}`,
but the UI never calls it, and sending an empty `name` blanks the document's
title. Do not call that endpoint by hand. Use `rmapi mv`, or do it on the
tablet.

### The daily brief

`/opt/rmbriefing/generate_daily_brief.sh` on LXC 117 runs from cron at 05:00.
It pushes the day's PDF with `rmapi put "$PDF" Daily`, and falls back to
`rmapi put --content-only` when that fails. When the brief does not appear on
the tablet, check this script's rmapi call and its `RMAPI_HOST` first.
