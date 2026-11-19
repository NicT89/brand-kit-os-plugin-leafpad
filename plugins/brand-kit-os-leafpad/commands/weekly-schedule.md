---
description: Sunday run. Research two topics for the coming week, write full briefs from the Brand Kit OS kit, and schedule them on Leafpad for Tuesday and Thursday (updating any pending rows), plus a weekly analytics section.
argument-hint: '[--brand <key>] [--week-of <YYYY-MM-DD>] [--dry-run]'
---

# Weekly Schedule

The Sunday half of the scheduled pipeline. It picks two topics for the coming week, writes a
full brief for each from the Brand Kit OS kit, and puts them on Leafpad's content calendar for
Tuesday and Thursday at 09:00 America/Chicago. Leafpad's AI writes and publishes the posts;
`/brand-kit-os-leafpad:post-qa` checks each one after it generates.

> **Cost and visibility.** Each scheduled post costs **$1** when it runs, and the
> `brand-kit-os` account **auto-publishes at generation**. The brief is the last point of
> control before a post is public, so this command fills every field, every time.

## Arguments

- `--brand <key>`: the brand entry in `references/pipeline-brands.json` (default `brand-kit-os`). Only entries with `enabled: true` run.
- `--week-of <YYYY-MM-DD>`: the Monday of the target week (default: the Monday after today).
- `--dry-run`: do every read and build both rows, show them, and write nothing to Leafpad.

## Per-brand config

Read the brand's entry from `references/pipeline-brands.json`, overridden by
`~/.brand-kit-os-leafpad/brands/<key>/pipeline.json` when that file exists. It supplies
`brand_kit_id`, `leafpad_org`, `site_base_url`, `blog_path`, `cta_url`, `cadence`,
`monthly_post_allocation`, the `digest` Slack channel, and the Search Console / GA4 ids. No
value in this command is specific to Brand Kit OS except as an example; adding AutoLogs means
filling in its entry and setting `enabled: true`.

## Workflow

### 1. Slots and budget

1. Compute the two slots from `cadence`: the Tuesday and Thursday of the target week at
   `local_time` in `timezone`, converted to UTC with `Z`. For 09:00 America/Chicago that is
   `15:00Z` in CST and `14:00Z` in CDT.
2. `leafpad_list_scheduled_posts` with `include_completed: true`, `from_date` the first of the
   month and `to_date` the end of the month. Count "new post" rows. If adding two would pass
   `monthly_post_allocation`, schedule only what fits and say so.
3. For each slot, `leafpad_list_scheduled_posts` with `from_date` and `to_date` 12 hours either
   side of it. A **pending** "new post" row there is updated in step 7, not duplicated.

### 2. Brand Kit OS context

- `get_agent_briefing` with `brand_kit_id` (kit health; note any section flagged as weak).
- `get_brand_context_for_agent` with `task_type: "content_generation"` and `platform` from the
  config (`blog`): voice, tone dimensions, `preferred_terminology`, governance
  (`negative_directory`, `writing_constraints`, drift-prevention prompts), expression
  examples, audience personas and the knowledge-file index.
- `get_brand_kit` with `sections: ["products", "seo", "competitors"]`: product features for
  placement, target keywords, and the competitor-mention rules.
- `get_knowledge_file` for any file whose `relevance_hint` matches blog writing or the topics.

### 3. Leafpad context

- `leafpad_get_company_data` with two or three questions (what the product does, recent
  launches, what customers use it for). This is Leafpad's own knowledge base.
- `leafpad_list_posts` with `limit: 100`, paging until empty: every live slug and title, for
  dedupe and for the internal-link list.
- `leafpad_list_scheduled_posts` with `include_completed: true` and `from_date` 120 days ago:
  every keyword already queued or already generated.

### 4. Topic sources

Gather candidates from all of these, labelling each with its source:

