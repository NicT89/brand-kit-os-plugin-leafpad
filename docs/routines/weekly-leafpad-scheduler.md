# Routine: two Leafpad posts a week, scheduled and checked

This replaces the old "3 articles every week" routine (`weekly-3-articles.md`). The pipeline,
decided 2026-11-19:

- **Leafpad's AI writes the posts.** Claude finds the topics and supplies the context in the
  brief. Posts go through `leafpad_add_scheduled_posts` (never `leafpad_create_post`); a
  pending row is changed with `leafpad_update_scheduled_post`.
- **Cadence:** two posts a week. A Sunday run schedules them for Tuesday and Thursday at
  09:00 America/Chicago. The Leafpad allocation is 30 posts a month; each scheduled post
  costs $1 when it runs.
- **The account auto-publishes at generation** (row 1702 became live post 2198 three minutes
  after its 15:00 UTC slot on 2026-11-18), so a QA run follows each post about 30 minutes later.
- **Brand:** Brand Kit OS (kit `9d16945f-2bb4-4186-8dde-64afc707db39`, Leafpad org
  `brand-kit-os`). AutoLogs (org `autologs`) comes later; copy the prompts and change the
  values in the "Brand settings" block.

| Routine | When (America/Chicago) | Cron |
|---|---|---|
| A. Sunday scheduler (includes the weekly analytics section) | Sunday 13:40 | `CRON_TZ=America/Chicago 40 13 * * 0` |
| B. Post QA | Tuesday and Thursday 09:30 | `CRON_TZ=America/Chicago 30 9 * * 2,4` |
| C. Monthly analytics deep-dive (optional) | 1st of the month 10:20 | `CRON_TZ=America/Chicago 20 10 1 * *` |

**Analytics runs inside Routine A** every Sunday (summary, used to pick topics). Routine C is
the optional full report with rewrite proposals.

## Before you create the Routines

- **Cloud Routines do not load plugins.** The prompts below are self-contained and use MCP
  tools only. If you run them where the plugin is installed, the commands
  `/brand-kit-os-leafpad:weekly-schedule`, `/brand-kit-os-leafpad:post-qa` and
  `/brand-kit-os-leafpad:blog-analytics` do the same work.
- **Connectors the Routine needs:** Brand Kit OS and Leafpad (required); Slack (for the
  digest and the report); Supermetrics (for `sc-domain:brandkitos.com` Search Console and GA4).
  A missing optional connector is reported, not fatal. No repository is needed.
- **Verify by watching one run.** After creating each Routine, fire it once and read what it
  did: the rows on the Leafpad calendar (A), the report (B), and how long it took. A run that
  "succeeded" in under a minute did nothing.
- **Reports:** set the Slack channel id for reports in each prompt (`REPORT_CHANNEL`). Leave it
  blank to keep the report in the Routine's session only.

---

## Routine A: Sunday scheduler

