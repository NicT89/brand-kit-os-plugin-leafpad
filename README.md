# Brand Kit OS + Leafpad Plugin for Claude

Connect your brand context and Leafpad blog publishing to Claude via Model Context Protocol (MCP).

## What's included

- **2 MCP servers** — Brand Kit OS (brand context) + Leafpad (blog publishing)
- **3 skills** — Brand Context, Voice Enforcement, and Topic Sourcing
- **10 agents** — content generation, brand review, audience adaptation, QA, SEO optimizer, Leafpad publisher, Cowork digest publisher, plus **topic-scout**, **citation-validator**, and **leafpad-ai-scheduler**
- **8 commands** — see the cheat sheet below
- **Session hook** — auto-loads your brand summary at session start

## Command cheat sheet

| Command | What it does |
|---|---|
| `/brand-kit-os-leafpad:doctor` | Health check + setup punch list |
| `/brand-kit-os-leafpad:publish-pipeline <topic> [--draft\|--publish\|--schedule <iso>]` | Research → draft → cite → SEO → QA → publish |
| `/brand-kit-os-leafpad:ai-schedule "<title>" <iso>` | Schedule a Leafpad-AI-generated future post |
| `/brand-kit-os-leafpad:plan-week [--count N]` | Research + build a content calendar |
| `/brand-kit-os-leafpad:execute-calendar [--ai-schedule\|--draft-now]` | Schedule/draft a planned calendar |
| `/brand-kit-os-leafpad:sync-brand-to-kb` | Push brand context into Leafpad's Knowledge Base |
| `/brand-kit-os-leafpad:create-content <type> for <audience> about <topic>` | Generate any content type |
| `/brand-kit-os-leafpad:enforce-voice <content>` | Apply brand voice to a request or text |

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
3. When prompted, paste your Brand Kit OS API key and pick a default `publish_mode` (`draft`, `published`, or `scheduled`).
4. Restart Claude. Ask "What brands do I have?" to verify.

## Publishing

`/brand-kit-os-leafpad:publish-pipeline <topic | brief | pasted source>` runs the full pipeline: load the **full breadth** of brand context (core, personality, expression, governance, audience, products, personas, knowledge files) → draft → SEO + media metadata + internal linking → QA → publish to Leafpad.

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
| `seo_title` / `seo_description` / `seo_keywords` (comma string) | `seo-optimizer` using `get_brand_kit_expression.preferred_terminology` |
| `tags` (comma string of names) | `leafpad_list_tags` + draft body; existing names reused, new ones auto-created |
| `published` | resolved from `publish_mode` or override flags (**defaults to `true`** — drafts send `published: false`) |

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
| [Claude](docs/install/claude.md) (Code + Desktop/Cowork) | ✅ native | Bearer | OAuth (native) | the plugin |
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

The quality of research depends on a **sources registry** (RSS feeds, citation domains, keyword themes, cadence) — set it up by asking *"Help me set up my content sources registry"* or see the **topic-sourcing** skill. To run this automatically every week/month, see [`docs/routines/`](docs/routines/).

## Citations & authority

The `citation-validator` agent adds 2–4 **verified** outbound citations — each one WebFetched and confirmed to actually support its claim — using your trusted-source domains and citation style. This strengthens search and AI-ranking authority without fabricated links.

## Brand-aware Leafpad AI — Knowledge Base sync

```
/brand-kit-os-leafpad:sync-brand-to-kb --dry-run
```

Pushes your Brand Kit OS context (voice, governance, audience, products) into your Leafpad org's Knowledge Base via Leafpad's REST API. Once synced, **every** Leafpad-AI-generated post — including AI-scheduled ones — is brand-aware, not just the ones the plugin hand-crafts.

## AI scheduling — Leafpad-generated future posts

`/brand-kit-os-leafpad:ai-schedule "<title>" <ISO-8601 UTC>` schedules a brand-aware future post via Leafpad's AI. **Leafpad generates the post at the scheduled time**, not us — the plugin prepares a brand-aware brief (title + secondary prompt encoding voice/governance/audience) and hands it off to `leafpad_add_scheduled_posts`.

Example:

```
/brand-kit-os-leafpad:ai-schedule "Building a brand-first content engine" 2026-07-01T09:30:00Z
```

> **Hand-crafted vs AI-scheduled.** `/publish-pipeline --schedule <iso>` and `/ai-schedule` both queue a topic for Leafpad to **generate** on the date (Leafpad has no `publish_at` to flip a finished draft live later). Use `/publish-pipeline` for immediate `--draft`/`--publish` runs that we write end-to-end, and `/ai-schedule` (or `--schedule`) when you want Leafpad's own AI to write the future post from a brand-aware brief. See [`LEAFPAD_REQUESTS.md`](LEAFPAD_REQUESTS.md) for gaps we've raised with Leafpad.

## Leafpad blog publishing

The `cowork-digest-publisher` agent turns Cowork news digests into brand-aligned blog posts on Leafpad. It:

1. Selects the most brand-relevant topic from the digest
2. Loads brand voice, governance, and audience from Brand Kit OS
3. Gathers existing Leafpad posts for internal linking and tag reuse
4. Writes, validates (meta desc, word count, tags, links), and publishes as draft

To use it: paste a Cowork digest and ask Claude to publish it.

## Available MCP tools

### Brand Kit OS (the read tools the pipeline uses)

The live Brand Kit OS MCP server exposes ~48 tools (including write/update tools for every brand section). The publish pipeline uses these read tools:

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
| `leafpad_create_post` | Create a blog post (draft or published). Body is `html_content` (HTML); `tags`/`seo_keywords` are comma strings; `published` defaults to `true` |
| `leafpad_update_post` | Update an existing post (no `tags` param — tags are immutable; SEO fields are co-required) |
| `leafpad_list_posts` | List existing posts for internal linking |
| `leafpad_get_post` | Read a specific post's content |
| `leafpad_list_tags` | Get existing tags for reuse |
| `leafpad_list_organizations` | List available organizations |
| `leafpad_get_company_data` | Query company knowledge base |
| `leafpad_add_scheduled_posts` | Schedule posts for future generation |
| `leafpad_generate_image` | Generate a feature/inline image (images are a separate step, not a post field) |

## Known Leafpad MCP limitations

- `leafpad_update_post` cannot modify tags after creation (no `tags` parameter) — recreate the post to change tags
- When updating SEO, send the full trio (`seo_title` + `seo_description` + `seo_keywords`); sending one alone is rejected
- `leafpad_create_post` body is HTML (`html_content`) — there is no markdown `content` field
- No delete endpoint — mistakes require Leafpad UI cleanup

> Note: the older "tags return `[]`" behavior did not reproduce on the calibrated instance (2026-06-13) — `leafpad_list_tags` returned the full tag list and tag reuse worked. Verify per instance.

## License

MIT