1. **Brand AI Weekly Digest** (when Slack is connected): `slack_read_channel` on the config's
   `digest.slack_channel_id` (`C0AMKSDCQ5A`, #weekly-digest) for the last 8 days. Use the most
   recent message whose text contains `digest.title_contains`. It is posted on Monday nights,
   so a Sunday run reads the one from six days earlier. If Slack is not connected or no
   digest is found, say so and continue.
2. **Search Console gaps**: `leafpad_get_search_console_data` with `dimensions: ["query"]`,
   `days: 28`, `row_limit: 500`. Keep queries with impressions and no post whose title or slug
   matches. Leafpad's connected property is the near-empty URL-prefix property
   (`https://brandkitos.com/`); when the Supermetrics connector is present, also query
   `sc-domain:brandkitos.com` (ds `GW`) the way `/brand-kit-os-leafpad:blog-analytics` does.
3. **Leafpad company data** from step 3: launches and product facts worth a post.
4. **Fresh research**: a web or news search for the brand's themes (from the kit's `seo`
   keywords and `content_categories`) over the last 14 days. Open every URL you plan to cite.

### 5. Choose two topics

Score each candidate 0 to 100: mission and audience fit (40), search demand or a Search
Console gap (30), timeliness (20), product tie-in without forcing it (10). Drop anything that:

- matches a live post or a row from the last 120 days on the same keyword or intent,
- governance rules out (negative directory topics, competitor rules),
- has no source you could open and confirm.

Pick the top two, on different keywords and different angles.

### 6. Build each row

Follow `references/scheduled-brief-template.md` exactly:

- `title`: the primary target keyword phrase.
- `date`: the slot from step 1.
- `prompt`: all 11 parts. Internal links come from step 3's slug list, in absolute
  `site_base_url` + `blog_path` + slug form. CTA is `cta_url`.
- `volume`, `kd`: from Leafpad research, Google Trends, or a keyword planner when connected.
  Search Console impressions are not volume. Omit only when unknown, and list the gap in the
  report.
- `intent`, `post_type` (`ARTICLE`), and `parent_id` / `parent_scheduled_post_id` when the
  topic belongs to an existing pillar folder.

Run `check_draft` on each brief's prose parts (angle, sections, voice notes) with the config's
`platform`. Matches inside the part 10 banned-term list are expected; fix anything else.

### 7. Write to Leafpad (skipped with `--dry-run`)

For each slot:

- **Pending row exists**: `leafpad_update_scheduled_post` with `organization_slug`,
  `scheduled_post_id` and every field (`date`, `title`, `prompt`, `volume`, `kd`, `intent`,
  `post_type`, `parent_id`, `parent_scheduled_post_id`).
- **No row**: `leafpad_add_scheduled_posts` with `organization_slug` and
  `posts: [{ title, date, prompt, volume, kd, intent, post_type, parent_id, parent_scheduled_post_id }]`.

Never call `leafpad_create_post` here.

### 8. Verify

`leafpad_list_scheduled_posts` for the target week. Confirm each row shows the date, title,
prompt and keyword data you sent. A "done" from the write call is a claim; the listing is the
evidence.

### 9. Weekly analytics section

Run the summary form of `/brand-kit-os-leafpad:blog-analytics` (last 7 and 28 days): the
top posts by clicks, posts that moved most, and up to three query gaps that informed or could
inform topic choice.

### 10. Report

Post the report to the config's `qa_report_slack_channel_id` when Slack is connected and it
is set; otherwise return it in the session.

```
Weekly schedule: <brand> · week of <Monday>
| Slot (UTC)            | Action  | Row id | Keyword | Intent | Volume | KD | Source |
|-----------------------|---------|--------|---------|--------|--------|----|--------|
| Tue 2026-11-24 15:00Z | added   | ...    | ...     | ...    | ...    | .. | digest |
| Thu 2026-11-26 15:00Z | updated | ...    | ...     | ...    | unknown| .. | GSC gap|

Budget: N of <allocation> new posts this month ($1 each when they run).
Missing data: <fields omitted and why, or "none">
Digest used: <message date and link | not found | Slack not connected>
Briefs: <each prompt verbatim>
Analytics: <section from step 9>
Next: /post-qa runs Tue and Thu about 09:30 America/Chicago.
```

## Rules

1. Fill every field on every row; omit `volume` or `kd` only when genuinely unknown, and say so.
2. One row per slot. Update a pending row; never add a duplicate.
3. Never schedule a keyword that a live post or a recent row already covers.
4. Every cited URL and internal link in a brief has been opened or confirmed in `leafpad_list_posts`.
5. No invented statistics, quotes or customers, in the brief or asked of Leafpad.
6. Respect `monthly_post_allocation`.
7. Write tools used: `leafpad_add_scheduled_posts` and `leafpad_update_scheduled_post` only.
