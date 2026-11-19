# Brand Kit OS + Leafpad Plugin for Claude

Connect your brand context and Leafpad blog publishing to Claude via Model Context Protocol (MCP).

## What's included

- **2 MCP servers** — Brand Kit OS (brand context) + Leafpad (blog publishing)
- **3 skills** — Brand Context, Voice Enforcement, and Topic Sourcing
- **10 agents** — content generation, brand review, audience adaptation, QA, SEO optimizer, Leafpad publisher, Cowork digest publisher, plus **topic-scout**, **citation-validator**, and **leafpad-ai-scheduler**
- **12 commands**: see the cheat sheet below
- **Session hook**: tells Claude to start with `get_agent_briefing`, load `get_brand_context_for_agent` before writing, and run `check_draft` on every draft

## Command cheat sheet

| Command | What it does |
|---|---|
| `/brand-kit-os-leafpad:setup` | Guided first-run setup: connect both MCP servers, set publish mode, verify |
| `/brand-kit-os-leafpad:doctor` | Health check + setup punch list |
| `/brand-kit-os-leafpad:publish-pipeline <topic> [--draft\|--publish\|--schedule <iso>]` | Research → draft → cite → SEO → QA → publish |
| `/brand-kit-os-leafpad:ai-schedule "<keyword>" <iso>` | Schedule one Leafpad-AI-generated future post ($1 when it runs) |
| `/brand-kit-os-leafpad:weekly-schedule [--dry-run]` | Sunday run: research two topics and schedule them for Tuesday and Thursday with full briefs |
| `/brand-kit-os-leafpad:post-qa` | Tue/Thu run: check the generated post (brand, links, CTA, SEO), fix what is safe, publish if still a draft |
| `/brand-kit-os-leafpad:blog-analytics [--summary]` | Per-post Search Console and GA4 with topic and rewrite recommendations |
| `/brand-kit-os-leafpad:plan-week [--count N]` | Research + build a content calendar |
| `/brand-kit-os-leafpad:execute-calendar [--ai-schedule\|--draft-now]` | Schedule/draft a planned calendar |
| `/brand-kit-os-leafpad:sync-brand-to-kb` | Push brand context into Leafpad's Knowledge Base |
| `/brand-kit-os-leafpad:create-content <type> for <audience> about <topic>` | Generate any content type |
| `/brand-kit-os-leafpad:enforce-voice <content>` | Apply brand voice to a request or text |

## Prerequisites

1. A Brand Kit OS account (the free plan works; no API key is needed)
2. Claude Desktop with Cowork mode, or Claude Code: both connect via the native HTTP MCP transport
3. A browser for first-time sign-in to Brand Kit OS and Leafpad. Both use OAuth on first connect; Leafpad MCP uses OAuth on first connect; the token is cached by the host afterward

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
3. When prompted, pick a default `publish_mode` (`draft`, `published`, or `scheduled`). The first time Claude uses Brand Kit OS or Leafpad it asks you to sign in to each.
4. Restart Claude. Ask "What brands do I have?" to verify.

## Publishing

`/brand-kit-os-leafpad:publish-pipeline <topic | brief | pasted source>` runs the full pipeline: load brand context (`get_brand_context_for_agent` plus `get_brand_kit` sections for core, personality, products and SEO, and relevant knowledge files), draft, SEO + media metadata + internal linking, `check_draft` and QA, then publish to Leafpad.

It honors the `publish_mode` you chose at install (default `draft`). Override per-run with a flag:

- `--draft` — force draft
- `--publish` — go live immediately
- `--schedule <ISO-8601>` — schedule for a future timestamp

Example:

```
/brand-kit-os-leafpad:publish-pipeline 3 ways retention beats acquisition for B2B SaaS --publish
```

### Brand Kit OS → Leafpad field mapping

The pipeline builds a rich-article object, then projects it onto the fields `leafpad_create_post` actually accepts (calibrated against the live Leafpad MCP — full detail at [`plugins/brand-kit-os-leafpad/references/brand-to-leafpad-mapping.md`](plugins/brand-kit-os-leafpad/references/brand-to-leafpad-mapping.md)). The verified Leafpad fields:

