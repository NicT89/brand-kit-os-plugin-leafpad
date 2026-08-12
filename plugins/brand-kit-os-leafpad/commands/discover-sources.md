---
name: discover-sources
description: Discover and add content sources for topic research. Scans Gmail for newsletters, accepts Substack/Reddit/website/competitor URLs, validates RSS feeds, and scrapes non-RSS sites via Firecrawl or Apify. Merges all findings additively into brands/<slug>/sources.json.
argument-hint: (no arguments — runs the discovery interview)
---

# Discover Sources

Scans connected accounts and user-provided URLs to build out the `trusted_sources` section of your sources registry. Can be run standalone at any time or called inline from `/setup`.

## Usage

```
/brand-kit-os-leafpad:discover-sources
```

## Workflow

### Step 1: Load context

Read `~/.brand-kit-os-leafpad/config.json` to get `active_brand_kit_slug`. Load the existing `brands/<slug>/sources.json` so new entries can be merged additively without duplicating anything already present.

Build a dedup set from existing `trusted_sources` entries by their `rss` URL field.

### Step 2: Gmail newsletter scan

Call Gmail MCP `search_threads` with:
- `query`: `(newsletter OR digest OR unsubscribe OR "view in browser") -from:me`
- `max_results`: 50

Parse each result to extract the sender email address. Group by domain. For each unique sender domain, map known newsletter platforms to RSS feed patterns:

| Domain pattern | RSS pattern |
|---|---|
| `*.substack.com` | `https://<subdomain>.substack.com/feed` |
| `*.beehiiv.com` | `https://<subdomain>.beehiiv.com/feed` |
| `*.ghost.io` | `https://<subdomain>.ghost.io/rss/` |
| `*.convertkit.com` / `*.ck.page` | No standard RSS: flag for Firecrawl |
| `*.mailchimp.com` | No standard RSS: skip (transactional only) |
| Other domains | Try `https://<domain>/feed`, `https://<domain>/rss`, `https://<domain>/feed.xml` in order |

Validate each candidate RSS URL using Python feedparser via bash:

```bash
python3 - <<'EOF'
import feedparser, sys, json

urls = <json_array_of_candidate_urls>

results = []
for url in urls:
    try:
        d = feedparser.parse(url)
        if d.entries:
            results.append({"url": url, "title": d.feed.get("title", ""), "valid": True})
        else:
            results.append({"url": url, "valid": False})
    except Exception as e:
        results.append({"url": url, "valid": False, "error": str(e)})

print(json.dumps(results))
EOF
```

Collect all valid feeds. Present a summary to the user:
"Found <N> newsletter RSS feeds from your Gmail. Here are the ones I can subscribe to for topic research: [list]. Any you'd like to exclude?"

Let the user confirm or deselect. Add confirmed feeds to a staging list.

### Step 3: Substack profile (optional)

Ask: "Do you have a Substack profile or list of Substack publications you follow? Paste your profile URL or a comma-separated list of Substack publication slugs (e.g. `lenny, swyx, annehelen`), or press enter to skip."

If the user provides slugs or a profile URL:
- For each slug, construct RSS: `https://<slug>.substack.com/feed`
- Validate via feedparser (same bash snippet as Step 2)
- Add valid feeds to the staging list

### Step 4: Reddit communities (optional)

Ask: "Any Reddit communities relevant to your brand? Enter subreddit names without r/ (e.g. `SaaS, marketing, branding`), or press enter to skip."

For each subreddit provided:
- RSS URL: `https://www.reddit.com/r/<subreddit>/.rss`
- Validate via feedparser
- Add valid feeds to the staging list

### Step 5: Your website and blog (optional)

Ask: "What is your website URL? I'll look for a blog RSS feed to track your own publishing history."

If provided:
- Try `<url>/feed`, `<url>/rss`, `<url>/blog/feed`, `<url>/feed.xml` via feedparser
- If no RSS found, use Firecrawl to scrape the blog index:
  - Call `firecrawl_scrape` with `url: <blog_url>` and `formats: ["markdown"]`
  - Extract post titles and URLs from the scraped content
  - Add as a `type: "html-scrape"` entry in `competitor_content_feeds` (not `trusted_sources`) with `scrape_interval: "weekly"`

### Step 6: Competitor websites (optional)

Ask: "Any competitor websites or industry blogs you want to monitor? Enter URLs separated by commas, or press enter to skip."

For each URL provided:
- Try to find an RSS feed via feedparser (same patterns as Step 2)
- If RSS found: add to `competitor_content_feeds` with `type: "rss"`
- If no RSS found: use Firecrawl `firecrawl_map` to find a `/blog` or `/news` path, then `firecrawl_scrape` to extract headlines
  - Add as `type: "html-scrape"` in `competitor_content_feeds`
- If Firecrawl is unavailable: try Apify `call-actor` with actor `apify/web-scraper` and `startUrls: [url]`

### Step 7: Merge and save

Take the dedup set from Step 1 and merge all staged feeds.

For each new `trusted_sources` entry, use this schema:

```json
{
  "name": "<feed title from feedparser or user-provided name>",
  "url": "<website URL>",
  "rss": "<validated RSS URL>",
  "type": "rss",
  "category": "<ai_tech | marketing_brand | saas_startups | reddit | personal | competitor>",
  "added_by": "discover-sources",
  "added_at": "<ISO 8601 date>"
}
```

For `competitor_content_feeds` entries (sites with no RSS):

```json
{
  "name": "<site name>",
  "url": "<URL>",
  "type": "html-scrape",
  "scrape_interval": "weekly",
  "added_by": "discover-sources",
  "added_at": "<ISO 8601 date>"
}
```

Write the merged result back to `brands/<slug>/sources.json`. Never overwrite existing entries; only append new ones. Deduplicate by `rss` field before saving.

### Step 8: Report

Output a summary:

```
Source discovery complete

Gmail newsletters:    <N> feeds added
Substack:             <N> feeds added
Reddit communities:   <N> feeds added
Your website:         <found | not found>
Competitor sites:     <N> monitored (RSS: <n>, scrape: <n>)

Total sources in registry: <total count>

Run /brand-kit-os-leafpad:plan-week to use these sources for topic research.
```

## Rules

1. Never overwrite existing `trusted_sources` entries. Merge additively only.
2. Only add feeds that pass feedparser validation (have at least one entry). Never add a feed URL that returns 0 entries or an error.
3. Never store API keys or auth tokens in `sources.json`. Sources must be publicly accessible RSS/Atom feeds or scrapeable URLs.
4. If Gmail MCP is not connected, skip Step 2 with a note: "Gmail not connected: skipping newsletter scan. You can connect Gmail in your MCP settings and re-run /discover-sources."
5. If Firecrawl MCP is not connected and Apify MCP is not connected, skip scraping steps with a note: "No web scraping tool connected. For sites without RSS feeds, connect Firecrawl or Apify in your MCP settings."
6. Always present found feeds to the user for confirmation before writing to disk. Never auto-add without showing the list.
7. No em dashes in any output. Use colons or semicolons instead.
