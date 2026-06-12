---
description: End-to-end brand-aligned publish pipeline — draft, validate, and publish an article to Leafpad in one command.
argument-hint: <topic | brief | pasted source> [--draft|--publish]
---

# Publish Pipeline

Take a topic, brief, or pasted source (digest, notes, transcript) and run the full publish flow: load brand context → research → draft → SEO + media + internal linking → QA → publish to Leafpad. Honors `${user_config.publish_mode}` unless the run overrides it with a flag.

For **AI-scheduled** future posts (Leafpad generates the content at a target date), use the separate `/brand-kit-os-leafpad:ai-schedule` command — Leafpad has no publish-at-date for hand-crafted drafts.

## Arguments

`$ARGUMENTS` should be one of:

- A **topic** — e.g. `short post about retention loops for SaaS founders`
- A **brief** — a few sentences describing angle, audience, and key messages
- **Pasted source material** — a Cowork digest, meeting notes, a transcript, a research clipping

Optional override flags:

- `--draft` — publish as a draft regardless of `publish_mode`
- `--publish` — publish immediately regardless of `publish_mode`

If no override is given, the run uses `${user_config.publish_mode}` (default `draft`).

## Workflow

1. **Resolve brand kit** — Call `get_brand_kit_summary` for the active brand. If multiple kits exist, call `list_brand_kits` and ask which to use.
2. **Parse arguments / find a topic** — Extract topic / brief / source from `$ARGUMENTS` and detect any override flag.
   - If a topic/brief/source is given, use it.
   - **If no topic is given** ("write me something on-brand"), delegate to the `topic-scout` agent (`count: 3`), present the top ideas, and let the user pick one — or auto-pick the highest-fit idea if they asked you to "just publish something."
   - If input is too thin, ask one short follow-up.
3. **Load full brand context in parallel** — pull the breadth of brand data per `agents/references/brand-to-leafpad-mapping.md`:
   - `get_brand_kit_core` — mission/promise framing for the intro
   - `get_brand_kit_personality` — tone calibration
   - `get_brand_kit_expression` — voice, terminology, visual style, content_categories
   - `get_brand_kit_governance` — constraints, negative directory, disclosure policy
   - `get_brand_kit_audience` — persona targeting
   - `get_brand_kit_products` — CTAs, product callouts
   - `get_brand_kit_personas` — for author byline if the brand uses a named AI persona
   - `list_knowledge_files` — if the brand has style guides or playbooks; fetch any relevant ones via `get_knowledge_file`
4. **Research the topic against Leafpad's Knowledge Base** — Call `leafpad_get_company_data` with a question like *"What do we know about [topic]? Include any product specifics, case studies, or company positioning relevant to this article."* This pulls real org-specific facts to weave into the article. If the KB is empty or no relevant content exists, proceed without it.
5. **Gather Leafpad context in parallel** — `leafpad_list_posts` (internal-link candidates) and `leafpad_list_tags` (tag reuse). Note: `leafpad_list_tags` may return `[]` per known limitation; `seo-optimizer` handles it.
6. **Delegate drafting** — Call the `content-generation` agent with the `blog post` template, passing the full brand context, parsed brief, KB research findings, and any loaded knowledge files. Expect a rich-article object back with `body` in **HTML** (Leafpad's `content` field expects HTML).
7. **Delegate citations** — Call the `citation-validator` agent with the draft. It adds 2–4 verified outbound citations (each WebFetch-checked) for factual claims, using the trusted-sources registry and brand citation style. Apply its insertion patch to the body.
8. **Delegate SEO + media metadata** — Call the `seo-optimizer` agent. Apply its full patch: `seo`, `excerpt`, `feature_image` (real CDN URL via `leafpad_generate_image`), `og_image`, `tags`, `categories`, `internal_links`, `canonical_url`. Insert internal links into the body where suggested.
9. **Delegate QA** — Call the `quality-assurance` agent against the enforcement checklist at `skills/brand-voice-enforcement/references/enforcement-checklist.md`. If a critical check fails, revise once and re-run QA. If it fails twice, stop and surface the QA report to the user — do not publish.
10. **Publish via `leafpad-publisher`** — Resolve `mode`:
    - Override flag (if present) wins
    - Otherwise use `${user_config.publish_mode}` (defaulting to `draft`)

    Pass `{ article (full rich-article object with HTML body), mode }` to `leafpad-publisher`. The publisher attempts all candidate fields and strip-on-rejects any unsupported by the user's Leafpad instance.
11. **Report** — Output the published URL (or draft id), the mode used, the Brand Application Notes, the citations added, and the `schema_fit` block from `leafpad-publisher`.

## Output format

```
Publish Pipeline Result
  Mode: draft | published (override flag used: yes/no)
  URL / Draft ID: ...

Brand Application Notes:
- Voice: [archetypes and attributes applied]
- Tone: [dimension settings and reasoning]
- Terminology: [notable choices from preferred_terminology]
- Governance: [constraints observed, disclosures included]
- Audience: [persona targeted]
- Products referenced: [...]
- Knowledge files applied: [...]   # if any were loaded
- Leafpad KB facts used: [...]      # from leafpad_get_company_data
- Citations added: N               # verified outbound links from citation-validator

Article metadata:
- SEO title / description / keywords
- Excerpt
- Feature image: <CDN URL from leafpad_generate_image, OR "auto-generated by Leafpad" when omitted>
- Tags: [...]
- Categories: [...]
- Internal links inserted: N

Auto-generated by Leafpad on publish (no need to send):
- wordCount
- articleSection
- inLanguage
- FAQPage schema (auto-extracted when 2+ H2/H3 headings end in "?")

schema_fit (from leafpad-publisher):
  accepted: [list of Leafpad fields that were saved]
  stripped: [list of candidate fields the user's Leafpad instance rejected]
  auto_generated: [list of fields Leafpad overrode]

Caveats (if any):
- "Tags couldn't be verified — leafpad_list_tags returned []"
```

After your first successful publish, review the `schema_fit.stripped` list. Any field there is one your Leafpad instance doesn't support — update `agents/references/brand-to-leafpad-mapping.md` to move it from "candidate" to "unsupported" so we stop retrying it next time.

## When no brand kit is found

If `list_brand_kits` returns no results, inform the user:
> "No brand kits found. Create a brand kit at brandkitos.com to use the publish pipeline."

## Rules

1. Always run QA before publishing — never publish on a failing critical check
2. Override flags (`--draft`/`--publish`) win over `${user_config.publish_mode}` for that single run
3. Always include Brand Application Notes and the resolved `mode` in the report
4. On Leafpad publish failure, surface the error and the draft body — do not retry blindly
5. Never publish without explicit success from `leafpad-publisher`
6. Body content sent to Leafpad must be **HTML**, not Markdown — `content-generation` produces HTML; if you receive Markdown, convert it before passing to `leafpad-publisher`
