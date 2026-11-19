# Scheduled post brief template

The template every scheduled Leafpad post is built from. Used by `/weekly-schedule`,
`/ai-schedule`, `/execute-calendar --ai-schedule`, the `leafpad-ai-scheduler` agent and the
Routine prompts in `docs/routines/weekly-leafpad-scheduler.md`.

**Division of labour.** Leafpad's AI writes the post (it produces better metadata,
formatting and images). Claude finds the topic and supplies the context. Leafpad already
holds its own layer of brand context (Business Overview, Writing Style, Keywords, Blog
Options, Knowledge Base); the brief adds the Brand Kit OS layer on top, every time.

## What Leafpad does with a scheduled row (verified 2026-11-18/19)

- Generates the post at `date`, charges **$1**, and on the `brand-kit-os` account
  **publishes it immediately** (row 1702 became live post 2198 three minutes after its slot).
- Rewrites the title: treat `title` as the target keyword, not the headline.
- Chooses the slug, tags, SEO title and description, featured image, 2 to 4 body images and
  internal links. Its internal links can be wrong (`/blog/` singular, or slugs that do not
  exist), which is why the brief lists the links to use and `/post-qa` checks them.

## Scheduled-post fields: fill every one, every time

| Field | Value |
|---|---|
| `organization_slug` | From the brand config, e.g. `brand-kit-os` |
| `title` | Primary target keyword phrase (Leafpad writes the final title) |
| `date` | ISO 8601 UTC with `Z`. Tuesday and Thursday 09:00 America/Chicago: `15:00Z` in CST (first Sunday of November to second Sunday of March), `14:00Z` in CDT |
| `prompt` | The full brief (11 parts below) |
| `volume` | Monthly search volume for the keyword if known (Leafpad research, Google Trends, a keyword planner). Search Console impressions are not search volume. Omit only when genuinely unknown, and say so in the run report |
| `kd` | Keyword difficulty 0 to 100 if known. Same rule |
| `intent` | `informational`, `commercial`, `transactional` or `navigational` |
| `post_type` | `ARTICLE` (or `FOLDER` for a pillar hub) |
| `parent_id` | Existing folder post id, when the post belongs to an existing pillar cluster |
| `parent_scheduled_post_id` | Scheduled folder row id, when the parent hub is itself still scheduled |

Call shape:

```
leafpad_add_scheduled_posts({
  organization_slug: "brand-kit-os",
  posts: [{ title, date, prompt, volume, kd, intent, post_type, parent_id, parent_scheduled_post_id }]
})
```

If `leafpad_list_scheduled_posts` already shows a **pending** "new post" row in the target
slot, change it with `leafpad_update_scheduled_post({ organization_slug, scheduled_post_id, ... })`
instead of adding a second row.

## The brief (`prompt`): 11 parts, in this order

Write the brief as plain text with a short label per part. Every part is required.

1. **Target keyword** and 2 to 4 secondary keywords.
2. **Audience**: the named Brand Kit OS audience persona(s) (from `get_brand_context_for_agent`
   or `get_brand_kit` `sections: ["audience"]`), their job and their pain, in one or two sentences.
3. **Angle and thesis** in two sentences. Lead with the problem or its consequence, never
   with the solution or the product.
4. **Why now**: the news item or signal that makes this timely, with its source URL and date
   (from the Brand AI Weekly Digest, a news search, or a Search Console trend).
5. **Required sections**: the H2s in order, with one line each on what the section must cover.
6. **Facts and sources** the post may cite, as URLs you have opened and confirmed. State
   plainly: no invented statistics, quotes, customers or case studies.
7. **Product placement and call to action**: where and how the product appears (once or
   twice, a specific feature, never the opener) and the CTA URL
   (`https://www.brandkitos.com/signup` for Brand Kit OS).
8. **Internal links to include**: 2 to 4 live URLs in absolute form, e.g.
   `https://www.brandkitos.com/blogs/<slug>` (plural `/blogs/`; every slug confirmed in
   `leafpad_list_posts`) or site pages. Tell Leafpad to use these and no other internal links.
9. **Voice**: from the kit: tone dimensions, verbal style, and `preferred_terminology` with
   the terms each one replaces ("say X instead of Y").
10. **Hard rules**: every `writing_constraints` entry with `isHard: true` (for Brand Kit OS: no
    em dashes, active voice only), the full `negative_directory` as a do-not-use list, the
    drift-prevention prompts that apply to blogs, and the competitor-mention rule. Quote the
    banned terms as a list; that is the one place they may appear.
11. **Length and format**: word target (e.g. 1,200 to 1,600 words), plus tables, lists or an
    FAQ where they help the reader.

## Example skeleton

```
1. Target keyword: <keyword>. Secondary: <k2>, <k3>, <k4>.
2. Audience: <persona name>: <job>; pain: <pain>.
3. Angle: <problem or consequence>. Thesis: <claim the post proves>.
4. Why now: <signal>, <source URL>, <date>.
5. Sections (H2, in order):
   - <H2 one>: <what it must cover>
   - <H2 two>: <what it must cover>
   - ...
6. Sources you may cite: <URL 1>, <URL 2>, <URL 3>. No invented statistics, quotes,
   customers or case studies.
7. Product: mention Brand Kit OS once or twice, never in the opening, as <specific feature>.
   CTA: https://www.brandkitos.com/signup
8. Internal links (use these, absolute, and no others): https://www.brandkitos.com/blogs/<slug-a>,
   https://www.brandkitos.com/blogs/<slug-b>
9. Voice: <tone dimensions>. <verbal style>. Say "<preferred>" instead of "<avoid>"; ...
10. Hard rules: never use em dashes; active voice only; do not name competitors unless
    <rule>; <drift-prevention prompts>. Never use these words or phrases: <full negative directory>.
11. Length: <N to M> words. Use a comparison table and a short FAQ.
```

## Checks before scheduling

- `check_draft` on parts 3, 5 and 9 (the prose) with `platform: "blog"`. The banned-term
  list in part 10 will match by design; ignore matches inside that list only.
- Every URL in parts 4, 6 and 8 opened and confirmed (internal slugs via `leafpad_list_posts`).
- `leafpad_list_posts` (search the keyword) and `leafpad_list_scheduled_posts`
  (`include_completed: true`, last 120 days) show no post or row on the same keyword.
