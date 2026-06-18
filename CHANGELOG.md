# Changelog

## 1.4.5 — 2026-06-16

- **Hard SEO/structure audit gate (blog posts).** `quality-assurance` now runs a measured, blocking pre-publish audit: body **≥ 800 words (target 900+)**, **title 8–12 words**, an embedded image, external sources cited, and 2–4 internal links. Body under 800 or a title outside 8–12 words is a Critical fail that blocks publish. Codified in the enforcement checklist; `content-generation` writes to these targets.
- **On-brand images.** The pipeline now generates a feature image via `leafpad_generate_image` (which applies the org's brand palette) from `seo-optimizer`'s image prompt and embeds it in the body. (Note: `leafpad_create_post` has no featured-image field, so the image lives in the body.)
- **Web research step.** `/publish-pipeline` step 1 now gathers 3–5 credible external sources (Firecrawl `firecrawl_search` when available, else built-in web search) and cites them as external links. Never fabricates sources.
- **Scheduled mode corrected.** `leafpad-publisher`, the mapping reference, and `/publish-pipeline` now use the real `leafpad_add_scheduled_posts` shape — `posts: [{ title, date (ISO-8601 UTC), prompt }]` for Leafpad to **generate** on the date — instead of a finished article + nonexistent `scheduled_at`. Verified format: `2026-06-23T14:00:00Z`.

## 1.4.4 — 2026-06-14

- **Fix (blocking marketplace install): invalid `author`.** `plugin.json` had `author` as a string; the plugin schema requires an object. `claude plugin validate` failed on it, so a marketplace install loaded no components/data. Changed to `{ "name", "url" }`. Both plugin and marketplace manifests now pass `claude plugin validate --strict`.
- **Fix: reference doc parsed as an agent.** Moved `agents/references/brand-to-leafpad-mapping.md` to `references/brand-to-leafpad-mapping.md` (plugin root) so it is no longer scanned as a frontmatter-less agent. Updated the relative links in `content-generation`, `seo-optimizer`, and `leafpad-publisher` to `../references/…`.
- **CI: plugin checks.** Added `.github/workflows/plugin-checks.yml` — runs `claude plugin validate --strict` on the marketplace and plugin, and (on PRs) fails if any plugin file changed without a version bump. Enable it as a required check in branch protection to enforce the bump rule.

## 1.4.3 — 2026-06-13

- **Fix (blocking): plugin manifest location.** Moved `plugin.json` to `.claude-plugin/plugin.json`. Claude Desktop's "Upload plugin" rejected the previous root-level manifest with `Invalid plugin: missing .claude-plugin/plugin.json`. This is the spec-required location for both direct upload and marketplace install.
- **Fix: hooks auto-discovery.** Moved `hooks.json` to `hooks/hooks.json` (the convention Claude Code auto-discovers). At the old root path the SessionStart brand-summary hook never fired.
- **Leafpad schema calibration (verified against the live MCP, 2026-06-13).** Rewrote `agents/references/brand-to-leafpad-mapping.md` and `agents/leafpad-publisher.md` to the **actual** `leafpad_create_post` schema:
  - Real accepted fields: `organization_slug`, `name`, `slug`, `html_content` (HTML, not markdown), `post_type`, `published`, `seo_title`, `seo_description`, `seo_keywords` (comma string), `tags` (comma string).
  - `published` defaults to `true` — drafts must send `published: false`.
  - Removed unsupported "candidate" fields (`excerpt`, `feature_image`, `og_image`, `categories`, `author_name`, `canonical_url`, `visibility`, `content_format`, `reading_time`, nested `seo{}`). Feature images are a separate `leafpad_generate_image` call; `author` is auto-set from the OAuth identity.
  - `leafpad_update_post`: SEO fields are co-required (send the full `seo_title`/`seo_description`/`seo_keywords` trio); tags are immutable after creation.
  - Verified live: tag reuse works (the older "tags return `[]`" caveat did not reproduce); SEO description must be raw text (not HTML-escaped).
- **Manifest hardening (spec audit).** Added the spec-required `type` + `title` to each `userConfig` option (`brand_kit_api_key`, `publish_mode`); removed the undocumented/inert `capabilities` field and the unsupported `enum` key on `publish_mode` (valid values now documented in its description). Confirmed `${user_config.brand_kit_api_key}` substitution in `.mcp.json` headers is valid per the plugin spec (no change needed).
- **Docs reconciled to the verified schema.** Updated `README.md` (field-mapping table, tool lists incl. `leafpad_generate_image`, known-limitations), `agents/seo-optimizer.md` (which fields actually reach Leafpad), and the test protocol header so they no longer reference unsupported Leafpad fields.

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
