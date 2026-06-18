---
name: leafpad-publisher
description: Publish a finalized article to Leafpad in draft, published, or scheduled mode. Maps the full rich-article object to Leafpad fields per the brand-to-leafpad-mapping reference, and adapts to the user's actual Leafpad schema via strip-on-reject retry.
---

# Leafpad Publisher Agent

Takes a finalized rich-article object (the shape defined in `../references/brand-to-leafpad-mapping.md`) and publishes it to Leafpad. Encapsulates field mapping, mode dispatch (`draft` / `published` / `scheduled`), strip-on-reject schema adaptation, and failure handling.

## When to activate

- The `/brand-kit-os-leafpad:publish-pipeline` command delegates here after QA passes
- The `cowork-digest-publisher` agent delegates here in its publish step
- Any future workflow needs to send a vetted article to Leafpad

## Inputs

- `article` — rich-article object per `../references/brand-to-leafpad-mapping.md` (used for `draft`/`published`)
- `mode` — `draft` | `published` | `scheduled`. Default is `${user_config.publish_mode}`, falling back to `draft`.
- `image_url` — optional. CDN URL from `leafpad_generate_image`, embedded in the body as an `<img>`.
- For `scheduled` mode only: `schedule = { title, date (ISO-8601 UTC), prompt }` — a topic, a future date, and a brand-voice generation prompt. **Not** a finished article.
- `organization_slug` — optional. Resolved via `leafpad_list_organizations` if needed.

## Workflow

1. **Validate inputs** — For `draft`/`published`, ensure `article.title` and `article.body` are present. For `scheduled`, ensure `schedule.title` and `schedule.date` are present. If a required field is missing, return an error without calling Leafpad.

2. **Resolve organization** — If `organization_id` not provided, call `leafpad_list_organizations`. If there's exactly one, use it. If multiple, ask the user once.

3. **Project to the verified Leafpad payload** — `leafpad_create_post` accepts a closed, lean field set (calibrated 2026-06-13; full detail in `../references/brand-to-leafpad-mapping.md`). Build exactly this payload — do not add fields the schema does not expose:
   - `organization_slug` ← resolved org
   - `name` ← `article.title` (**required**)
   - `slug` ← `article.slug` (else kebab-case from title)
   - `html_content` ← `toHTML(article.body)` with internal links inserted and, if `image_url` is present, an `<img src="image_url" alt="…">` near the top (**HTML, not markdown** — there is no `content`/`content_format` field; there is no separate featured-image field, so the image lives in the body). Escape literal `&` as `&amp;` in the body
   - `post_type` ← `"ARTICLE"`
   - `published` ← `mode === "published"` (**defaults to `true` if omitted — always send `false` for draft/scheduled staging**)
   - `seo_title` ← `article.seo.title` (flat field, not nested)
   - `seo_description` ← `article.seo.description` (**raw text — never HTML-escape; a literal `&amp;` here leaks into the meta tag**)
   - `seo_keywords` ← `article.seo.keywords.join(", ")` (**comma string**, not array)
   - `tags` ← `article.tags.join(", ")` (**comma string** of names; existing names are reused, new ones auto-created)

   **Do not send:** `excerpt`, `feature_image`/`og_image`, `categories`, `author_name`, `canonical_url`, `visibility`, `content_format`, `reading_time`, or a nested `seo {}` object — none exist on this tool. Feature images are a separate `leafpad_generate_image` call, and `author` is auto-set from the OAuth identity.

4. **Dispatch by mode**:
   - `draft` → `leafpad_create_post` with `published: false`
   - `published` → `leafpad_create_post` with `published: true`
   - `scheduled` → `leafpad_add_scheduled_posts` with `organization_slug` and `posts: [{ title: schedule.title, date: schedule.date, prompt: schedule.prompt }]`. **`date` is ISO-8601 in UTC with `Z`** (verified accepted, e.g. `2026-06-23T14:00:00Z`). Leafpad **generates** the post on that date from the title + prompt — no `html_content`/`seo`/`tags` are sent in this mode. Encode the brand voice rules and the word-count/title rules into `schedule.prompt`.

5. **Strip-on-reject retry** — If the Leafpad MCP error message matches any of:
   - `unknown field`
   - `unexpected property`
   - `not allowed`
   - `invalid_field`
   - a 4xx schema/validation error mentioning a field name

   Then:
   1. Parse the offending field name from the error
   2. Remove it from the payload
   3. Retry the same dispatch call
   4. Max **3 retries total**. After that, return error + remaining payload.

   Track every stripped field in `schema_fit.stripped` for the report.

6. **Detect auto-generation** — If the response succeeds but a field came back different from what was sent (notably `author`, which Leafpad sets from the OAuth identity), record it in `schema_fit.auto_generated`.

7. **Failure handling (non-schema errors)** — On any Leafpad MCP error that doesn't match a schema-reject pattern (auth, network, server), return the full article + error and **do not retry**. The caller decides whether to retry, edit, or escalate.

8. **Report** — Return the Leafpad URL, the resolved mode, and the `schema_fit` block so the caller (and the user) can see which candidate fields landed.

## MCP tools used

| Tool | Server | Purpose |
|------|--------|---------|
| `leafpad_create_post` | leafpad | Create draft or live post (`draft`/`published` modes) |
| `leafpad_add_scheduled_posts` | leafpad | Queue a topic for Leafpad to generate on a future date (`scheduled` mode) |
| `leafpad_generate_image` | leafpad | (Upstream) generate the on-brand feature image; its URL is passed in as `image_url` |
| `leafpad_list_organizations` | leafpad | Resolve organization when ambiguous |

## Output format

```
Publish Result:
  status: success | error
  mode: draft | published | scheduled
  url: https://...                 # when status=success (draft/published)
  post_id: ...                     # when status=success (draft/published)
  scheduled: { id, title, date }   # when mode=scheduled (Leafpad will generate it on date)
  schema_fit:
    accepted: ["organization_slug", "name", "slug", "html_content", "post_type", "published", "seo_title", "seo_description", "seo_keywords", "tags"]
    stripped: []                                 # should stay empty — mapping matches the verified schema. Anything here means Leafpad changed its schema; update ../references/brand-to-leafpad-mapping.md
    auto_generated: ["author"]                   # Leafpad sets the byline from the OAuth identity
  caveats:
    - "Tags could not be verified — leafpad_list_tags returned []"
  error: "..."                     # when status=error
```

## Rules

1. Never mutate `article.body` — this agent only publishes; content edits belong upstream
2. Never call `leafpad_update_post` to fix tags — `leafpad_update_post` has no `tags` parameter; tags are immutable after creation. If tags are wrong, recreate the post.
3. **When editing SEO via `leafpad_update_post`, send the full trio** (`seo_title` + `seo_description` + `seo_keywords`) together. Sending `seo_description` alone returns `422 … Required at "seo.title"; Required at "seo.keywords"`.
4. **Strip-on-reject is a fallback, not the plan** — the verified mapping should land cleanly. Keep it bounded at max 3 retries; never silently drop required fields (`name`, `html_content`)
5. On non-schema Leafpad MCP failure (auth, network, 5xx), return the article + error and stop — do not retry blindly
6. Always include the `mode` and full `schema_fit` block in the output. This is how the user discovers their Leafpad schema and updates `../references/brand-to-leafpad-mapping.md`
7. Never fabricate a Leafpad URL — only return URLs that came back from the MCP response
