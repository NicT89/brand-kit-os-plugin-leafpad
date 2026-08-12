---
description: Manage the sources registry that powers topic research and citations — trusted RSS/news feeds, authoritative citation domains, SEO keyword clusters, and company news. Activates when the user sets up content planning, asks where article ideas come from, or wants to add/edit content sources.
---

# Topic Sourcing — Skill

## Purpose

Tell Claude where to find article ideas and citations for a brand. The `topic-scout` and `citation-validator` agents read a **sources registry** — a user-editable JSON file — to know which feeds, sites, and keyword themes to draw from.

This makes topic research repeatable and on-brand instead of generic. The richer the registry, the better the ideas.

## The sources registry

**Location (in priority order):**
1. Per-brand (recommended): `~/.brand-kit-os-leafpad/brands/<brand-kit-slug>/sources.json`
   — Created automatically by `/setup`. Use this for all new installs.
2. Per-brand-kit (legacy): `~/.brand-kit-os-leafpad/registry.<brand_kit_id>.json`
3. Global default (legacy): `~/.brand-kit-os-leafpad/registry.json`

All three locations are honored for backward compatibility. If the new per-brand file exists,
it takes precedence. The `/setup` command creates the new structure automatically on first run.

If neither exists, `topic-scout` falls back to Leafpad's Knowledge Base + web search, and notes that adding a registry improves results.

**Schema:** see `references/registry.schema.json`. An annotated example lives at `references/registry.example.json`.

### Fields

| Field | Type | Used by | What it does |
|---|---|---|---|
| `trusted_sources` | array of `{ name, url, type }` | topic-scout | RSS/Atom feeds or news sites to scan for industry topics. `type` is `rss`, `atom`, or `html`. |
| `authoritative_citations` | array of `{ domain, note }` | citation-validator | Pre-vetted domains to prefer when citing claims (e.g. official stats bodies, standards orgs, research outlets). |
| `seo_keyword_clusters` | array of `{ theme, keywords[] }` | topic-scout | Keyword groups per content theme — used to score SEO opportunity and suggest titles. |
| `internal_news_feed_url` | string (URL) | topic-scout | A company changelog/press/blog feed for "company update" topics. Optional — Leafpad KB can substitute. |
| `competitor_content_feeds` | array of `{ name, url }` | topic-scout | Competitor blogs to watch for differentiation angles (we write *better*, never copy). |
| `citation_style_guide` | object | citation-validator | Anchor-text style, `rel` rules, whether to append a Sources block, competitor-link policy. |
| `topic_cadence` | object | plan-week | Default posts-per-week and preferred publish days/times. |

## Adding sources with /discover-sources

Run `/brand-kit-os-leafpad:discover-sources` at any time to expand your sources registry:

- Gmail newsletter scan: finds newsletters you already subscribe to and extracts their RSS feeds
- Substack: add publications you follow by slug or profile URL
- Reddit: add subreddit RSS feeds by name
- Your website: monitors your own blog for publishing history
- Competitors: monitors competitor blogs via RSS or Firecrawl scrape

Discovery merges additively. It never removes or overwrites sources you have already added.

Run `/discover-sources` again whenever you want to add new sources. It skips anything already in the registry.

## How to set it up

The `/setup` command scaffolds this file automatically on first run, pre-populated with
keyword clusters from the brand kit. To add or update sources afterward, run
`/brand-kit-os-leafpad:topic-sourcing` or edit the file directly.

To set up manually (or add sources to an existing registry):

1. Ask for 3–8 industry sources they trust (publications, blogs, newsletters with RSS).
2. Ask for any authoritative sources they want cited (research orgs, official data).
3. Pull keyword themes from `get_brand_kit_expression.content_categories` as a starting point for `seo_keyword_clusters`.
4. Ask their preferred posting cadence (e.g., 3 posts/week, Mon/Wed/Fri at 9am).
5. Write the file to `~/.brand-kit-os-leafpad/registry.json` (or per-kit), validated against `references/registry.schema.json`.

The `/brand-kit-os-leafpad:doctor` command checks whether a valid registry exists and reports what's missing.

## Rules

1. The registry is **user-owned data** — never overwrite it without confirming; merge additively when adding sources.
2. Validate against `references/registry.schema.json` before writing.
3. Never put secrets/API keys in the registry — it's plain config. Auth lives in MCP config.
4. If a feed URL fails to fetch repeatedly, flag it to the user rather than silently dropping it.
5. Treat `competitor_content_feeds` as inspiration for *differentiation* — never as content to reproduce.
