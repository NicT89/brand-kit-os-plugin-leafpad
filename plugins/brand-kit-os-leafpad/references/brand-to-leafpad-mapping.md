# Brand Kit OS → Leafpad Field Mapping

The canonical mapping from Brand Kit OS data into Leafpad's post payload. Used by `leafpad-publisher`, `seo-optimizer`, and `content-generation` to build the richest post the Leafpad MCP actually accepts.

> **Calibrated 2026-06-13** against the live Leafpad MCP (`leafpad_create_post` / `leafpad_update_post` JSON schemas + a real draft round-trip, post `brand-drift-new-technical-debt-ai-tools`). The earlier "rich payload + strip-on-reject" model assumed many fields that the tool does not expose. Those have been moved to **Unsupported** below. Treat this file as the source of truth; re-verify if Leafpad ships a schema change.

## How this is used

1. `content-generation` drafts the body and `seo-optimizer` builds the SEO block, both as an internal **rich article object** (shape at the end of this doc).
2. `leafpad-publisher` **projects** that object onto the lean set of fields `leafpad_create_post` actually accepts (see Verified below). It does not send unsupported fields.
3. Strip-on-reject is retained only as a defensive fallback. In practice the tool schema is `additionalProperties: false`, so the host never even forms a call containing unknown fields — the correct mapping is what keeps publishes clean, not the retry loop.

## Verified Leafpad fields — `leafpad_create_post`

This is the **complete** accepted field set (the tool schema is closed; nothing else is accepted).

| Leafpad field | Type | Brand Kit OS source | Notes |
|---|---|---|---|
| `organization_slug` | string | resolved via `leafpad_list_organizations` | **Required.** e.g. `brand-kit-os` |
| `name` | string | drafted title from `content-generation` | **Required.** This is the post title |
| `slug` | string | kebab-case from `name` | Optional; auto-derived if omitted |
| `html_content` | string (**HTML**, not markdown) | drafted body, rendered to HTML | There is **no** markdown `content` field and **no** `content_format`. Convert the draft to HTML before sending. Escape literal `&` as `&amp;` inside the body |
| `post_type` | enum `ARTICLE` \| `FOLDER` | always `ARTICLE` for posts | Default `ARTICLE` |
| `published` | boolean | resolved from `${user_config.publish_mode}` + override flags | **Defaults to `false`** (re-verified 2026-11-19: the tool now creates an unpublished draft unless `published: true`). Still send `published: false` explicitly for drafts. `publish_post` publishes a draft later |
| `seo_title` | string ≤60 | `seo-optimizer` | Flat field — **not** nested under a `seo` object |
| `seo_description` | string 140–160 | `seo-optimizer` | **Plain text.** Do NOT HTML-escape it — a literal `&amp;` here renders as `&amp;` in the meta tag. Use a raw `&` |
| `seo_keywords` | **comma-separated string** | `seo-optimizer` + expression `preferred_terminology` (from `get_brand_context_for_agent`) | e.g. `"brand drift, brand consistency, AI governance"`. Not a JSON array |
| `tags` | **comma-separated string** of tag names | `seo-optimizer` from `leafpad_list_tags` + draft body | e.g. `"Brand Consistency, AI Governance"`. New names are created automatically; existing names are reused. Pass names, not IDs |

### Verified behaviors (from the live round-trip)

