# Changelog

## 1.6.1 — 2026-06-12

Patch release fixing plugin.json validation per the official Claude Code plugin manifest spec.

- **userConfig entries** now include the required `type` and `title` fields per the spec. Added `required: true` to `brand_kit_api_key`. Removed the unsupported `enum` keyword from `publish_mode` (allowed values moved into the `description`).
- **Dropped `capabilities`** — not a recognized top-level field; Claude Code warns on it. Component discovery happens via the default directories (`agents/`, `commands/`, `skills/`, `hooks.json`, `.mcp.json`).
- **`.mcp.json`** reverted to the documented stdio + `mcp-remote` proxy shape (the example shape in the plugin reference). Direct HTTP `url + headers` works in Claude Desktop's own MCP config, but plugin `.mcp.json` is validated against the documented stdio form.
- **`displayName`** + structured `author` object + `keywords` added for better presentation in the `/plugin` picker.

No behavioral changes to agents, commands, or workflows.

## 1.6.0 — 2026-06-12

Research-driven content planning, citations, scheduling routines, Knowledge Base sync, a health-check command, and a full documentation suite — plus portability beyond Claude Code.

### Research & planning

- **`topic-scout` agent** — researches and proposes ranked, brand-relevant blog topics from five sources: user themes, company updates (Leafpad KB), trusted RSS/news feeds (sources registry), content-gap analysis of existing Leafpad posts, and trending web search. Each idea gets a 0–100 brand-fit score and provenance label.
- **`/plan-week [--count N] [--start] [--themes]`** — builds an editorial calendar via `topic-scout`, assigns publish slots from your cadence, and saves a calendar file.
- **`/execute-calendar [--ai-schedule | --draft-now]`** — schedules a planned calendar via Leafpad's AI scheduler, or hand-crafts every post as a draft through the full pipeline.
- **`topic-sourcing` skill + sources registry** — a user-editable `~/.brand-kit-os-leafpad/registry.json` (RSS feeds, citation domains, keyword clusters, cadence) with JSON Schema and an annotated example. The richer the registry, the better the research.

### Citations & authority

- **`citation-validator` agent** — adds 2–4 verified outbound citations to each article. Every source is WebFetched and confirmed to support its claim before insertion; drops unverifiable candidates transparently. Wired into `/publish-pipeline` and `cowork-digest-publisher`.

### Knowledge Base sync

- **`/sync-brand-to-kb [--sections] [--dry-run]`** — pushes Brand Kit OS context into your Leafpad org's Knowledge Base via Leafpad's REST API, so every Leafpad-AI-generated post is brand-aware. `--dry-run` previews the documents before upload.

### Health & onboarding

- **`/doctor`** — read-only health check: verifies both MCP connections, lists brand kits + Leafpad orgs, checks brand-kit completeness and Leafpad readiness, validates the sources registry, and prints a punch list with concrete next steps.
- **`docs/getting-started.md`** — end-to-end onboarding from install to first post to recurring calendar, with a command cheat sheet and troubleshooting.

### Routines & portability

- **`docs/routines/`** — `weekly-3-articles.md` and `monthly-editorial-calendar.md` show how to wire `/plan-week` + `/execute-calendar` into Cowork scheduled sessions or Claude Code cron for hands-off content.
- **`docs/integrations/`** — guides for Claude Desktop, VS Code, Cursor, and any generic MCP client / custom code, making the workflow portable across apps and LLMs.
- **`schemas/rich-article.schema.json`** — the vendor-neutral intermediate object, codified as JSON Schema for interoperability.

### Pipeline changes

- `/publish-pipeline` now (a) calls `topic-scout` when no topic is given, and (b) runs `citation-validator` between drafting and SEO.
- `cowork-digest-publisher` now adds citations back to original sources and outputs HTML.

## 1.5.0 — 2026-06-11

Major correctness pass integrating direct intel from Leafpad MCP's actual capabilities.

### Corrections (current code was wrong)

- **`content` field is HTML, not Markdown** — `content-generation` now outputs HTML; the rich-article schema body field is HTML; `leafpad-publisher` enforces this. Leafpad's `content` field expects HTML.
- **`leafpad_update_post` supports updating every field including tags** — removed the "tag updates blocked" rule from `leafpad-publisher` and the corresponding "known limitation" note in README. Post-publish corrections are now first-class.
- **`leafpad_add_scheduled_posts` AI-generates a brand-new post; it does NOT delay-publish a hand-crafted draft.** Removed the `--schedule <iso>` flag from `/publish-pipeline` (it would have malfunctioned). Replaced with a new dedicated `/ai-schedule` command for the actual AI-scheduled flow.
- **9 Leafpad MCP tools, not 8** — `leafpad_generate_image` was missing from the inventory.
- **Dropped `scheduled` from `publish_mode` userConfig enum** — only `draft` and `published` are coherent defaults. AI scheduling is per-run via the new command.

### New

