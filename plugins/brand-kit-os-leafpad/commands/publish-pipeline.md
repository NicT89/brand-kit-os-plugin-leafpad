---
description: End-to-end brand-aligned publish pipeline — draft, validate, and publish an article to Leafpad in one command.
argument-hint: <topic | brief | pasted source> [--draft|--publish|--schedule <iso>]
---

# Publish Pipeline

Take a topic, brief, or pasted source (digest, notes, transcript) and run the full publish flow: load brand context → draft → SEO + internal linking → QA → publish to Leafpad. Honors `${user_config.publish_mode}` unless the run overrides it with a flag.

## Arguments

`$ARGUMENTS` should be one of:

- A **topic** — e.g. `short post about retention loops for SaaS founders`
- A **brief** — a few sentences describing angle, audience, and key messages
- **Pasted source material** — a Cowork digest, meeting notes, a transcript, a research clipping

Optional override flags (any one of):

- `--draft` — publish as a draft regardless of `publish_mode`
- `--publish` — publish immediately regardless of `publish_mode`
- `--schedule <ISO-8601>` — schedule for the given timestamp

If no override is given, the run uses `${user_config.publish_mode}` (default `draft`).

## Workflow

1. **Resolve brand kit** — Call `get_brand_kit_summary` for the active brand. If multiple kits exist, call `list_brand_kits` and ask which to use.
2. **Parse arguments** — Extract topic / brief / source from `$ARGUMENTS` and detect any override flag. If the input is too thin to draft from (e.g. just a single word), ask one short follow-up before proceeding.
3. **Load brand context in parallel** — `get_brand_kit_expression`, `get_brand_kit_governance`, `get_brand_kit_audience`, `get_brand_kit_products`.
4. **Gather Leafpad context in parallel** — `leafpad_list_posts` (for internal-link candidates) and `leafpad_list_tags` (for tag reuse). Note: `leafpad_list_tags` may return `[]` per known limitation; that's fine — `seo-optimizer` handles it.
5. **Delegate drafting** — Call the `content-generation` agent with the `blog post` template, passing brand context and parsed brief.
6. **Delegate SEO + internal linking** — Call the `seo-optimizer` agent with the draft + brand kit id. Apply its `seo`, `internal_links`, and `tags` patch onto the article object (do not modify the body except to insert internal links where suggested).
7. **Delegate QA** — Call the `quality-assurance` agent against the enforcement checklist at `skills/brand-voice-enforcement/references/enforcement-checklist.md`. If a critical check fails, revise once and re-run QA. If it fails twice, stop and surface the QA report to the user — do not publish.
8. **Publish via `leafpad-publisher`** — Resolve `mode`:
   - Override flag (if present) wins
   - Otherwise use `${user_config.publish_mode}` (defaulting to `draft`)

   Pass `{ article, mode, scheduled_at? }` to `leafpad-publisher`.
9. **Report** — Output the published URL (or scheduled time / draft id), the mode used, and the Brand Application Notes.

## Output format

```
Publish Pipeline Result
  Mode: draft | published | scheduled (override flag used: yes/no)
  URL / Draft ID: ...
  Scheduled For: <iso>            # only when mode=scheduled

Brand Application Notes:
- Voice: [archetypes and attributes applied]
- Tone: [dimension settings and reasoning]
- Terminology: [notable choices from preferred_terminology]
- Governance: [constraints observed, disclosures included]
- Audience: [persona targeted]

SEO:
- Title: ...
- Description: ...
- Keywords: [...]
- Internal links inserted: N

Caveats (if any):
- "Tags couldn't be verified — leafpad_list_tags returned []"
```

## When no brand kit is found

If `list_brand_kits` returns no results, inform the user:
> "No brand kits found. Create a brand kit at brandkitos.com to use the publish pipeline."

## Rules

1. Always run QA before publishing — never publish on a failing critical check
2. Override flags (`--draft`/`--publish`/`--schedule`) win over `${user_config.publish_mode}` for that single run
3. Always include the Brand Application Notes and the resolved `mode` in the report so the user understands what they got and why
4. On Leafpad publish failure, surface the error and the draft body — do not retry blindly
5. Never publish without explicit success from `leafpad-publisher`
