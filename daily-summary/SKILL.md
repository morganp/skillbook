---
name: daily-summary
description: Produce a fresh, read-only summary of SecondBrain long-term goals, today's events, all-day events over the next 27 days, priorities, and outstanding actions. Use when the user asks for a daily summary, daily brief, todo or task list, priority rundown, outstanding work, "what's next", or to refresh the day; support repeated invocations throughout the same day without creating duplicate records.
---

# Daily Summary

Generate a concise snapshot from the loaded SecondBrain connector. Treat every invocation as a fresh query, even when the skill has already run that day.

## Retrieve

1. Use the session's current local date and time.
2. Query today's events with `list_events`, setting both `from` and `to` to today's date.
3. Query upcoming all-day events with `list_events`, from tomorrow through 27 days after today. Keep today out of this second window.
4. Query `list_areas` to locate the active long-term goals area. Ignore `areas/calendar/*`, read `areas/goals.md` when present, and extract only explicit goals rather than treating every ongoing responsibility as a goal.
5. Query `list_actions` for all active stages. Apply the user's requested domain to actions and areas when one is supplied.
6. Do not read archived actions or areas unless the user explicitly asks for completed work or history.
7. Do not write, append, edit, archive, or otherwise change the vault while generating the summary.

Batch independent SecondBrain reads into one parallel tool step when the host supports it. Keep progress commentary to a single brief update unless an error or decision needs the user's attention.

Deduplicate events that overlap both windows. Show an ongoing event under **Today** and do not repeat it under **Next 27 days**.

If the SecondBrain connector is unavailable, say that the live summary cannot be loaded. Do not substitute workspace files or an inferred task list.

## Prioritize

Classify outstanding actions in this order:

1. Overdue.
2. Due today.
3. Due within the next seven days.
4. Undated `next` actions.
5. `waiting` actions.

Report the number of `someday` actions without expanding them unless the user asks. Preserve due dates and meaningful ownership or project context. Do not invent urgency, deadlines, status, or completion.

## Align Actions with Goals

For every action shown individually, compare its title, tags, and project context with the stored long-term goal titles, descriptions, and success measures.

- Add one primary goal and at most one clearly supported secondary goal.
- Format the annotation as `↳ Likely supports: <category icon> **<category>: <compact goal name>**`.
- Use the same category icons as the long-term-goals section.
- Write `↳ No clear goal link` when the available metadata does not support a defensible mapping.
- Treat every mapping as an inference unless the action explicitly stores a goal relationship. Do not claim that an inferred link proves progress, completion, or measurable impact.
- Do not attach goal mappings to aggregate action counts because the actions within a count may support different goals.

## Present

Start with `As of <local date and time>`. Use these icon-labelled Markdown headings for non-empty sections:

- `### 📅 Today` for calendar events.
- `### 🗓️ Next 27 days` for future all-day events, with dates or date ranges.
- `### 🔴 Overdue` for overdue actions.
- `### 🟠 Due today` for actions due today; use orange as the portable Markdown approximation of amber.
- `### 📆 Next seven days`.
- `### 📋 Next, no due date`.
- `### ⏳ Waiting`.
- `💭 <count> someday actions hidden.` as a compact standalone line.
- `### 🎯 Long-term goals` as the final section, with compact reminders from active areas.

Begin every long-term-goal sentence with its category label and icon:

- `💼 **Work:**` for work delivery and engineering goals.
- `🤝 **DEI:**` for diversity, equity, inclusion, and collaborative-participation goals.
- `🌱 **Development:**` for professional development goals.
- `🏠 **Personal:**` for personal goals, including unlabelled goals such as hobbies.

Preserve an explicit category from the goal heading. Infer `Personal` only when no category is stored. Use emoji indicators rather than HTML or ANSI colour because those formats do not render consistently across Codex surfaces.

When the user requests a particular domain's actions, list every matching non-`someday` action individually and include its goal alignment. Otherwise, keep entries compact and action-oriented. If a general daily summary is long, show urgent and dated work first, summarize the remainder by domain, and offer to expand a domain. On repeated calls, return the current state without commenting on earlier snapshots unless the user asks for a comparison.