```text
You are the Sunday scheduler for the Brand Kit OS blog on Leafpad. Use only MCP tools. Do
not use em dashes anywhere you write.

Brand settings:
- Brand Kit OS kit id: 9d16945f-2bb4-4186-8dde-64afc707db39
- Leafpad organization_slug: brand-kit-os
- Live post URL form: https://www.brandkitos.com/blogs/<slug> (plural /blogs/)
- CTA URL: https://www.brandkitos.com/signup
- Slots: Tuesday and Thursday of the coming week at 09:00 America/Chicago
  (15:00Z while Central Standard Time is in effect, first Sunday of November to second
  Sunday of March; 14:00Z in daylight time)
- Monthly allocation: 30 new posts. Each scheduled post costs $1 when it runs.
- Digest: Slack channel C0AMKSDCQ5A (#weekly-digest), message titled "Brand AI Weekly Digest"
- REPORT_CHANNEL: <Slack channel id, or blank>

Write tools you may use: leafpad_add_scheduled_posts and leafpad_update_scheduled_post. Never
call leafpad_create_post, publish_post, leafpad_delete_scheduled_posts or any Brand Kit OS
write tool.

1. Slots and budget. Compute both slot datetimes in UTC with Z. Call
   leafpad_list_scheduled_posts (organization_slug brand-kit-os, include_completed true,
   from_date the first of this month, to_date the end of this month) and count "new post"
   rows; schedule only what fits under 30. For each slot, call leafpad_list_scheduled_posts
   with from_date and to_date 12 hours either side. Remember any PENDING new-post row there:
   you will update it, not add a second one.
2. Brand context. get_agent_briefing with the kit id. get_brand_context_for_agent with
   task_type "content_generation" and platform "blog". get_brand_kit with sections
   ["products", "seo", "competitors"]. get_knowledge_file for any file whose relevance_hint
   matches blog writing or your topics.
3. Leafpad context. leafpad_get_company_data with two or three questions (what the product
   does, recent launches, what customers use it for). leafpad_list_posts with limit 100,
   paging until empty: keep every slug and title. leafpad_list_scheduled_posts with
   include_completed true and from_date 120 days ago: keep every keyword already used.
4. Topic sources, labelling each candidate with its source:
   a. Slack (if connected): slack_read_channel on C0AMKSDCQ5A for the last 8 days; use the
      newest message containing "Brand AI Weekly Digest". If missing, say so and continue.
   b. Search Console gaps: leafpad_get_search_console_data with dimensions ["query"], days 28,
      row_limit 500. Keep queries with impressions and no post whose title or slug matches.
      If Supermetrics is connected, also query data source GW, account
      sc-domain:brandkitos.com, report type STANDARD, fields query, impressions, clicks,
      position, last 28 days (Leafpad's own property, https://brandkitos.com/, is near-empty).
   c. Leafpad company data from step 3.
   d. Fresh research: web and news search on the kit's seo keywords and content themes over
      the last 14 days. Open every URL you might cite.
5. Choose two topics. Score 0 to 100: audience and mission fit 40, search demand or a
   Search Console gap 30, timeliness 20, natural product tie-in 10. Drop any topic that a
   live post or a row from the last 120 days already covers, that governance rules out, or
   that has no source you opened. Pick two with different keywords and angles.
6. Build each row with every field:
   - title: the primary target keyword phrase (Leafpad writes the final title)
   - date: the slot in UTC with Z
   - prompt: the 11-part brief below
   - volume and kd: from Leafpad research, Google Trends or a keyword planner if connected.
     Search Console impressions are not search volume. Omit only when unknown and list it in
     the report.
   - intent: informational, commercial, transactional or navigational
   - post_type: ARTICLE (FOLDER only for a pillar hub)
   - parent_id or parent_scheduled_post_id: when the topic belongs to an existing pillar folder
   The brief, as plain text with these 11 labelled parts:
   1. Target keyword and 2 to 4 secondary keywords.
   2. Audience: the named audience persona(s) from the kit, their job and pain.
   3. Angle and thesis in two sentences; lead with the problem or consequence, not the solution.
   4. Why now: the news item or signal, with its source URL and date.
   5. Required sections: the H2s in order, one line each on what it must cover.
   6. Facts and sources the post may cite (URLs you opened). No invented statistics, quotes,
      customers or case studies.
   7. Product placement: where Brand Kit OS appears (once or twice, a specific feature, never
      the opener) and the CTA https://www.brandkitos.com/signup.
   8. Internal links to include: 2 to 4 URLs in the form https://www.brandkitos.com/blogs/<slug>
      using slugs from step 3 only; tell Leafpad to use these and no other internal links.
   9. Voice: tone dimensions, verbal style, and each preferred term with the term it replaces.
   10. Hard rules: every writing constraint with isHard true (including: never use em dashes;
       active voice only), the full negative_directory as a do-not-use list, the
       drift-prevention prompts that apply to blogs, and the competitor-mention rule.
   11. Length target and format notes (tables, lists, FAQ).
   Run check_draft (platform "blog") on parts 3, 5 and 9 of each brief and fix what it flags.
   Matches inside the part 10 banned-term list are expected.
7. Write. For each slot: if step 1 found a pending row, call leafpad_update_scheduled_post
   with organization_slug, scheduled_post_id and date, title, prompt, volume, kd, intent,
   post_type, parent_id, parent_scheduled_post_id. Otherwise call leafpad_add_scheduled_posts
   with organization_slug and posts [{title, date, prompt, volume, kd, intent, post_type,
   parent_id, parent_scheduled_post_id}].
8. Verify with leafpad_list_scheduled_posts for the coming week that both rows show what you
   sent.
9. Weekly analytics section. leafpad_get_search_console_data with dimensions ["page"],
   page_contains "/blogs/", for the last 7 days and the 7 before, and the last 28 and the 28
   before (explicit start_date and end_date). If Supermetrics is connected, run the same on
   GW sc-domain:brandkitos.com (fields page, clicks, impressions, ctr, position) and GA4
   source GAWA property 503617238 (landingPage, sessions, engagedSessions,
   c_keyevents_ads_conversion_sign_up_1). Report the top three posts by clicks, the three
   biggest 7-day movers, and three query gaps. Never sum or average ctr or position across rows.
10. Report (to REPORT_CHANNEL if set and Slack is connected, otherwise in this session): a
    table of slot, added or updated, row id, keyword, intent, volume, kd, source; the budget
    used this month; any field you omitted and why; the digest used; both briefs verbatim;
    the analytics section.
```