| Leafpad field | Sourced from |
|---|---|
| `name`, `slug` | drafted by `content-generation` from brand core + personality + expression |
| `html_content` (HTML, not markdown) | drafted body, rendered to HTML, with internal links inserted |
| `seo_title` / `seo_description` / `seo_keywords` (comma string) | `seo-optimizer` using the kit's `preferred_terminology` and `seo` keywords |
| `tags` (comma string of names) | `leafpad_list_tags` + draft body; existing names reused, new ones auto-created |
| `published` | resolved from `publish_mode` or override flags (**defaults to `false`**; drafts still send `published: false` explicitly) |

The body's `author` is auto-set by Leafpad from your account. Feature images are produced via the separate **`leafpad_generate_image`** tool, not a post field. Fields the rich object carries for other channels — `excerpt`, `categories`, `reading_time`, `canonical_url` — are **not** Leafpad post fields and are dropped on publish. `leafpad-publisher` still reports a `schema_fit` block so you can spot any future schema change.

### Manual install

Download the `plugins/brand-kit-os-leafpad` folder and upload it via Cowork → Customize → Browse plugins → Upload plugin.

## Platform compatibility

The full **plugin** (skills/agents/commands/hooks) runs only on **Claude**. But the two MCP
servers connect to any MCP-capable host, and the brand-voice intelligence is ported to each
platform's native instructions format. Per-platform guides live in
[`docs/install/`](docs/install/README.md).

| Platform | Plugin? | Brand Kit OS | Leafpad | Intelligence ported as |
|---|---|---|---|---|
| [Claude](docs/install/claude.md) (Code + Desktop/Cowork) | ✅ native | OAuth (native, no key) | OAuth (native) | the plugin |
| [Cursor](docs/install/cursor.md) | MCP + rules | `headers` | OAuth (native) | `.cursor/rules/*.mdc` |
| [OpenAI Codex CLI](docs/install/codex.md) | MCP + AGENTS.md | `bearer_token` | OAuth via `mcp-remote` | `AGENTS.md` |
| [ChatGPT](docs/install/chatgpt.md) (Developer Mode) | connectors | API-key | OAuth | custom GPT / Project instructions |
| [Gemini CLI](docs/install/gemini.md) | MCP + GEMINI.md | `headers` | OAuth | `GEMINI.md` |
| [Manus](docs/install/manus.md) | MCP integration | URL + key | OAuth/key | agent instructions |
| [Perplexity](docs/install/perplexity.md) (Pro/Max/Ent) | connectors | API-key | OAuth | Space instructions |

Two caveats apply everywhere: **Brand Kit OS enforces a host allowlist** (a `403` with a valid
key means the platform needs allowlisting, not a new key), and **Codex** needs an `mcp-remote`
bridge for Leafpad because it doesn't yet support MCP OAuth.

The canonical agent instructions are [`AGENTS.md`](AGENTS.md); the per-platform mirrors
(`GEMINI.md`, the Cursor rule, [`docs/portable/custom-instructions.md`](docs/portable/custom-instructions.md))
are derived from it. The setup interview an agent runs is
[`docs/setup/setup-spec.json`](docs/setup/setup-spec.json) — on Claude, run
`/brand-kit-os-leafpad:setup`.

## Research & planning — topics, calendars, routines

The plugin can research what to write about, not just how. The `topic-scout` agent draws on your trusted sources, company updates, content gaps, and trends to propose ranked, on-brand topic ideas.

```
/brand-kit-os-leafpad:plan-week --count 3      # research + build a weekly calendar
/brand-kit-os-leafpad:execute-calendar         # schedule it on Leafpad
```

The quality of research depends on a **sources registry** (RSS feeds, citation domains, keyword themes, cadence) — set it up by asking *"Help me set up my content sources registry"* or see the **topic-sourcing** skill. To run the two-posts-a-week pipeline automatically, see [`docs/routines/weekly-leafpad-scheduler.md`](docs/routines/weekly-leafpad-scheduler.md); for a monthly calendar, [`docs/routines/monthly-editorial-calendar.md`](docs/routines/monthly-editorial-calendar.md).