- **`/brand-kit-os-leafpad:ai-schedule "<title>" <iso>`** — schedules a future AI-generated post via `leafpad_add_scheduled_posts`. Builds a brand-aware secondary prompt from BKOS expression + governance + audience + products.
- **`leafpad-ai-scheduler` agent** — backs the new command. Loads brand context, refines the title, composes the secondary prompt, dispatches the call.
- **`seo-optimizer` now calls `leafpad_generate_image`** — produces a real CDN-hosted feature image URL aligned with `get_brand_kit_expression.visual_style`. Falls back to prompt-only on tool failure.
- **`content-generation` now researches the topic against Leafpad's Knowledge Base** — calls `leafpad_get_company_data` to pull real org-specific facts before drafting, grounding article claims.
- **`leafpad_get_post` with `content_format: "markdown"`** added to seo-optimizer's internal-link analysis path.
- **`LEAFPAD_REQUESTS.md`** at the repo root — captures the 7 Leafpad MCP gaps (publish_at, KB push, Writing Style sync, delete, create_tag, analytics, post-type support) with shape proposals and plugin-side workarounds.
- **README expanded** to document Leafpad's auto-extracted FAQ schema, markdown delivery for AIO, server-computed structured data fields, and webhook behavior — so users understand what the publish pipeline relies on and what Leafpad provides "for free".

### Removed

- `--schedule <iso>` flag from `/publish-pipeline` (no clean home in Leafpad's API; replaced with `/ai-schedule`)
- `scheduled` value from `publish_mode` userConfig enum
- "Tag updates blocked" / "leafpad_update_post cannot modify tags" claims from README and `leafpad-publisher` rules (was incorrect)
- `reading_time` computation from `seo-optimizer` (Leafpad derives word count and related fields itself)
- `wordCount`/`articleSection`/`inLanguage`/FAQ computation from the rich-article schema (Leafpad auto-derives on publish)

## 1.4.2 — 2026-06-11

- **Endpoint change**: Brand Kit OS MCP server moved to `https://www.brandkitos.com/mcp` (was `https://fupwpcqmyykfiuakjxxc.supabase.co/functions/v1/mcp-server`).
- **Transport change**: both MCP servers now use direct HTTP transport (`url` + `headers`) instead of the `mcp-remote` stdio proxy. This is faster, drops the Node-subprocess dependency, and matches the format Claude Desktop and VS Code natively expect. Leafpad's OAuth handshake is now handled by the host's MCP runtime rather than `mcp-remote`.
- Docs: test protocol and README updated to the new transport shape.

## 1.4.1 — 2026-06-11

- **Fix**: `.mcp.json` referenced `@anthropic-ai/mcp-remote` which does not exist on npm; corrected to `mcp-remote` (v0.1.38+). Without this fix the plugin's MCP servers cannot launch on install.
- **Docs**: `README.md` Prerequisites now lists Node 18+ and notes that Leafpad uses OAuth on first connect.
- **Docs**: new test protocol at `docs/testing/claude-desktop-test-protocol.md` for end-to-end validation in Claude Desktop Chat.

## 1.4.0 — 2026-06-11

- Full-depth **Brand Kit OS → Leafpad field mapping** — `/publish-pipeline` now pulls every relevant brand section (`core`, `personality`, `expression`, `governance`, `audience`, `products`, `personas`, knowledge files) and maps it into a rich-article object covering all candidate Leafpad fields (excerpt, feature_image, og_image, author, categories, visibility, content_format, reading_time, canonical_url, and more)
- New canonical reference at `agents/references/brand-to-leafpad-mapping.md` documenting every Brand Kit source → Leafpad field
- `leafpad-publisher` adds **strip-on-reject schema adaptation** — sends the rich payload, automatically removes any field the user's Leafpad instance rejects, and reports `schema_fit: { accepted, stripped, auto_generated }` so the user can refine the mapping for their instance
- `seo-optimizer` upgraded to emit excerpt, feature/og image briefs (prompt + alt + caption), categories from brand kit `content_categories`, computed reading time, and optional canonical URL — all distinct from the SEO meta block
- `content-generation` blog template now returns a rich-article object and consumes the full breadth of brand sections (mission, personality, products, knowledge files) for higher-quality long-form output

## 1.3.0 — 2026-06-11

- New command `/brand-kit-os-leafpad:publish-pipeline` — end-to-end orchestrator that drafts, optimizes for SEO, runs QA, and publishes to Leafpad in one call
- New agent `seo-optimizer` — builds the `seo` block, suggests internal links from existing Leafpad posts, and proposes tags (without rewriting the body)
- New agent `leafpad-publisher` — generic publisher that encapsulates field mapping, mode dispatch, and failure handling
- New `publish_mode` userConfig (`draft` | `published` | `scheduled`, default `draft`) — controls default publishing behavior
- Per-run override flags `--draft`, `--publish`, and `--schedule <iso>` on `/publish-pipeline`
- Refactor: `cowork-digest-publisher` now delegates its publish step to `leafpad-publisher` (no behavior change for digest users)

## 1.2.0 — 2026-04-18

Initial public marketplace release.

- 2 MCP servers: Brand Kit OS and Leafpad (both via `mcp-remote`)
- 2 skills: `brand-context`, `brand-voice-enforcement`
- 5 agents: `content-generation`, `brand-review`, `audience-adaptation`, `quality-assurance`, `cowork-digest-publisher`
- 2 commands: `/brand-kit-os-leafpad:enforce-voice`, `/brand-kit-os-leafpad:create-content`
- SessionStart agent hook that auto-loads brand summary when exactly one brand kit exists
- Brand Kit OS API key prompted at install via `userConfig` and injected into `.mcp.json` via `${user_config.brand_kit_api_key}`
