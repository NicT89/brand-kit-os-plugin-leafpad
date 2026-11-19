# Brand Kit OS + Leafpad — Gemini Operating Guide

Gemini CLI reads this file as context. It mirrors the canonical [`AGENTS.md`](AGENTS.md) — keep
the two in sync. Connection setup: [`docs/install/gemini.md`](docs/install/gemini.md).

## Tools
- **Brand Kit OS (read, MCP 3.0):** `get_agent_briefing`, `list_brand_kits`, `get_brand_kit`
  (summary with no `sections`; `sections: [...]` such as `core`, `personality`, `expression`,
  `platform_expressions` + `platform`, `governance`, `products`, `audience`, `seo`,
  `knowledge_files`), `get_brand_context_for_agent`, `get_knowledge_file`, `check_draft`.
  (3.0 removed the `get_brand_kit_<section>` getters, `list_knowledge_files` and
  `get_platform_expression`.)
- **Leafpad:** `leafpad_list_organizations`, `leafpad_list_posts`, `leafpad_get_post`,
  `leafpad_list_tags`, `leafpad_create_post`, `leafpad_update_post`, `publish_post`,
  `leafpad_add_scheduled_posts`, `leafpad_list_scheduled_posts`,
  `leafpad_update_scheduled_post`, `leafpad_delete_scheduled_posts`, `leafpad_generate_image`,
  `leafpad_get_company_data`, `leafpad_get_search_console_data`, `check_draft_seo`.

## Brand voice enforcement (always)
Call `get_agent_briefing` first (ask which kit if several; never guess a kit id). Before
writing, call `get_brand_context_for_agent` (`task_type: "content_generation"`, `platform`).
Enforce tone, voice archetype, preferred terminology, negative directory, behavioral
constraints, compliance and disclosure. Run `check_draft` on every draft before it is shown or
sent; fix every hard violation and re-check. **Never override governance**: flag conflicts and offer
an on-brand alternative.

## Publish pipeline
Resolve brand kit → research 3–5 credible sources (cite, never fabricate) → load full brand
context → `leafpad_list_posts` + `leafpad_list_tags` → draft (title **8–12 words**, body **≥ 800
words**) → SEO (`seo_title` ≤60, `seo_description` 140–160 raw, `seo_keywords` + `tags` as comma
strings) → `leafpad_generate_image` and embed the CDN URL as `<img>` in the body → **hard QA
gate** (`check_draft` passes, ≥800 words, 8–12-word title, image embedded, sources cited, 2–4 internal links; stop if
it fails twice) → publish.

Publish modes: `draft` → `leafpad_create_post(published:false)`; `published` →
`published:true` (`published` defaults to `false`; `publish_post` publishes a draft later);
`scheduled` → check `leafpad_list_scheduled_posts` and update a pending row for the slot with
`leafpad_update_scheduled_post`; otherwise `leafpad_add_scheduled_posts(organization_slug,
posts:[{title (target keyword), date (ISO-8601 UTC), prompt (full brief), volume, kd, intent,
post_type, parent_id, parent_scheduled_post_id}])`. Leafpad generates the post on that date,
charges $1, and on the `brand-kit-os` account publishes it at generation. Brief template:
`plugins/brand-kit-os-leafpad/references/scheduled-brief-template.md`.

## Leafpad field limits
`leafpad_create_post` accepts only `organization_slug, name, slug, html_content` (**HTML**),
`post_type, published, seo_title, seo_description, seo_keywords` (comma), `tags` (comma). Do not
send `excerpt/feature_image/canonical_url/categories/author/visibility` — rejected. `author` is
set from the OAuth identity. No delete endpoint; tags immutable after create. Full mapping:
[`plugins/brand-kit-os-leafpad/references/brand-to-leafpad-mapping.md`](plugins/brand-kit-os-leafpad/references/brand-to-leafpad-mapping.md).

## First-run setup
If the user is connecting for the first time, run the interview in
[`docs/setup/setup-spec.json`](docs/setup/setup-spec.json): detect platform → ask for Brand Kit
OS API key (secret) → ask default publish mode (`draft`) → write `~/.gemini/settings.json` per
the install guide → verify via `list_brand_kits` + `leafpad_list_organizations`.
