# Trusted Sources Repository

This directory contains a curated library of authoritative content sources bundled with the Brand Kit OS + Leafpad plugin. It is a read-only reference: Claude reads it during setup to seed a user's local sources registry.

## Two separate concepts with the same name

**`references/trusted-sources/` (this folder)**
A global curated repository bundled with the plugin. Maintained by the plugin authors. Contains high-quality sources organized by category (AI/Tech, Marketing/Brand, SaaS/Startups, AI Agents/MCP, Reddit Communities). Read by `/setup` to seed new installs.

**`trusted_sources` key in `~/.brand-kit-os-leafpad/brands/<slug>/sources.json`**
Per-brand RSS feed list on the user's local machine. User-owned. Written by `/setup` (seeded from this folder) and extended by `/discover-sources`. Never overwritten without the user's confirmation.

These are different things. The global list is a starting point. The per-brand list is what topic-scout actually uses.

## When this file is used

During `/setup` Step 8, Claude reads `default-sources.json` and offers the user a menu of categories. The user selects relevant categories, and matching sources are merged into their `brands/<slug>/sources.json`. This gives new users a populated sources registry before they have run any discovery.

## How to update this list

Open a PR against `main` and add or update entries in `default-sources.json`. Each source entry must include:
- `name`: human-readable publication name
- `url`: canonical website URL
- `rss`: validated RSS or Atom feed URL (must return at least one entry when parsed)
- `type`: always `"rss"` for entries in this list

Verify all RSS URLs before committing. Run:

```bash
python3 -c "import feedparser; d = feedparser.parse('<rss_url>'); print(len(d.entries), 'entries')"
```

A valid feed returns at least 1 entry.

## Local copy

During setup, the plugin also copies relevant sources to `~/.brand-kit-os-leafpad/trusted_sources/` as a local snapshot. This local copy is informational only and is not read by topic-scout. Topic-scout reads from `brands/<slug>/sources.json`.
