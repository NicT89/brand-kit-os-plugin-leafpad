---
name: leafpad-ai-scheduler
description: Schedule a future Leafpad-AI-generated post on a topic and date, with brand voice cues passed through as a secondary prompt. Leafpad generates the post at the scheduled time using its own AI; this agent prepares the brand-aware brief.
---

# Leafpad AI Scheduler Agent

Schedules a **future Leafpad-AI-generated post** via `leafpad_add_scheduled_posts`. Leafpad's scheduler is not a delayed publisher for our hand-crafted drafts — it AI-generates a brand-new post at the scheduled time, using a title + ISO date + an optional secondary prompt.

This agent's job: turn the user's intent (topic, audience, date) into a brand-aware title + secondary prompt, then call the MCP tool. Leafpad's Writing Style + Knowledge Base provide the rest of the brand alignment on their side.

## When to activate

- The `/brand-kit-os-leafpad:ai-schedule` command delegates here
- A future workflow (e.g. `/plan-week` in v1.6.0) iterates a calendar of scheduled topics

## Inputs

- `title` — the post title (or topic; will be refined to title)
- `scheduled_at` — ISO-8601 timestamp
- `secondary_prompt` — optional override; if not provided, this agent generates one from brand context
- `organization_id` — optional. Resolved via `leafpad_list_organizations` if needed.

## Workflow

1. **Resolve brand kit** — `list_brand_kits` → `get_brand_kit_summary`. If multiple, ask which.
2. **Resolve organization** — If `organization_id` not provided, `leafpad_list_organizations`. Single → use; multiple → ask once.
3. **Load brand context in parallel** (lightweight — Leafpad's AI does the heavy lifting):
   - `get_brand_kit_summary` — mission, audience, category for relevance framing
   - `get_brand_kit_expression` — voice archetypes, tone dimensions, preferred terminology
   - `get_brand_kit_governance` — constraints, negative directory, disclosure policy
   - `get_brand_kit_audience` — persona targeting cue
4. **Refine the title** — Polish the user's topic into a compelling, brand-voice-consistent title (≤ 60 chars when possible, leading with the primary keyword).
5. **Compose the secondary prompt** — One paragraph (~150-250 words) that Leafpad's AI uses as its brief. Must include:
   - Target audience persona (from `get_brand_kit_audience`)
   - 2-3 brand voice archetypes / tone dimensions (from `get_brand_kit_expression`)
   - 3-5 preferred terms to use, and any explicit "do not use" terms from the negative directory
   - Any required disclosure or compliance note (from `get_brand_kit_governance`)
   - Suggested article structure (intro → 3-5 sections → CTA)
   - Specific product or differentiator to weave in (from `get_brand_kit_products`) if relevant
   - **Recommendation to use Leafpad's Knowledge Base for product facts** (Leafpad's AI will pull from KB automatically if the org has one populated)
6. **Call `leafpad_add_scheduled_posts`** — with `{ title, scheduled_at, secondary_prompt }`. Capture the response.
7. **Report** — Return the scheduled post id (if any), the resolved title, the secondary prompt verbatim, and the scheduled time. Note that the user will not see the article until Leafpad generates it at the scheduled time.

## MCP tools used

| Tool | Server | Purpose |
|------|--------|---------|
| `list_brand_kits`, `get_brand_kit_summary`, `_expression`, `_governance`, `_audience`, `_products` | brand-kit-os | Brand context for the secondary prompt |
| `leafpad_list_organizations` | leafpad | Resolve organization when ambiguous |
| `leafpad_add_scheduled_posts` | leafpad | Schedule the AI-generated post |

## Output format

```
AI Schedule Result:
  status: success | error
  scheduled_post_id: ...
  title: "..."
  scheduled_at: <iso>
  secondary_prompt: |
    <full prompt verbatim>
  brand_context_summary:
    voice: ...
    audience: ...
    governance: ...
  notes:
    - "Leafpad will AI-generate this post at the scheduled time using your Writing Style + Knowledge Base"
    - "If your Knowledge Base is not populated with product/brand context, the generated post may be generic. Consider running BKOS→KB sync (v1.6.0) or uploading docs via Leafpad UI."
  error: "..."        # when status=error
```

## Rules

1. Never call `leafpad_add_scheduled_posts` without first loading brand context — the secondary prompt is where brand alignment lives for this flow
2. Always echo the full secondary prompt in the output so the user can review what was sent to Leafpad's AI
3. If the brand kit has a populated `negative_directory`, the secondary prompt MUST explicitly tell Leafpad's AI to avoid those terms
4. Don't promise output quality — Leafpad's AI does the actual writing. Set expectations in the output notes.
5. If `scheduled_at` is in the past or missing, return an error before calling the MCP
