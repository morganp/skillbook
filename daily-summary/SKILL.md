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

## Present

Start with `As of <local date and time>`. Include only non-empty sections:

- **Today** for calendar events.
- **Next 27 days** for future all-day events, with dates or date ranges.
- **Long-term goals** for compact reminders from active areas.
- **Overdue**.
- **Due today**.
- **Next seven days**.
- **Next, no due date**.
- **Waiting**.
- A final count of hidden `someday` actions.

Keep entries compact and action-oriented. If the result is long, show urgent and dated work first, summarize the remainder by domain, and offer to expand a domain. On repeated calls, return the current state without commenting on earlier snapshots unless the user asks for a comparison.
