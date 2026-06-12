# Brand Kit OS + Leafpad Plugin for Claude

Connect your brand context and Leafpad blog publishing to Claude via Model Context Protocol (MCP).

## What's included

- **2 MCP servers** — Brand Kit OS (brand context) + Leafpad (blog publishing)
- **2 skills** — Brand Context loading + Voice Enforcement
- **8 agents** — Content generation, brand review, audience adaptation, QA, SEO optimizer, Leafpad publisher, Leafpad AI scheduler, and Cowork digest-to-Leafpad publisher
- **4 commands** — `/brand-kit-os-leafpad:enforce-voice`, `/brand-kit-os-leafpad:create-content`, `/brand-kit-os-leafpad:publish-pipeline`, and `/brand-kit-os-leafpad:ai-schedule`
- **Session hook** — auto-loads your brand summary at session start

## Prerequisites

1. A Brand Kit OS account with a **Base or Premium** plan
2. An API key from [Settings → API Keys](https://brandkitos.com/settings)
3. Claude Desktop with Cowork mode, or Claude Code — both connect via the native HTTP MCP transport
4. A browser for first-time Leafpad sign-in — Leafpad MCP uses OAuth on first connect; the token is cached by the host afterward

## Install

### From marketplace

1. In Claude, run:
   ```
   /plugin marketplace add https://github.com/NicT89/brand-kit-os-plugin-leafpad
   ```
2. Install the plugin:
   ```
   /plugin install brand-kit-os-leafpad@brand-kit-os-leafpad
   ```
3. When prompted, paste your Brand Kit OS API key and pick a default `publish_mode` (`draft` or `published`).
4. Restart Claude. Ask "What brands do I have?" to verify.

### Manual install

Download the `plugins/brand-kit-os-leafpad` folder and upload it via Cowork → Customize → Browse plugins → Upload plugin.

## Publishing — hand-crafted brand-aligned drafts

`/brand-kit-os-leafpad:publish-pipeline <topic | brief | pasted source>` runs the full pipeline: load the **full breadth** of brand context (core, personality, expression, governance, audience, products, personas, knowledge files) → research the topic against your Leafpad Knowledge Base → draft → SEO + media metadata + internal linking → QA → publish to Leafpad.

It honors the `publish_mode` you chose at install (default `draft`). Override per-run with a flag:

- `--draft` — force draft
- `--publish` — go live immediately

Example:

```
/brand-kit-os-leafpad:publish-pipeline 3 ways retention beats acquisition for B2B SaaS --publish
```

## AI scheduling — Leafpad-generated future posts

`/brand-kit-os-leafpad:ai-schedule "<title>" <ISO-8601 datetime>` schedules a brand-aware future post via Leafpad's AI. **Leafpad generates the post at the scheduled time**, not us — the plugin prepares a brand-aware brief (title + secondary prompt encoding voice/governance/audience) and hands it off to `leafpad_add_scheduled_posts`.

Example:

```
/brand-kit-os-leafpad:ai-schedule "Building a brand-first content engine" 2026-07-01T09:30:00Z
```

> **Why two commands?** Leafpad's API has no `publish_at` field, so a hand-crafted draft cannot be scheduled to flip live at a target time. `publish-pipeline` does the heavy work (research, draft, SEO, QA, publish) but only supports immediate publish or draft. `ai-schedule` uses Leafpad's own AI scheduling but offloads the writing to Leafpad — quality depends on Leafpad's Writing Style + Knowledge Base. See [`LEAFPAD_REQUESTS.md`](LEAFPAD_REQUESTS.md) for the gap requests we've raised with Leafpad.

## Brand Kit OS → Leafpad field mapping

The pipeline builds a rich-article object covering every Leafpad field we can populate. The canonical mapping (and how to update it for your Leafpad instance) lives at [`plugins/brand-kit-os-leafpad/agents/references/brand-to-leafpad-mapping.md`](plugins/brand-kit-os-leafpad/agents/references/brand-to-leafpad-mapping.md). Highlights:

| Leafpad field | Sourced from |
|---|---|
| `name`, `slug`, `content` (HTML) | drafted by `content-generation` from brand core + personality + expression |
| `seo.title` / `seo.description` / `seo.keywords` | `seo-optimizer` using `get_brand_kit_expression.preferred_terminology` |
| `excerpt` | `seo-optimizer` — distinct from SEO desc, used for blog index + social feeds |
| `feature_image` URL | `seo-optimizer` calls `leafpad_generate_image` to produce a brand-aligned image and get a CDN URL |
| `tags` | `leafpad_list_tags` + draft body |
| `categories` | `get_brand_kit_expression.content_categories` |
| `author_name` | `get_brand_kit_personas` (when an AI persona is the byline) |
| `published` | resolved from `publish_mode` or override flags |

Because Leafpad MCP schemas vary by instance, `leafpad-publisher` sends the full payload and automatically strips any unsupported field, reporting back in the `schema_fit` block which fields landed and which were stripped. After your first publish, check `schema_fit.stripped` and update the mapping reference accordingly.

## Cowork digest publishing

The `cowork-digest-publisher` agent turns Cowork news digests into brand-aligned blog posts on Leafpad. It:

1. Selects the most brand-relevant topic from the digest
2. Loads brand voice, governance, and audience from Brand Kit OS
3. Gathers existing Leafpad posts for internal linking and tag reuse
4. Writes, validates, and publishes via `leafpad-publisher`

To use it: paste a Cowork digest and ask Claude to publish it.

## Available MCP tools

### Brand Kit OS (12 tools)

| Tool | Description |
|------|-------------|
| `list_brand_kits` | List all brand kits you own or have access to |
| `get_brand_kit_summary` | Compact brand overview (~500 tokens) |
| `get_brand_kit` | Complete brand kit with all sections |
| `get_brand_kit_core` | Mission, vision, brand story, promises |
| `get_brand_kit_personality` | Traits, values, principles, moods |
| `get_brand_kit_expression` | Tone, verbal style, voice archetypes, visual style |
| `get_brand_kit_products` | Products, services, features, differentiators |
| `get_brand_kit_audience` | Target audience personas |
| `get_brand_kit_governance` | Constraints, compliance, disclosure policy |
| `get_brand_kit_personas` | AI persona configurations |
| `list_knowledge_files` | Knowledge files attached to a brand kit |
| `get_knowledge_file` | Specific knowledge file metadata |

### Leafpad (9 tools)

| Tool | Description |
|------|-------------|
| `leafpad_list_organizations` | List orgs you belong to |
| `leafpad_list_posts` | Paginated post list with metadata for internal linking |
| `leafpad_get_post` | Full post by slug; supports `markdown`, `html`, or `json` content formats |
| `leafpad_create_post` | Create a post (draft or live) with HTML content, title, slug, SEO fields, tags |
| `leafpad_update_post` | Edit **any** field on an existing post — title, slug, content, tags, SEO, published status |
| `leafpad_add_scheduled_posts` | Schedule one or more AI-generated future posts (Leafpad writes them at the scheduled time from a title + ISO date + optional secondary prompt) |
| `leafpad_generate_image` | Generate a brand-aligned featured image via AI; returns a CDN URL |
| `leafpad_list_tags` | List/search all tags in an org for reuse |
| `leafpad_get_company_data` | Q&A against the org's Knowledge Base content |

## Leafpad behaviors worth knowing

These are platform features Leafpad provides automatically. Documented here so you understand what the publish pipeline relies on:

- **Auto-extracted FAQPage schema** — When 2+ H2/H3 headings end in `?`, Leafpad auto-emits FAQPage JSON-LD. `content-generation` is aware of this and structures headings accordingly when the topic suits FAQs.
- **Markdown delivery for AI consumers** — Any blog URL accessed with `.md` appended returns the post in Markdown. Combined with auto-generated `llms.txt`, your published content is natively AI-readable (AIO — AI-inclusive optimization).
- **Server-computed structured data** — Leafpad's public API derives `wordCount`, `articleSection`, `inLanguage`, and `isAccessibleForFree` on publish. The plugin does not send these.
- **Webhooks** — Leafpad fires webhooks on blog create/update with org id + slug + path. Useful for downstream automation in Supabase/Zapier (not currently wired into this plugin; happy path for future versions).

## Known Leafpad MCP gaps (filing with Leafpad)

These are tracked in [`LEAFPAD_REQUESTS.md`](LEAFPAD_REQUESTS.md). Plugin workarounds noted where applicable.

- No `publish_at` on `leafpad_update_post` — hand-crafted drafts can't be scheduled to flip live; use `/ai-schedule` for AI-generated future posts or publish manually at the target time
- No `leafpad_delete_post` — mistakes require Leafpad UI cleanup
- No `leafpad_create_tag` — tags supplied to `leafpad_create_post` may be auto-created or may need pre-existence (under verification)
- No Knowledge Base push via MCP — `/sync-brand-to-kb` (v1.6) will use the REST endpoint to push BKOS data into Leafpad KB
- No Writing Style read/write via MCP — relies on Leafpad dashboard configuration
- No analytics tool — on Leafpad's roadmap

> Earlier versions of this README claimed `leafpad_update_post` cannot modify tags and `leafpad_list_tags` returns `[]`. Per Leafpad's MCP docs, `leafpad_update_post` supports updating every field including tags — corrected in v1.5.0. The list-tags-empty behavior is still under verification on real installs; check `schema_fit` in your first publish.

## License

MIT