## Citations & authority

The `citation-validator` agent adds 2–4 **verified** outbound citations — each one WebFetched and confirmed to actually support its claim — using your trusted-source domains and citation style. This strengthens search and AI-ranking authority without fabricated links.

## Brand-aware Leafpad AI — Knowledge Base sync

```
/brand-kit-os-leafpad:sync-brand-to-kb --dry-run
```

Pushes your Brand Kit OS context (voice, governance, audience, products) into your Leafpad org's Knowledge Base via Leafpad's REST API. Once synced, **every** Leafpad-AI-generated post — including AI-scheduled ones — is brand-aware, not just the ones the plugin hand-crafts.

## AI scheduling: Leafpad-generated future posts

`/brand-kit-os-leafpad:ai-schedule "<keyword>" <ISO-8601 UTC>` schedules a brand-aware future post via Leafpad's AI. **Leafpad generates the post at the scheduled time**, not us. The plugin prepares a full brief from the kit ([`references/scheduled-brief-template.md`](plugins/brand-kit-os-leafpad/references/scheduled-brief-template.md)) and calls `leafpad_add_scheduled_posts` with `organization_slug` and `posts: [{ title, date, prompt, volume, kd, intent, post_type, parent_id, parent_scheduled_post_id }]`.

Example:

```
/brand-kit-os-leafpad:ai-schedule "brand voice for AI agents" 2026-11-24T15:00:00Z
```

What to expect (verified 2026-11-18/19):

- **$1 per scheduled post**, charged when it runs. `leafpad_create_post` posts are free.
- **Auto-publish:** the `brand-kit-os` account publishes at generation (row 1702 became live post 2198 three minutes after its slot). There is no draft option on scheduling yet; see [`LEAFPAD_REQUESTS.md`](LEAFPAD_REQUESTS.md).
- **Leafpad decides** the final title (treat `title` as the target keyword), slug, tags, SEO fields, images and internal links. `/post-qa` checks the result.
- **The queue is editable:** `leafpad_list_scheduled_posts`, `leafpad_update_scheduled_post` and `leafpad_delete_scheduled_posts` (deleting a pending row is never charged).

> **Hand-crafted vs AI-scheduled.** `/publish-pipeline --schedule <iso>` and `/ai-schedule` both queue a topic for Leafpad to **generate** on the date (Leafpad has no `publish_at` to flip a finished draft live later). Use `/publish-pipeline` for immediate `--draft`/`--publish` runs that we write end-to-end.

## Scheduled pipeline: two posts a week

Leafpad's AI writes the posts; Claude finds the topics and supplies the brand context.

| When | Command | What it does |
|---|---|---|
| Sunday | `/brand-kit-os-leafpad:weekly-schedule` | Reads the Brand AI Weekly Digest (Slack `#weekly-digest`), the kit, Leafpad company data, Search Console gaps and fresh research; dedupes against live posts and the calendar; schedules Tuesday and Thursday 09:00 America/Chicago with every field filled (updating a pending row rather than adding one); adds a weekly analytics section |
| Tue and Thu, about 09:30 Chicago | `/brand-kit-os-leafpad:post-qa` | Finds the generated post, runs `check_draft` and `check_draft_seo`, checks every link (`https://www.brandkitos.com/blogs/<slug>`) and the CTA, fixes HTML and the SEO trio with `leafpad_update_post`, publishes if still a draft, reports |
| Weekly (summary) or monthly | `/brand-kit-os-leafpad:blog-analytics` | Per-post Search Console (Leafpad, and Supermetrics `sc-domain:brandkitos.com`) and GA4 with 7 and 28-day trends; recommends new topics and rewrites |

Per-brand settings live in [`references/pipeline-brands.json`](plugins/brand-kit-os-leafpad/references/pipeline-brands.json) (AutoLogs is stubbed and disabled until it is configured). Cloud Routines do not load plugins, so [`docs/routines/weekly-leafpad-scheduler.md`](docs/routines/weekly-leafpad-scheduler.md) carries self-contained Routine prompts that use MCP tools only.

## Leafpad blog publishing

