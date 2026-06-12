---
description: Research and build a content calendar of brand-relevant blog topics for the week (or any range), with proposed publish dates. Powered by the topic-scout research agent.
argument-hint: [--count N] [--start YYYY-MM-DD] [--themes "a, b, c"]
---

# Plan Week

Build an editorial calendar: research brand-relevant topics, then lay them out across a date range with proposed publish slots. This is the **planning** step — it produces a calendar file you review, then hand to `/execute-calendar` to schedule.

## Arguments

All optional:

- `--count N` — number of posts to plan (default: `topic_cadence.posts_per_week` from the registry, else 3)
- `--start YYYY-MM-DD` — first day of the range (default: next occurrence of the first preferred day)
- `--themes "a, b, c"` — bias the research toward specific themes

Examples:

```
/brand-kit-os-leafpad:plan-week
/brand-kit-os-leafpad:plan-week --count 3 --start 2026-06-15
/brand-kit-os-leafpad:plan-week --count 5 --themes "retention, onboarding, pricing"
```

## Workflow

1. **Resolve brand kit** — `get_brand_kit_summary`; if multiple, ask which.
2. **Load cadence** — Read `topic_cadence` from the sources registry (`~/.brand-kit-os-leafpad/registry.json`). Use it for `count`, preferred days, time, and timezone unless overridden by flags. If no registry, default to 3 posts on Mon/Wed/Fri at 09:00 UTC and suggest the user run setup (see the `topic-sourcing` skill).
3. **Research topics** — Delegate to the `topic-scout` agent with `count`, `themes`, and `avoid_recent: true`. It returns ranked topic briefs drawing from the registry's trusted sources, company updates (Leafpad KB), content gaps, and trending search.
4. **Assign slots** — Map the top `count` topics onto the preferred publish days/times starting from `--start`, distributing evenly across the range.
5. **Write the calendar file** — Save to `~/.brand-kit-os-leafpad/calendars/week-<start-date>.json` (a structured list of `{ title, angle, scheduled_at, audience, keywords, source, citation_candidates }`).
6. **Present** — Show the calendar as a readable table and tell the user how to execute it.

## Output format

```
Content Calendar — week of <start>
Brand: <brand kit name>   ·   Cadence: N posts   ·   Timezone: <tz>

| # | Date/Time        | Working Title                    | Audience      | Source         | Fit |
|---|------------------|----------------------------------|---------------|----------------|-----|
| 1 | Mon Jun 15, 9:00 | ...                              | ...           | company update | 88  |
| 2 | Wed Jun 17, 9:00 | ...                              | ...           | TechCrunch RSS | 82  |
| 3 | Fri Jun 19, 9:00 | ...                              | ...           | content gap    | 79  |

Saved to: ~/.brand-kit-os-leafpad/calendars/week-2026-06-15.json

Next steps:
- Review/edit the calendar file, or ask me to adjust any topic
- Run /brand-kit-os-leafpad:execute-calendar to schedule these via Leafpad's AI scheduler
- Or run /brand-kit-os-leafpad:publish-pipeline "<title>" to hand-craft any single post now
```

## Rules

1. Always use `topic-scout` for ideation — never invent topics directly in this command
2. Respect the registry's cadence and timezone; flags override per-run
3. Distribute posts across the range, don't bunch them
4. Save the calendar file so `/execute-calendar` can pick it up; never schedule directly from this command
5. If `topic-scout` returns fewer good ideas than `count`, present what it found and say so — don't pad with weak topics

## When no brand kit is found

> "No brand kits found. Create a brand kit at brandkitos.com to plan content."
