# Local File Structure

The brand-kit-os-leafpad plugin writes to a local directory at `~/.brand-kit-os-leafpad/`.
This directory is created automatically by the `/setup` command on first run.

## Directory layout

```
~/.brand-kit-os-leafpad/
  config.json                    # Global defaults: active kit, publish mode, plugin version
  brands/
    <brand-kit-slug>/            # One folder per brand (slug = lowercase hyphenated name)
      sources.json               # RSS feeds, citation domains, keyword clusters, cadence
      history.json               # Dedup log: published and drafted topic URLs/titles
  cache/
    rss/                         # Cached RSS feed responses (reduces repeat fetches)
    web/                         # Cached web scrape responses
  logs/
    runs.json                    # Audit trail: what ran, when, what was published
```

## File details

### `config.json`
Created by `/setup`. Stores global defaults so you don't re-specify them per run.

```json
{
  "publish_mode": "draft",
  "active_brand_kit_id": "9d16945f-...",
  "active_leafpad_org": "brand-kit-os",
  "plugin_version": "1.7.0"
}
```

### `brands/<slug>/sources.json`
The per-brand sources registry. Validated against `skills/topic-sourcing/references/registry.schema.json`. Scaffolded by `/setup`, extended by `/topic-sourcing`.

Supported source types for `trusted_sources`:

- `rss` — Substack, newsletters, most blogs. Fetched with `feedparser` via bash. Pattern for Substack: `https://<publication>.substack.com/feed`
- `atom` — Some GitHub changelogs, developer blogs. Also fetched with `feedparser`.
- `html` — Sites without feeds. Scraped via WebFetch or Firecrawl.
- Reddit RSS: `https://www.reddit.com/r/<subreddit>.rss`

### `brands/<slug>/history.json`
Dedup log used by `topic-scout` to avoid re-proposing recently published or drafted topics.

```json
{
  "published": [
    { "title": "...", "slug": "...", "published_at": "2026-07-09" }
  ],
  "drafted": [
    { "title": "...", "created_at": "2026-07-08" }
  ]
}
```

### `cache/rss/<feed-hash>.json`
Cached RSS feed responses with a TTL of 4 hours. Reduces feedparser calls when the same feed is referenced across multiple topic-scout runs in a day.

### `logs/runs.json`
Append-only audit trail. One entry per `/publish-pipeline` or `/plan-week` run:

```json
[
  {
    "run_at": "2026-07-09T14:30:00Z",
    "command": "publish-pipeline",
    "brand_kit_id": "9d16945f-...",
    "leafpad_org": "brand-kit-os",
    "topic": "Brand governance is the new SEO",
    "publish_mode": "draft",
    "post_id": 1193
  }
]
```

## Backward compatibility
The legacy flat registry (`~/.brand-kit-os-leafpad/registry.json` and `registry.<brand_kit_id>.json`) is still honored as a fallback. The new per-brand `brands/<slug>/sources.json` takes precedence when both exist.

## Version check
The `/doctor` command fetches the latest release from: `https://api.github.com/repos/NicT89/brand-kit-os-plugin-leafpad/releases/latest`
and compares it to the `plugin_version` in `config.json` (and the constant embedded in `commands/doctor.md`). If behind, it reports an update notice with instructions.

## Note on secrets
This directory contains only config and content data. API keys and OAuth tokens are managed by the Claude plugin system (`plugin.json` userConfig), never written here.