- **Tags persist and are reusable.** `leafpad_list_tags` returned 27 existing tags and the 4 we reused came back intact on read. The older "tags return `[]`" caveat did **not** reproduce on this instance — verify per instance, but do not assume tags are broken.
- **`author` is auto-assigned** from the authenticated OAuth identity (we sent nothing; it came back as the account owner's name). It is **not** settable on create. Treat `author_name` as auto-generated.
- **Body must be HTML.** Markdown sent as `html_content` is stored verbatim, not rendered.

## Unsupported on create — do NOT send

The tool schema does not include these. They are not "candidates"; sending them is a hard error. Listed here so agents stop trying.

`excerpt`, `custom_excerpt`, `feature_image`, `feature_image_alt`, `feature_image_caption`, `og_image`, `twitter_image`, `canonical_url`, `meta_title`, `meta_description`, `author_name`, `author_id`, `categories`, `visibility`, `content_format`, `reading_time`, `published_at`, and any nested `seo { ... }` object.

- **Images** are a separate step, not a create field. Use **`leafpad_generate_image`** to produce a feature/inline image, then embed or attach it. `seo-optimizer`'s image brief feeds that tool, not a `feature_image` field.
- **Excerpt / categories / reading_time / canonical_url / visibility** have no home on this instance. Keep them in the rich article object for other channels, but the Leafpad projection drops them.

## Update path — `leafpad_update_post` caveats

- **SEO fields are co-required.** Sending `seo_description` alone returns `422 … Required at "seo.title"; Required at "seo.keywords"`. Always resend the full trio (`seo_title` + `seo_description` + `seo_keywords`) together on any SEO edit.
- **Tags are immutable after creation.** `leafpad_update_post` has no `tags` parameter. To change tags you must recreate the post (matches the documented limitation — now schema-confirmed).
- Updatable fields: `name`, `slug`, `html_content`, `published`, `seo_title`, `seo_description`, `seo_keywords`.
- **`html_content` replaces the whole body.** Read the post first with `leafpad_get_post` and `content_format: "html"` (custom HTML blocks survive only in that format), edit, and send the full body back.
- **Publishing a draft:** `publish_post({ organization_slug, post_id })` makes one draft live and notifies a configured webhook. Use it only when the user (or a Routine the user set up) has agreed to publish.

## Scheduling: `leafpad_add_scheduled_posts` (re-verified 2026-11-19)

**Scheduling is a different model from drafting.** You do **not** send a finished article with a publish timestamp. You queue a target keyword and a brief, and Leafpad **generates** the post on the date.

```
leafpad_add_scheduled_posts({
  organization_slug,               // e.g. "brand-kit-os" (not an id)
  posts: [{
    title,                         // target keyword phrase; Leafpad writes the final title (required)
    date,                          // ISO 8601 UTC with Z, e.g. "2026-11-24T15:00:00Z" (required)
    prompt,                        // the full brief; see scheduled-brief-template.md
    volume,                        // monthly search volume (integer >= 0), if known
    kd,                            // keyword difficulty 0 to 100, if known
    intent,                        // informational | commercial | transactional | navigational
    post_type,                     // "ARTICLE" (default) or "FOLDER" for a pillar hub
    parent_id,                     // existing folder post to nest under
    parent_scheduled_post_id       // scheduled folder row whose generated post becomes the parent
  }]
})
```

There is no `scheduled_at`, `secondary_prompt` or `organization_id` parameter. Older versions of this plugin sent those names; they were wrong.

- **Cost:** each scheduled post charges **$1** to the organization's balance when it runs. `leafpad_create_post` posts are never charged.
- **Auto-publish:** the `brand-kit-os` account publishes at generation. Observed 2026-11-18: scheduled row 1702 produced post 2198, live at 15:03 UTC, 3 minutes after its 15:00 UTC slot. The row's type changes from "new post" to "publish existing post" and it carries the new post id. There is no draft option on this tool today (requested in `LEAFPAD_REQUESTS.md`).
- **What Leafpad decides:** the final title, slug, tags, SEO fields, featured image, 2 to 4 body images and internal links. Its internal links can point at `/blog/...` (singular) or at slugs that do not exist; QA must flag those.
- **Live URL:** `https://www.brandkitos.com/blogs/<slug>` (plural `/blogs/`).

### The queue: list, change, remove

| Tool | Use |
|---|---|
| `leafpad_list_scheduled_posts({ organization_slug, include_completed, from_date, to_date, limit })` | Rows soonest first, with scheduled post id, type (new post, rewrite, publish existing post), status, date, title, prompt and keyword data. `include_completed: true` adds rows that already ran (and their post id). |
| `leafpad_update_scheduled_post({ organization_slug, scheduled_post_id, ... })` | Change a pending row. New post rows take `date`, `title`, `prompt`, `volume`, `kd`, `intent`, `post_type`, `parent_id`, `parent_scheduled_post_id`; rewrite rows take `instructions`, `target_keywords`, `url`, `volume`, `kd`, `intent`. A row that ran cannot change. |
| `leafpad_delete_scheduled_posts({ organization_slug, scheduled_post_ids })` | Remove pending rows (1 to 50). Never charged; rows that already ran are kept as history. |
| `leafpad_schedule_rewrites({ organization_slug, rewrites: [{ post_id, date, instructions, target_keywords, url, volume, kd, intent }] })` | AI rewrite of an existing post, published in place. Uses the daily update allowance and, on a paid plan, a refresh credit. |

Before adding a row, always check the queue: if a pending new-post row already holds the target slot, update it with the new-post fields instead of adding a second one. Never send new-post fields to a rewrite row; report that conflict instead.

## Images — `leafpad_generate_image`

Images are a separate call, not a post field.

```
leafpad_generate_image({ organization_slug, prompt }) -> public CDN URL
```

- Leafpad applies the **org's brand style + color palette** automatically, so the prompt only needs subject/style/mood.
- There is no featured-image field on `leafpad_create_post`; embed the returned URL as an `<img>` in `html_content` (it becomes an image block in Leafpad's editor). Note (2026-11-19): the tool's description now says its URL "can be passed as a post's featured image" to `leafpad_create_post` / `leafpad_update_post`, but neither tool's schema exposes such a field. Until one appears, body-inline is the only path. Scheduled (AI-generated) posts get a featured image from Leafpad automatically.
- Optional args (2026-11-19 schema): `aspect` (`landscape` default, `square`, `portrait`), `quality`, `brand_style` (default true), `file_name` (SEO file name).
- ⚠️ **Known issue (2026-06-24): `leafpad_generate_image` returns `Unauthorized` server-side** even though every other Leafpad tool (read + write) authenticates with the same token. The OAuth resource advertises no scopes (`scopes_supported: []`), and create/update/schedule all succeed — so it's a Leafpad-side entitlement or token-propagation bug, not a client auth problem. Filed in `LEAFPAD_REQUESTS.md`.
- **Fallback while it's down:** generate with **Gamma** (`generate` → read the AI image's `src` on `cdn.gamma.app` from the result JSON) or **Higgsfield**, then embed that URL. Caveat: those hot-link a non-Leafpad CDN; prefer Leafpad's CDN once the tool is fixed.
- **Add/replace an image on an existing post:** call `leafpad_update_post` with the full `html_content` re-sent plus the `<img>` (update replaces the whole body). Verified working 2026-06-24.

## Brand Kit OS sections consumed (full breadth)

`/publish-pipeline` calls these in parallel to build the article. They feed the **body and SEO**, which then project onto the verified fields above.

Brand Kit OS MCP 3.0 tools (the per-section getters such as `get_brand_kit_expression` were removed in 3.0):

| Brand Kit OS call | Feeds | Used for |
|---|---|---|
| `get_brand_kit` (no `sections`: the summary) | (planning only) | Topic-fit scoring against brand mission |
| `get_brand_context_for_agent` (`task_type: "content_generation"`, `platform: "blog"`) | `html_content` (voice, compliance copy, disclosure footer), `seo_keywords`, `tags`, scheduled `prompt` | Voice, preferred terminology, content categories, visual style (image brief), writing constraints, negative directory, disclosure policy, audience, examples, knowledge index |
| `get_brand_kit` `sections: ["core"]` | `html_content` (intro + closing CTA) | Mission/promise framing, taglines |
| `get_brand_kit` `sections: ["personality"]` | `html_content` (tone calibration) | Traits, values, principles, moods |
| `get_brand_kit` `sections: ["products"]` | `html_content` (CTAs, product callouts) | Product CTAs and differentiators |
| `get_brand_kit` `sections: ["seo"]` | `seo_keywords`, scheduled `title` | Target keywords |
| `get_brand_kit` `sections: ["ai_personas"]` | (byline context only) | `author` is auto-set by Leafpad, so persona name informs voice, not the byline field |
| `get_knowledge_file` | `html_content` (style adherence) | Long-form style guides and playbooks from the knowledge index |
| `check_draft` | gate before any publish | Every body is checked; hard violations block publish |

## Rich article intermediate object → Leafpad projection

`content-generation` + `seo-optimizer` still build the full rich object (it serves channels beyond Leafpad). `leafpad-publisher` projects only the supported slice.

```
rich_article = {
  title, slug,
  body_markdown,            // converted to HTML for html_content
  excerpt,                  // dropped for Leafpad (kept for social/index)
  tags: string[],           // joined to a comma string for Leafpad
  categories: string[],     // dropped for Leafpad
  seo: { title, description, keywords[] },   // flattened to seo_title/seo_description/seo_keywords
  feature_image: { prompt, alt, caption },   // routed to leafpad_generate_image, not a create field
  reading_time,             // dropped for Leafpad
  internal_links: [...],    // inserted into body before send
  brand_application_notes: { ... }
}

leafpad_create_post payload = {
  organization_slug,
  name:            rich_article.title,
  slug:            rich_article.slug,
  html_content:    toHTML(rich_article.body_markdown),   // with internal links inserted
  post_type:       "ARTICLE",
  published:       mode === "published",                  // false for draft (also the default)
  seo_title:       rich_article.seo.title,
  seo_description: rich_article.seo.description,           // raw text, no &amp;
  seo_keywords:    rich_article.seo.keywords.join(", "),
  tags:            rich_article.tags.join(", ")
}
```

## schema_fit reporting

`leafpad-publisher` still returns a `schema_fit` block so future schema drift is caught:

```
schema_fit:
  accepted: ["organization_slug","name","slug","html_content","post_type","published","seo_title","seo_description","seo_keywords","tags"]
  stripped: []                       # should stay empty now that the mapping matches the schema
  auto_generated: ["author"]         # Leafpad sets the byline from the OAuth identity
```

If anything lands in `stripped`, the Leafpad schema changed — update this file.
