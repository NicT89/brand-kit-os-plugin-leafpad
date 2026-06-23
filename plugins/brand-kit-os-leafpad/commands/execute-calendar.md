---
description: Take a content calendar produced by /plan-week and schedule each post on Leafpad via the AI scheduler. Optionally hand-craft posts instead of AI-scheduling them.
argument-hint: '[path-to-calendar.json] [--ai-schedule | --draft-now]'
---

# Execute Calendar

Turn a planned content calendar into scheduled Leafpad posts. Reads the calendar file from `/plan-week` and dispatches each entry.

## Arguments

- `path-to-calendar.json` — the calendar to execute (default: the most recent file in `~/.brand-kit-os-leafpad/calendars/`)
- `--ai-schedule` (default) — schedule each entry via Leafpad's AI scheduler (`leafpad_add_scheduled_posts`). Leafpad generates each post at its scheduled time using the brand-aware brief.
- `--draft-now` — instead of scheduling, hand-craft every post right now via the full `/publish-pipeline` and save each as a draft. Higher quality and fully brand-controlled, but generates everything immediately rather than at the scheduled time.

Examples:

```
/brand-kit-os-leafpad:execute-calendar
/brand-kit-os-leafpad:execute-calendar ~/.brand-kit-os-leafpad/calendars/week-2026-06-15.json
/brand-kit-os-leafpad:execute-calendar --draft-now
```

## Workflow

1. **Load the calendar** — Read the specified (or most recent) calendar file. Validate it has entries with `title` and `scheduled_at`.
2. **Confirm the plan** — Show the user the list of posts and the chosen mode (`ai-schedule` vs `draft-now`) and confirm before dispatching. This step writes to Leafpad, so confirmation matters.
3. **Dispatch each entry**:
   - **`--ai-schedule`** → for each entry, delegate to the `leafpad-ai-scheduler` agent with `{ title, scheduled_at, secondary_prompt (built from the entry's angle/audience/keywords) }`. Leafpad AI-generates the post at the scheduled time.
   - **`--draft-now`** → for each entry, run the `/publish-pipeline` flow (`content-generation` → `citation-validator` → `seo-optimizer` → `quality-assurance` → `leafpad-publisher` in `draft` mode). Produces fully brand-crafted drafts immediately.
4. **Track results** — Collect each dispatch's result (scheduled id or draft URL, plus any errors).
5. **Report** — A summary table of what was scheduled/drafted, with links and any failures. Update the calendar file to mark each entry's status.

## Output format

```
Calendar Execution — week of <start>   ·   Mode: ai-schedule | draft-now

| # | Title              | Scheduled For    | Status   | Link / ID        |
|---|--------------------|------------------|----------|------------------|
| 1 | ...                | Mon Jun 15 9:00  | scheduled| post_abc123      |
| 2 | ...                | Wed Jun 17 9:00  | scheduled| post_def456      |
| 3 | ...                | Fri Jun 19 9:00  | error    | (see note below) |

Errors:
- #3: <error message + what to do>

Calendar updated: ~/.brand-kit-os-leafpad/calendars/week-2026-06-15.json
```

## Rules

1. **Always confirm before dispatching** — this writes to Leafpad. Show the full plan and mode first.
2. In `--ai-schedule` mode, always pass a brand-aware secondary prompt — never schedule a bare title
3. In `--draft-now` mode, every post goes through QA before it's saved as a draft
4. On a per-entry failure, continue with the rest and report the failures at the end — don't abort the whole calendar
5. Update the calendar file with each entry's final status so re-running skips completed entries
6. Never delete the calendar file — the user owns it

## Routine automation

To run this on a schedule (e.g., every Monday), see `docs/routines/weekly-3-articles.md` — it shows how to wire `/plan-week` + `/execute-calendar` into a Claude Cowork scheduled session.