The `cowork-digest-publisher` agent turns Cowork news digests into brand-aligned blog posts on Leafpad. It:

1. Selects the most brand-relevant topic from the digest
2. Loads brand voice, governance, and audience from Brand Kit OS
3. Gathers existing Leafpad posts for internal linking and tag reuse
4. Writes, validates (meta desc, word count, tags, links), and publishes as draft

To use it: paste a Cowork digest and ask Claude to publish it.

## Available MCP tools

### Brand Kit OS (MCP 3.0 read tools the plugin uses)

| Tool | Description |
|------|-------------|
| `get_agent_briefing` | Session bootstrap: lists your kits, or one kit's health, next step and account write settings |
| `list_brand_kits` | List all brand kits you own or have access to |
| `get_brand_kit` | Any part of a kit: the summary with no `sections`, or `sections: [...]` (`core`, `personality`, `expression`, `platform_expressions` + `platform`, `governance`, `visuals`, `seo`, `products`, `partners`, `audience`, `ai_personas`, `competitors`, `customers`, `company_icps`, `knowledge_files`, `expression_examples`, `anti_slop_rules`, `objections`, ...) |
| `get_brand_context_for_agent` | One-call bundle for a task; `task_type: "content_generation"` + `platform` returns voice, governance, examples, audience and the knowledge index |
| `get_knowledge_file` | One knowledge file's full content |
| `check_draft` | Checks a draft against the kit's anti-slop rules, banned terms and writing constraints. The plugin runs it before any draft is shown or sent |

MCP 3.0 removed `get_brand_kit_summary`, the `get_brand_kit_<section>` getters, `list_knowledge_files` and `get_platform_expression`; see [`data-model.md`](plugins/brand-kit-os-leafpad/skills/brand-context/references/data-model.md) for the mapping.

### Leafpad

| Tool | Description |
|------|-------------|
| `leafpad_create_post` | Create a blog post. Body is `html_content` (HTML); `tags`/`seo_keywords` are comma strings; `published` defaults to `false` |
| `leafpad_update_post` | Update a post (no `tags` param; `html_content` replaces the whole body; SEO fields are co-required) |
| `publish_post` | Publish a draft the user has agreed to publish |
| `leafpad_list_posts` | List existing posts (internal links, dedupe) |
| `leafpad_get_post` | Read a post (`content_format: "html"` before any body edit) |
| `leafpad_list_tags` | Get existing tags for reuse |
| `leafpad_list_organizations` | List available organizations |
| `leafpad_get_company_data` | Query the org's indexed company content |
| `leafpad_add_scheduled_posts` | Schedule AI-generated posts ($1 each when they run) |
| `leafpad_list_scheduled_posts` | List the content calendar (pending, and completed with `include_completed`) |
| `leafpad_update_scheduled_post` / `leafpad_delete_scheduled_posts` | Change or remove a pending row |
| `leafpad_schedule_rewrites` | Schedule an AI rewrite of an existing post (published in place) |
| `leafpad_get_search_console_data` | Search Console clicks, impressions, CTR, position |
| `check_draft_seo` | Score a post with Leafpad's on-page SEO checks |
| `find_pages_needing_attention` | Pages losing search traffic and pending refresh proposals |
| `leafpad_generate_image` | Generate an image on Leafpad's CDN (embedded in the body; no featured-image field on create/update) |

## Known Leafpad MCP limitations

- `leafpad_update_post` cannot modify tags after creation (no `tags` parameter) — recreate the post to change tags
- When updating SEO, send the full trio (`seo_title` + `seo_description` + `seo_keywords`); sending one alone is rejected
- `leafpad_create_post` body is HTML (`html_content`) — there is no markdown `content` field
- No post delete endpoint: mistakes require Leafpad UI cleanup (pending scheduled rows can be removed with `leafpad_delete_scheduled_posts`)
- `leafpad_add_scheduled_posts` has no draft option: on an auto-publishing account the generated post is live at generation

> Note: the older "tags return `[]`" behavior did not reproduce on the calibrated instance (2026-06-13) — `leafpad_list_tags` returned the full tag list and tag reuse worked. Verify per instance.

## License

MIT
