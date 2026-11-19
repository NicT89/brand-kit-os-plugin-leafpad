---
description: Schedule a future Leafpad-AI-generated post with brand voice cues. Leafpad generates the post at the scheduled time using its own AI + your Writing Style + Knowledge Base.
argument-hint: '"<title or topic>" <ISO-8601 datetime>'
---

# AI Schedule

Schedule a brand-aware future post via Leafpad's AI scheduler. **Leafpad generates the post**, not us. This command prepares a brand-aware brief (target keyword as `title`, the full brief as `prompt`, plus keyword data) and hands it to `leafpad_add_scheduled_posts`.

> **Cost and visibility.** Each scheduled post costs **$1** when it runs. The `brand-kit-os` account **auto-publishes at generation** (observed 2026-11-18: row 1702 became live post 2198 three minutes after its slot), so the post is public a few minutes after the date you pick. Run `/brand-kit-os-leafpad:post-qa` after it generates.

Use this when you want a stream of brand-aligned posts on autopilot, or when you want a calendar of future topics that Leafpad fills in at the right time.

For hand-crafted posts you've drafted with full brand context, use `/brand-kit-os-leafpad:publish-pipeline --draft` or `--publish` instead. Leafpad has no `publish_at` field, so a "schedule my hand-crafted draft" workflow is currently not possible; see `LEAFPAD_REQUESTS.md`. For the recurring two-posts-a-week flow, use `/brand-kit-os-leafpad:weekly-schedule`.

## Arguments

`$ARGUMENTS` should be:

```
"<target keyword or topic>" <ISO-8601 datetime> [--volume N] [--kd N] [--intent informational|commercial|transactional|navigational] [--parent <post id>]
```

Examples:

```
/brand-kit-os-leafpad:ai-schedule "3 ways retention beats acquisition for B2B SaaS" 2026-06-15T13:00:00Z

/brand-kit-os-leafpad:ai-schedule "Building a brand-first content engine" 2026-07-01T09:30:00-04:00
```

## Workflow

Delegates to the `leafpad-ai-scheduler` agent. The agent:

1. Resolves the active brand kit (`get_agent_briefing`)
2. Loads brand context (`get_brand_context_for_agent` with `task_type: "content_generation"`, `platform: "blog"`, plus `get_brand_kit` `sections: ["products"]`)
3. Dedupes against `leafpad_list_posts` and `leafpad_list_scheduled_posts`; if a pending row already holds the slot, updates it with `leafpad_update_scheduled_post` instead of adding one
4. Composes the brief per `references/scheduled-brief-template.md` (11 parts) and checks its prose with `check_draft`
5. Calls `leafpad_add_scheduled_posts` with `organization_slug` and `posts: [{ title, date, prompt, volume, kd, intent, post_type, parent_id, parent_scheduled_post_id }]`
6. Reports the scheduled post id, every field sent (prompt verbatim), the $1 cost and the auto-publish note

## Output

See `agents/leafpad-ai-scheduler.md` "Output format" section.

## When this is NOT the right command

- You want to publish a **specific finished draft** at a later time → not possible today; Leafpad has no `publish_at`. Use `--draft` and publish manually at the target time.
- You want a **calendar of N posts** scheduled across a date range: use `/brand-kit-os-leafpad:plan-week` then `/brand-kit-os-leafpad:execute-calendar`, or `/brand-kit-os-leafpad:weekly-schedule` for the Tuesday and Thursday cadence.
- You want to **change or cancel** a queued post: `leafpad_list_scheduled_posts` shows the queue; `leafpad_update_scheduled_post` changes a pending row and `leafpad_delete_scheduled_posts` removes it (never charged).

## Rules

1. The title (target keyword) is mandatory: don't derive it from a vague topic without confirming with the user
2. The ISO timestamp must be in the future
3. The prompt always carries the brand's full negative directory and hard writing constraints
4. Always show the user the full prompt that was sent to Leafpad: it is the only artifact they can review before the post goes live
5. Fill `volume`, `kd` and `intent` whenever they are known; say so when they are not

## When no brand kit is found

If `get_agent_briefing` lists no kits, inform the user:
> "No brand kits found. Create a brand kit at brandkitos.com to use AI scheduling."
