# Routine: Monthly editorial calendar

Plan a full month of content in one pass, then schedule it across the month.

## The pattern

```
/brand-kit-os-leafpad:plan-week --count 12 --start 2026-07-01
/brand-kit-os-leafpad:execute-calendar
```

`--count 12` plans roughly 3 posts/week across the month. `topic-scout` distributes ideas across themes so the month has variety rather than 12 takes on one subject. The calendar lands in `~/.brand-kit-os-leafpad/calendars/week-2026-07-01.json` (despite the `week-` prefix, it holds the full range you requested).

## Claude Desktop / Cowork

Create a **scheduled session for the 1st of each month at 8:00 AM**:

```
Run /brand-kit-os-leafpad:plan-week --count 12 --start <first of this month> to
research and build this month's editorial calendar across my preferred posting
days. Then show me the calendar for review before I execute it.
```

Leave execution as a manual confirmation step the first few months — a month of content is worth a human glance before it's scheduled. Once confident, append:

```
...then run /brand-kit-os-leafpad:execute-calendar to schedule them all.
```

## Balancing the month

Ask `topic-scout` (via `/plan-week`) to balance across themes by passing `--themes`:

```
/brand-kit-os-leafpad:plan-week --count 12 --themes "product education, industry trends, customer stories, thought leadership"
```

This nudges the calendar toward a healthy editorial mix rather than clustering.

## Refresh mid-month

News changes. If a major industry event lands mid-month, re-run `/plan-week` for the remaining days and merge — `topic-scout` dedups against what's already scheduled and on the blog.

## See also

- [`weekly-3-articles.md`](weekly-3-articles.md) — the weekly cadence and per-host scheduling setup
- The `topic-sourcing` skill — registry setup that powers research quality
