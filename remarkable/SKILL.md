---
name: remarkable
description: >
  Push books and documents onto a reMarkable tablet over its USB web interface,
  into a chosen folder on the device, skipping anything already there. Use this
  skill whenever the user wants to copy, send, push, sync, or load PDFs or EPUBs
  onto a reMarkable, organise what is on the device, or check what the device
  already holds. Also trigger on mentions of 10.11.99.1, the reMarkable USB web
  interface, or moving books from a downloads folder or a library share onto the
  tablet.
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