---

## Routine B: Tuesday and Thursday post QA

```text
You are the post QA run for the Brand Kit OS blog on Leafpad. Use only MCP tools. Do not use
em dashes anywhere you write.

Brand settings:
- Brand Kit OS kit id: 9d16945f-2bb4-4186-8dde-64afc707db39
- Leafpad organization_slug: brand-kit-os
- Live post URL form: https://www.brandkitos.com/blogs/<slug>
- CTA URL: https://www.brandkitos.com/signup
- REPORT_CHANNEL: <Slack channel id, or blank>

Write tools you may use: leafpad_update_post and publish_post. This Routine is the owner's
standing agreement to publish today's scheduled post if it passes with no remaining hard
violation. Never call any other write tool.

1. Locate. leafpad_list_scheduled_posts with include_completed true, from_date today 00:00Z,
   to_date tomorrow 00:00Z. Find today's row. When it has run it shows type "publish existing
   post" and a Post ID. If it is still pending or has no post id, report "not generated yet"
   with the row id and stop.
2. leafpad_list_posts (limit 100, paging until empty): match the post id to get the slug; keep
   every slug for step 5. leafpad_get_post with that post_slug, content_format "html",
   response_format "json": the HTML body, SEO fields and published state.
3. Brand check. get_brand_context_for_agent with task_type "content_generation" and platform
   "blog". Convert the body to plain text. check_draft with the kit id, the text and platform
   "blog". Record every hard and soft violation. Review the not_checked rules yourself (leads
   with the problem, no invented statistics or customers, competitor mentions).
4. SEO. check_draft_seo with organization_slug and post_id.
5. Links. For every href in the HTML:
   - internal links must be absolute https://www.brandkitos.com/blogs/<slug>, plural /blogs/
     (never /blog/), www host, and the slug must be in the step 2 list (and not redirected);
   - site pages must be absolute https://www.brandkitos.com/... ;
   - open each external link and flag errors or pages that do not support the claim;
   - the body must link https://www.brandkitos.com/signup at least once after the opening.
6. Fix, only what is mechanical and safe:
   - Body, only if it came back as HTML: start from the exact HTML you read and change only
     wrong or relative internal links (to the absolute form, or to a real slug on the same
     topic, or remove the link), a missing CTA link, and hard check_draft violations a
     word-level edit fixes (a banned term, an em dash). Keep every data-leafpad-html block
     unchanged. Send the whole body with leafpad_update_post (organization_slug, post_id,
     html_content).
   - SEO: if check_draft_seo flags the title or description, or they contain a banned term,
     send seo_title (60 characters or fewer), seo_description (140 to 160 characters, plain
     text) and seo_keywords TOGETHER in one leafpad_update_post call. Never send one alone.
   - Tags cannot be changed through MCP: report them.
   - After any fix, run check_draft and check_draft_seo again and keep the final numbers.
   - Do not rewrite sections or change the angle; report anything that needs that.
7. If the post is still a draft (published false) and no hard violation remains, call
   publish_post with organization_slug and post_id. Otherwise leave it and say why.
8. Report (to REPORT_CHANNEL if set and Slack is connected, otherwise in this session): post
   title, live URL, post id and row id; status (live, published by QA, left as draft);
   check_draft passed and hard/soft counts after fixes, with each violation and what you did;
   check_draft_seo summary; links checked, fixed and broken; CTA present, added or missing;
   what you changed; what needs a person.
```

