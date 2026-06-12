---
description: Schedule a future Leafpad-AI-generated post with brand voice cues. Leafpad generates the post at the scheduled time using its own AI + your Writing Style + Knowledge Base.
argument-hint: "<title or topic>" <ISO-8601 datetime>
---

# AI Schedule

Schedule a brand-aware future post via Leafpad's AI scheduler. **Leafpad generates the post**, not us — this command prepares a brand-aware brief (title + secondary prompt) and hands it to `leafpad_add_scheduled_posts`.

Use this when you want a stream of brand-aligned posts on autopilot, or when you want a calendar of future topics that Leafpad fills in at the right time.

For hand-crafted posts you've drafted with full brand context (richer, more controlled), use `/brand-kit-os-leafpad:publish-pipeline --draft` or `--publish` instead. Leafpad has no `publish_at` field, so a "schedule my hand-crafted draft" workflow is currently not possible — see `LEAFPAD_REQUESTS.md`.

## Arguments

`$ARGUMENTS` should be:

```
"<title or topic>" <ISO-8601 datetime>
```

Examples:

```
/brand-kit-os-leafpad:ai-schedule "3 ways retention beats acquisition for B2B SaaS" 2026-06-15T13:00:00Z

/brand-kit-os-leafpad:ai-schedule "Building a brand-first content engine" 2026-07-01T09:30:00-04:00
```

## Workflow

Delegates to the `leafpad-ai-scheduler` agent. The agent:

1. Resolves the active brand kit
2. Loads brand context (expression, governance, audience, products)
3. Refines the title to be brand-voice-consistent
4. Composes a secondary prompt encoding voice, audience, governance constraints, and structural guidance
5. Calls `leafpad_add_scheduled_posts` with `{ title, scheduled_at, secondary_prompt }`
6. Reports the scheduled post id, the secondary prompt verbatim, and notes about how Leafpad will use it

## Output

See `agents/leafpad-ai-scheduler.md` "Output format" section.

## When this is NOT the right command

- You want to publish a **specific finished draft** at a later time → not possible today; Leafpad has no `publish_at`. Use `--draft` and publish manually at the target time.
- You want a **calendar of N posts** scheduled across a date range → wait for `/brand-kit-os-leafpad:plan-week` in v1.6.0, which iterates this command.

## Rules

1. The title is mandatory — don't try to derive it from a vague topic without confirming with the user
2. The ISO timestamp must be in the future
3. The secondary prompt always references the brand's negative directory if one exists
4. Always show the user the full secondary prompt that was sent to Leafpad — this is the only artifact they can review before the AI-generated post lands

## When no brand kit is found

If `list_brand_kits` returns no results, inform the user:
> "No brand kits found. Create a brand kit at brandkitos.com to use AI scheduling."
