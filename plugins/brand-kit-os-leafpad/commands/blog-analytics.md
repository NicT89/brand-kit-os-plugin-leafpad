---
description: Per-post blog performance from Search Console (Leafpad, plus Supermetrics when connected) and GA4, with a table per post and recommendations for new topics and rewrites.
argument-hint: '[--brand <key>] [--days 28] [--summary]'
---

# Blog Analytics

Feeds performance back into topic choice. `/brand-kit-os-leafpad:weekly-schedule` runs the
`--summary` form every Sunday; run the full form by hand or monthly.

## Arguments

- `--brand <key>`: the brand entry in `references/pipeline-brands.json` (default `brand-kit-os`).
- `--days <N>`: the main window (default 28). Trends always compare the last 7 days with the
  7 before, and the last 28 with the 28 before.
- `--summary`: top movers and three query gaps only (the Sunday form).

## Sources

| Source | When | Call |
|---|---|---|
| Leafpad Search Console | Always | `leafpad_get_search_console_data` |
| Supermetrics Search Console | When the Supermetrics connector is present | ds `GW`, account `sc-domain:brandkitos.com` |
| Supermetrics GA4 | When the Supermetrics connector is present | ds `GAWA`, property `503617238` ("Brand Kit") |
| Leafpad decay list | Always | `find_pages_needing_attention` |

Leafpad's Search Console connection uses the URL-prefix property `https://brandkitos.com/`,
which is near-empty because the site serves from `https://www.brandkitos.com`. Treat
Supermetrics `sc-domain:brandkitos.com` as the primary Search Console source when it is
available, and Leafpad's as the fallback. Say in the report which one each number came from.

## Workflow

### 1. Posts

`leafpad_list_posts` (`limit: 100`, paging): every live post with id, slug, title and
published date. The live URL is `site_base_url` + `blog_path` + slug
(`https://www.brandkitos.com/blogs/<slug>`).

### 2. Search Console via Leafpad

- Per page: `leafpad_get_search_console_data` with `dimensions: ["page"]`,
  `page_contains: "/blogs/"`, `days: 28`, `row_limit: 1000`, `response_format: "json"`.
- Top queries per page: same call with `dimensions: ["page", "query"]`.
- Trends: the `["page"]` call four more times with explicit `start_date` / `end_date` for the
  last 7 days, the prior 7, the last 28 and the prior 28. The latest two days are excluded
  because Google is still filling them in.
- Gaps: `dimensions: ["query"]`, `days: 28`, `row_limit: 1000`.

### 3. Search Console and GA4 via Supermetrics (when connected)

Follow the Supermetrics workflow: `data_source_discovery` with the ds id (confirms auth and
report types), `accounts_discovery` if needed, `data_query`, then `get_async_query_results`
until data arrives. Field ids below were confirmed with `field_discovery` on 2026-11-19;
re-run it if a query rejects one.

- **Search Console (`GW`)**, account `sc-domain:brandkitos.com`, report type `STANDARD`:
  metrics `clicks`, `impressions`, `ctr`, `position`; dimensions `page` (or `pagepath`),
  `query`, `Date`. Filter to pages whose path contains `/blogs/`. Run the same four windows
  as step 2. `ctr` and `position` are pre-aggregated: request each grouping directly; never
  sum or average them across rows.
- **GA4 (`GAWA`)**, property `503617238`: metrics `sessions`, `engagedSessions`,
  `engagementRate`, `conversions`, and `c_keyevents_ads_conversion_sign_up_1` (the sign-up key
  event on this property); dimension `landingPage` (and `Date` for trends). Filter to landing
  pages containing `/blogs/`.

If the connector is missing or a source needs sign-in, say so (with the login link the
discovery call returns) and continue with Leafpad data.

### 4. Decay

`find_pages_needing_attention` with `organization_slug` and `limit: 10`: pages losing search
traffic, and any refresh proposals waiting. Read-only; do not approve or reject anything.

### 5. Output

One row per post, sorted by 28-day clicks:

```
Blog analytics: <brand> · <start> to <end> · Search Console source: Supermetrics sc-domain | Leafpad URL-prefix

| Post (slug) | Clicks 28d | Impr. 28d | CTR | Pos. | Clicks 7d vs prior 7d | Clicks 28d vs prior 28d | Sessions 28d | Sign-ups 28d | Top queries (impr.) |
|-------------|-----------:|----------:|----:|-----:|----------------------:|------------------------:|-------------:|-------------:|---------------------|
| /blogs/...  |         42 |     3,100 | 1.4%| 11.2 | +8 (+40%)             | +15 (+56%)              |           61 |            2 | q1 (900), q2 (400)  |
```

Posts with no Search Console rows still get a row (zeros), so new posts are visible.

### 6. Recommendations

- **New topics**: queries with impressions in the last 28 days, average position worse than
  10, and no post whose title or slug targets them. List up to five with impressions and
  position. These feed `/weekly-schedule` step 4.
- **Rewrites**: posts with impressions but CTR under 1%, or position between 8 and 20, or on
  the decay list. For each, propose a `leafpad_schedule_rewrites` item:
  `{ post_id, date, target_keywords: [{ keyword, volume }], instructions, intent }`.
  Scheduling a rewrite publishes a new version of a live page and uses a refresh credit, so
  list the proposal and schedule it only after the user agrees.
- **Cuts or merges**: two posts ranking for the same query; suggest a redirect
  (`leafpad_set_redirect`) for a person to decide. Never set one from this command.

With `--summary`, output only: the top three posts by clicks, the three biggest 7-day movers
(up or down), and three new-topic gaps.

## Rules

1. Read-only. This command never writes to Leafpad, Brand Kit OS or Supermetrics.
2. Never fabricate a number; a missing source is reported as missing.
3. Do not sum or average `ctr`, `position` or `engagementRate` across rows.
4. Name the Search Console property behind every number.