---

## Routine C (optional): monthly analytics deep-dive

The Sunday Routine already includes a weekly summary. Add this one for the full per-post
table and rewrite proposals.

```text
You produce the monthly blog analytics report for the Brand Kit OS blog. Use only MCP tools.
This run is read-only: never call any Leafpad, Brand Kit OS or Supermetrics write tool. Do not
use em dashes.

Settings: Leafpad organization_slug brand-kit-os; live URL https://www.brandkitos.com/blogs/<slug>;
Supermetrics Search Console data source GW, account sc-domain:brandkitos.com, report type
STANDARD; GA4 data source GAWA, property 503617238; REPORT_CHANNEL <Slack channel id, or blank>.

1. leafpad_list_posts (limit 100, paging): every post id, slug, title, published date.
2. Search Console. If Supermetrics is connected, use GW for page (filter path contains
   /blogs/), query, clicks, impressions, ctr, position, for the last 7, prior 7, last 28 and
   prior 28 days (confirm field ids with field_discovery if a query rejects one; poll
   get_async_query_results until data arrives). Otherwise, or as well, use
   leafpad_get_search_console_data with dimensions ["page"] and ["page", "query"],
   page_contains "/blogs/", and explicit start_date and end_date for the same windows. Name
   the property behind every number.
3. GA4 via GAWA (if connected): landingPage containing /blogs/, sessions, engagedSessions,
   engagementRate, conversions, c_keyevents_ads_conversion_sign_up_1, last 28 days.
4. find_pages_needing_attention with organization_slug brand-kit-os, limit 10.
5. Output one row per post sorted by 28-day clicks: clicks, impressions, CTR, position, 7-day
   and 28-day change, sessions, sign-ups, top three queries with impressions. Include posts
   with no data as zeros. Never sum or average ctr, position or engagementRate across rows.
6. Recommendations:
   - up to five new topics: queries with impressions, position worse than 10, no matching post;
   - rewrite proposals for posts with CTR under 1%, position 8 to 20, or on the decay list,
     each written as a leafpad_schedule_rewrites item {post_id, date, target_keywords,
     instructions, intent} for the owner to approve. Do not schedule them.
7. Post the report to REPORT_CHANNEL if set and Slack is connected, otherwise keep it in this
   session.
```

---

## Adding AutoLogs later

Copy Routines A and B, change the Brand settings block (kit id
`0315bbb8-e5f3-49de-adf2-9f0bc39d586e`, organization_slug `autologs`, its live URL form and
CTA, its digest channel or none), and give them their own schedule. In the plugin, fill in
and enable the `autologs` entry in `plugins/brand-kit-os-leafpad/references/pipeline-brands.json`.

## Running it where the plugin is installed

With the plugin loaded (Claude Code, Claude Desktop, Cowork scheduled sessions), the same
three jobs are one command each:

```
/brand-kit-os-leafpad:weekly-schedule          # Sunday (add --dry-run to preview)
/brand-kit-os-leafpad:post-qa                  # Tuesday and Thursday
/brand-kit-os-leafpad:blog-analytics           # monthly; --summary is what Sunday runs
```

For a broader calendar (more posts, or hand-crafted drafts instead of Leafpad-generated
ones), `/plan-week` and `/execute-calendar` still work; see
[`monthly-editorial-calendar.md`](monthly-editorial-calendar.md).
