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
- `--schedule <ISO-8601 UTC>` — queue Leafpad to **generate** the post on that date (different path — see workflow step 10)

If no override is given, the run uses `${user_config.publish_mode}` (default `draft`).

## Workflow

1. **Resolve brand kit** — Call `get_brand_kit_summary` for the active brand. If multiple kits exist, call `list_brand_kits` and ask which to use.
2. **Parse arguments** — Extract topic / brief / source from `$ARGUMENTS` and detect any override flag. If the input is too thin to draft from (e.g. just a single word), ask one short follow-up before proceeding.
3. **Research the topic (step 1 of drafting)** — Gather credible external grounding before writing:
   - Use the available web research tool — prefer Firecrawl `firecrawl_search` if present, otherwise the built-in web search. Pull 3–5 recent, credible sources; capture each source's title, URL, and a one-line takeaway. These become **citable external links**.
   - Optionally call `leafpad_get_company_data` for the org's own indexed site content to ground claims in existing material.
   - If no web research tool is available, continue without it and note "no external research run" in the report — do not fabricate sources or links.
4. **Load full brand context in parallel** — pull the breadth of brand data per `references/brand-to-leafpad-mapping.md`:
   - `get_brand_kit_core` — mission/promise framing for the intro
   - `get_brand_kit_personality` — tone calibration
   - `get_brand_kit_expression` — voice, terminology, visual style, content_categories
   - `get_brand_kit_governance` — constraints, negative directory, disclosure policy
   - `get_brand_kit_audience` — persona targeting
   - `get_brand_kit_products` — CTAs, product callouts
   - `get_brand_kit_personas` — for author byline if the brand uses a named AI persona
   - `list_knowledge_files` — if the brand has style guides or playbooks; fetch any relevant ones via `get_knowledge_file`
5. **Gather Leafpad context in parallel** — `leafpad_list_posts` (internal-link candidates) and `leafpad_list_tags` (tag reuse).
6. **Delegate drafting** — Call the `content-generation` agent with the `blog post` template, passing the full brand context, the research findings, parsed brief, and any loaded knowledge files. Expect a rich-article object back with a **title of 8–12 words**, a **body of 800+ words (target 900+)**, internal links, and **external citation links** from the research.
7. **Delegate SEO** — Call the `seo-optimizer` agent. Apply its patch onto the rich-article object: `seo` (title/description/keywords), `tags`, `internal_links`, and the brand-styled **feature-image prompt**. Insert internal links into the body where suggested; do not otherwise modify the body.
8. **Generate the on-brand image** — Call `leafpad_generate_image(organization_slug, prompt)` with `seo-optimizer`'s image prompt (it uses the org's brand palette automatically). Embed the returned CDN URL as an `<img>` near the top of the body. There is no featured-image post field, so the image lives in the body. If generation fails, note it and continue (QA will flag the missing image).
9. **Delegate QA (final audit gate)** — Call the `quality-assurance` agent against `skills/brand-voice-enforcement/references/enforcement-checklist.md`, **including the measured blog SEO & structure gate**: body ≥ 800 words, title 8–12 words, image embedded, external sources cited, 2–4 internal links. If any Critical check fails, revise once and re-run QA. If it fails twice, stop and surface the QA report — **do not publish**.
10. **Publish via `leafpad-publisher`** — Resolve `mode` (override flag wins, else `${user_config.publish_mode}`, default `draft`):
    - `draft` / `published` → pass the full rich-article object; publisher maps it to `leafpad_create_post` (`html_content`, comma-string tags/seo, `published` flag).
    - `scheduled` → **different path**: pass `{ title, date (ISO-8601 UTC from --schedule), prompt }` where `prompt` is a brand-voice brief built from the loaded context. Publisher calls `leafpad_add_scheduled_posts`; Leafpad generates the post on that date. No finished body is sent in this mode.
11. **Report** — Output the URL / draft id / scheduled date, the mode, the Brand Application Notes, the measured QA numbers (word count, title length), and the `schema_fit` block.

## Output format

```
Publish Pipeline Result
  Mode: draft | published | scheduled (override flag used: yes/no)
  URL / Draft ID: ...
  Scheduled For: <iso>            # only when mode=scheduled

Audit (hard gates):
- Word count: N (min 800, target 900+) — Pass/Fail
- Title length: N words (must be 8–12) — Pass/Fail
- Image embedded: yes/no — Pass/Fail
- External sources cited: N
- Internal links inserted: N

Brand Application Notes:
- Voice: [archetypes and attributes applied]
- Tone: [dimension settings and reasoning]
- Terminology: [notable choices from preferred_terminology]
- Governance: [constraints observed, disclosures included]
- Audience: [persona targeted]
- Products referenced: [...]
- Knowledge files applied: [...]   # if any were loaded

Article metadata:
- SEO title / description / keywords
- Tags: [...]
- Feature image: [CDN URL from leafpad_generate_image, embedded in body]
- Research sources: [titles + URLs gathered in step 3]

schema_fit (from leafpad-publisher):
  accepted: [Leafpad fields that were saved]
  stripped: [fields rejected — should be empty with the calibrated mapping]
  auto_generated: [fields Leafpad set itself, e.g. author]
```

If anything lands in `schema_fit.stripped`, your Leafpad schema changed — update `references/brand-to-leafpad-mapping.md`.

## When no brand kit is found

If `list_brand_kits` returns no results, inform the user:
> "No brand kits found. Create a brand kit at brandkitos.com to use the publish pipeline."

## Rules

1. Always run QA before publishing — never publish on a failing critical check
2. **The audit gate is hard.** Never publish a blog post under 800 words, with a title outside 8–12 words, or with no embedded image. Revise once; if still failing, surface the report and stop.
3. Override flags (`--draft`/`--publish`/`--schedule`) win over `${user_config.publish_mode}` for that single run
4. **`scheduled` mode does not send a finished body** — it queues a topic + date + brand prompt for Leafpad to generate. The word-count/image gates apply to drafted posts (`draft`/`published`); for scheduled, encode the rules into the generation prompt instead.
5. Never invent external sources or links — only cite URLs returned by the research step
6. Always include the Brand Application Notes, the measured audit numbers, and the resolved `mode` in the report
7. On Leafpad publish failure, surface the error and the draft body — do not retry blindly
8. Never publish without explicit success from `leafpad-publisher`
