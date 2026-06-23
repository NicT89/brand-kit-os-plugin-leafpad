# Brand Kit OS + Leafpad — Gemini Operating Guide

Gemini CLI reads this file as context. It mirrors the canonical [`AGENTS.md`](AGENTS.md) — keep
the two in sync. Connection setup: [`docs/install/gemini.md`](docs/install/gemini.md).

## Tools
- **Brand Kit OS (read):** `list_brand_kits`, `get_brand_kit_summary`, `get_brand_kit_core`,
  `get_brand_kit_personality`, `get_brand_kit_expression`, `get_brand_kit_governance`,
  `get_brand_kit_audience`, `get_brand_kit_products`, `get_brand_kit_personas`,
  `list_knowledge_files`, `get_knowledge_file`.
- **Leafpad:** `leafpad_list_organizations`, `leafpad_list_posts`, `leafpad_get_post`,
  `leafpad_list_tags`, `leafpad_create_post`, `leafpad_update_post`,
  `leafpad_add_scheduled_posts`, `leafpad_generate_image`, `leafpad_get_company_data`.

## Brand voice enforcement (always)
Load `get_brand_kit_summary` first (ask which kit if several). Before any external-facing output,
enforce: tone · voice archetype · preferred terminology · negative directory · behavioral
constraints · compliance · disclosure. **Never override governance** — flag conflicts and offer
an on-brand alternative.

## Publish pipeline
Resolve brand kit → research 3–5 credible sources (cite, never fabricate) → load full brand
context → `leafpad_list_posts` + `leafpad_list_tags` → draft (title **8–12 words**, body **≥ 800
words**) → SEO (`seo_title` ≤60, `seo_description` 140–160 raw, `seo_keywords` + `tags` as comma
strings) → `leafpad_generate_image` and embed the CDN URL as `<img>` in the body → **hard QA
gate** (≥800 words, 8–12-word title, image embedded, sources cited, 2–4 internal links; stop if
it fails twice) → publish.

Publish modes: `draft` → `leafpad_create_post(published:false)`; `published` →
`published:true`; `scheduled` → `leafpad_add_scheduled_posts(posts:[{title, date (ISO-8601 UTC),
prompt}])` (Leafpad generates a draft on that date — no finished body sent).

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
