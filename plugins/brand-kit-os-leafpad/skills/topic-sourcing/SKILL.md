---
description: Manage the sources registry that powers topic research and citations — trusted RSS/news feeds, authoritative citation domains, SEO keyword clusters, and company news. Activates when the user sets up content planning, asks where article ideas come from, or wants to add/edit content sources.
---

# Topic Sourcing — Skill

## Purpose

Tell Claude where to find article ideas and citations for a brand. The `topic-scout` and `citation-validator` agents read a **sources registry** — a user-editable JSON file — to know which feeds, sites, and keyword themes to draw from.

This makes topic research repeatable and on-brand instead of generic. The richer the registry, the better the ideas.

## The sources registry

**Location (in priority order):**
1. Per-brand-kit: `~/.brand-kit-os-leafpad/registry.<brand_kit_id>.json`
2. Global default: `~/.brand-kit-os-leafpad/registry.json`

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

## How to set it up

When a user wants to start content planning, help them create the registry:

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
