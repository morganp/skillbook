  ---
  name: close
  description: >
    Session-end "flush to second brain": review the active conversation and append its
    durable knowledge into the right notes of the brain vault — the markdown knowledge wiki
    served by the brain-mcp server. Trigger when the user types /close or says "close the
    session", "flush this to my second brain", "save what we learned", "update the wiki from
    this session", "file the knowledge", or any end-of-session capture request. Routes
    project progress, decisions, new tasks/ideas, reusable reference knowledge, and new
    glossary terms to their canonical homes; proposes the changes before writing.
  ---

  # Close — flush the session into the second brain

  ## Overview

  At the end of a working session, knowledge you generated lives only in the chat. `/close`
  harvests that knowledge and files it into the **brain vault** (the personal markdown wiki
  served by `brain-mcp`) so it survives the session. The vault is the **single source of
  truth**; this skill only ever writes there — never to the public blog.

  It is deliberately **propose-then-write**: it shows you a routing plan and waits for your
  OK before touching any file, so nothing is invented or silently changed.

  ## Prerequisites

  - The **brain-mcp** server is connected. Expected tools: `list_projects`, `list_actions`,
    `list_areas`, `grep`, `read_text`, `write_text`, `append`, `edit`, `glossary_add`,
    `archive_project` / `archive_action` / `archive_area`.
  - If brain-mcp is **not** connected, say so and stop — do not write knowledge anywhere else.
  - Conventions are defined by the vault itself: `README.md` (behavior layer), `CLAUDE.md`,
    and `reference/knowledge-architecture.md`. If they diverge from this skill, defer to them.

  ## Workflow

  ### 1 — Harvest
  Scan the active session for **durable** knowledge, grouped into:
  - **Project progress / decisions** — work done, choices made, new `next_action`.
  - **New tasks or ideas** — anything to do later.
  - **Reference knowledge** — reusable facts, how-tos, gotchas worth looking up again.
  - **New glossary terms** — a term + one-line definition.
  - **Public-worthy items** — knowledge the user may want to blog.

  Ignore: ephemeral chatter, things already filed, and **never** capture secrets, tokens,
  or credentials. Convert relative dates ("today", "next week") to absolute dates.

  ### 2 — Resolve targets (progressive disclosure — no bulk reads)
  For each item, find its canonical home using indexes and search, not by reading the vault:
  - `list_projects` / `grep` to locate the matching project or reference note.
  - If none exists and the item warrants one, plan a **new** note from the relevant template
    (`projects/_template.md`, `actions/_template.md`, `areas/_template.md`).

  ### 3 — Propose
  Present a routing plan as a table and **wait for approval**:

  | Item (quoted from session) | Target | Action |
  |---|---|---|
  | "decided X over Y because…" | `projects/<id>.md` | append `## Log` + set `next_action` |
  | "should build a Z later" | `actions/build-z.md` (new) | `write_text`, `stage: someday` |
  | "term: telemetry = …" | `glossary.md` | `glossary_add` |

  Quote the user's own words; do not paraphrase facts into something they didn't say.

  ### 4 — Apply via brain-mcp
  On approval, route each item:
  - **Project worked on** → `edit` frontmatter (`last_touched`, `next_action`) + `append` a
    dated line under `## Log`.
  - **New task / idea** → `write_text` `actions/<id>.md` (`stage: someday|next|waiting`,
    `tags`, optional `due`).
  - **Durable lookup knowledge** → `append` to (or `write_text`) `reference/<id>.md`.
  - **New term** → `glossary_add`.
  - **Public-worthy** → set `visibility: public`, `blog_status: draft` on the note. Keep it
    in its PARA bucket; do **not** push to the blog from here (publishing is a separate,
    explicit step via blog-mcp).
  - **Completed / cancelled** → the matching `archive_*` tool.

  ### 5 — Confirm
  Summarise what was written (file → change). `brain-mcp` commits and pushes after each
  write; note the result. If a write returns a push error but saved locally, surface it.

  ## Rules

  - **Wiki is the single source of truth.** Never write knowledge to the blog from `/close`.
  - **Progressive disclosure.** Use `list_*` + `grep`; never bulk-read the vault.
  - **Propose before writing.** No fabrication; preserve the user's wording.
  - **No secrets.** Never store tokens, passwords, or credentials in the vault.
  - **Default private.** Only set `visibility: public` when the user said so or it is
    unambiguously public knowledge.
  - **One idea per note**; link related notes with `[[wikilinks]]`.

  ## Example

  > **User:** /close
  >
  > **Skill:** Harvested 3 items from this session:
  >
  > | Item | Target | Action |
  > |---|---|---|
  > | "switched the parser to streaming to fix the 2GB OOM" | `projects/log-ingest.md` | `## Log` + `next_action: add backpressure test` |
  > | "try clickhouse for the rollups later" | `actions/eval-clickhouse.md` (new) | `stage: someday`, tags `[code, data]` |
  > | "term: backpressure = flow-control that slows a producer to match a slow consumer" | `glossary.md` | `glossary_add` |
  >
  > Apply these? (y / edit)

  ## Notes

  This skill assumes the brain vault layout: PARA buckets (`projects/`, `actions/`, `areas/`,
  `reference/`, `archive/`), an always-on `memory/INDEX.md` brief, `glossary.md`, and
  `journal/<year>.md`. Public/private split follows `reference/knowledge-architecture.md`:
  the wiki is canonical, the blog is a projection of `visibility: public` notes.

  To land it from your clone:

  mkdir -p skillbook/close
  $EDITOR skillbook/close/SKILL.md   # paste the above
  cd skillbook
  git add close/SKILL.md
  git commit -m "feat: add close skill — flush active session into the second-brain wiki"
  git push
