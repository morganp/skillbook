---
name: codex-yolo
description: Restore a user's Codex full-access (YOLO) preference after an update resets ~/.codex/config.toml. Use when Codex unexpectedly runs read-only or workspace-write, asks to restore YOLO/full access, or needs sandbox and approval settings repaired. Do not use to broaden permissions unless the user explicitly requests full access.
---

# Codex YOLO

Restore the active user configuration to Codex full access while preserving unrelated settings.

Full access requires both root-level TOML keys:

```toml
sandbox_mode = "danger-full-access"
approval_policy = "never"
```

## Workflow

1. Resolve the active file as `${CODEX_HOME:-$HOME/.codex}/config.toml`. Also inspect the user's tracked dotfiles source when one exists, but do not substitute it for the active file.
2. Run `python3 scripts/set_yolo.py --check` without elevated access. If it reports that the active file is already correct, verify the two root-level values directly and stop.
3. Immediately before mutation, request the user's permission to write the resolved active config path. State that the change disables the filesystem/network sandbox and future approval prompts. Use the environment's approval mechanism for the exact `python3 scripts/set_yolo.py` command; do not request broader access than needed.
4. If the current policy is `never` and therefore cannot raise an approval prompt, do not pretend approval was requested. Ask the user to open `/permissions`, select **Ask for approval**, and invoke `$codex-yolo` again. Stop without changing the active file.
5. After approval, run `python3 scripts/set_yolo.py`. The script preserves unrelated content, writes a sibling `.codex-yolo.bak` backup, validates TOML when the Python runtime provides `tomllib`, and atomically replaces the active file.
6. Run `python3 scripts/set_yolo.py --check`, then directly read the two active root-level keys. Use `codex doctor --json` to confirm that Codex parses the active config. Report the active path, backup path, and whether a new Codex session is required.

Run the script by absolute path when the current directory is not this skill directory. Never use a forced dotfiles installer merely to change these two keys because it can overwrite newer machine-local entries.

The current OpenAI documentation describes this pairing as **Full access**: <https://learn.chatgpt.com/docs/sandboxing>.
