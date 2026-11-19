---
description: Tuesday and Thursday run after Leafpad generates the scheduled post. Finds the post, checks it against the Brand Kit OS kit, its links, CTA and on-page SEO, fixes what it safely can, publishes it if still a draft, and reports.
argument-hint: '[--brand <key>] [--date <YYYY-MM-DD>] [--post <slug or id>] [--no-fix]'
---

# Post QA

The Tuesday and Thursday half of the scheduled pipeline. Run it about 30 minutes after the
slot (09:30 America/Chicago for a 09:00 slot). Leafpad has already generated the post and, on
the `brand-kit-os` account, already published it, so this pass corrects a live page.

## Arguments

- `--brand <key>`: the brand entry in `references/pipeline-brands.json` (default `brand-kit-os`).
- `--date <YYYY-MM-DD>`: the slot date to check (default today).
- `--post <slug or id>`: skip discovery and check this post.
- `--no-fix`: report only; make no `leafpad_update_post` or `publish_post` call.

## Workflow

### 1. Locate the generated post

1. `leafpad_list_scheduled_posts` with `include_completed: true`, `from_date` the slot date at
   00:00Z and `to_date` the next day at 00:00Z.
2. Find the row for today's slot. When it has run, its type reads "publish existing post"
   and it carries a **Post ID** (row 1702 carried post 2198). If the row is still pending or
   has no post id, report "not generated yet" with the row id and stop.
3. `leafpad_list_posts` (`limit: 100`, paging) and match the post id to get its `slug`,
   title, tags, SEO description and timestamps. Keep the full slug list for step 4.
4. `leafpad_get_post` with `post_slug`, `content_format: "html"` and `response_format: "json"`
   for the body, SEO fields and published state. Read HTML, not markdown: custom HTML blocks
   survive only in HTML, and any fix replaces the whole body.

### 2. Brand check

1. `get_brand_context_for_agent` with `task_type: "content_generation"` and `platform: "blog"`
   (the negative directory, hard writing constraints, drift-prevention prompts).
2. Convert the body to plain text (title, headings, paragraphs, list items, table cells).
3. `check_draft` with `brand_kit_id`, `draft_text` and `platform: "blog"`. Record every hard
   and soft violation with its match and suggested fix. Review the `not_checked` rules by hand
   (e.g. leads with the problem, no invented statistics or customers, competitor mentions).

### 3. On-page SEO

`check_draft_seo` with `organization_slug` and `post_id`: title length, meta description,
word count, headings, images, links, tags, and any saved guardrail result.

### 4. Links and call to action

Extract every `href` in the HTML body.

- **Internal links** (anything pointing at the brand's own site, relative or absolute):
  - must be absolute: `site_base_url` + `blog_path` + slug, e.g. `https://www.brandkitos.com/blogs/<slug>`;
  - must use `/blogs/` (plural), never `/blog/`;
  - the slug must exist in the step 1 slug list (and not be a redirected post);
  - relative links (`/blogs/x`, `/x`) and the bare `https://brandkitos.com` host get rewritten
    to the absolute `www` form.
- **Site pages** (pricing, signup, features): absolute `https://www.brandkitos.com/...` form.
- **External links**: open each one; flag 4xx/5xx or a page that does not support the claim
  it is attached to.
- **Call to action**: the body links `cta_url` (`https://www.brandkitos.com/signup`) at least
  once, with clear anchor text, after the opening section.

The site normalizes `/blog/` and missing slugs at render time, but the stored HTML should
still be correct; flag every case.

### 5. Fix (skipped with `--no-fix`)

Fix only what is mechanical and safe; report everything else for a person.

- **Body** (`leafpad_update_post` with `organization_slug`, `post_id`, `html_content`): only
  when the body came back as HTML. Start from the exact HTML read in step 1 and change only:
  broken or relative internal links (to the absolute form, or to a real slug on the same
  topic; remove the link if none fits), a missing CTA link, and hard `check_draft`
  violations that a word-level edit fixes (a banned term, an em dash). Send the whole body
  back; keep every custom `data-leafpad-html` block unchanged. Leafpad has no revision
  precondition, so call `leafpad_get_post` again just before sending: if the body differs from
  what step 1 read, someone edited it; stop and report instead of overwriting.
- **SEO** (`leafpad_update_post` with `seo_title`, `seo_description` and `seo_keywords`
  **together**; sending one alone returns a 422): when `check_draft_seo` flags the title or
  description, or they contain a banned term. Title 60 characters or fewer; description 140
  to 160 characters, plain text.
- **Tags** cannot be changed through MCP; report tag problems for the Leafpad UI.
- After any fix, run `check_draft` again on the new text and `check_draft_seo` again.
- Do not rewrite sections, change the angle, or touch the title beyond a banned term. A post
  that needs that is reported, and a rewrite can be scheduled with `leafpad_schedule_rewrites`
  after a person agrees.

### 6. Publish if still a draft

If the post's published flag is false, `publish_post` with `organization_slug` and `post_id`.
The Routine that runs this command is the user's standing agreement to publish posts that
pass with no remaining hard violation. A post with a remaining hard violation stays a draft
and is reported. (On this account, generated posts are normally already live.)

### 7. Report

Post to the config's `qa_report_slack_channel_id` when Slack is connected and it is set;
otherwise return it in the session.

```
Post QA: <brand> · <slot date>
Post: <title> · https://www.brandkitos.com/blogs/<slug> · post <id> (row <row id>)
Status: live | published by QA | left as draft (reason)

check_draft: passed <true/false> · hard <N> · soft <N> (after fixes)
  - <violation, match, fixed | left (why)>
check_draft_seo: <score or summary> · <flags>
Links: <N internal> (<N fixed>), <N external> (<N broken>), CTA <present | added | missing>
  - <href> -> <issue> -> <fixed to ... | left>
Fixes sent: body <yes/no> · SEO trio <yes/no>
Needs a person: <tag changes, rewrites, judgement calls, or "none">
```

## Rules

1. Never edit a post body read as markdown; read and write HTML only.
2. Send the SEO trio together or not at all.
3. Never invent a replacement link; use a slug from `leafpad_list_posts` or remove the link.
4. Re-check after every fix; report the final numbers, not the first ones.
5. Write tools used: `leafpad_update_post` and `publish_post` only, and never with `--no-fix`.
