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
| `published` | boolean | resolved from `${user_config.publish_mode}` + override flags | **Defaults to `true`.** For a draft you MUST send `published: false`, or the post goes live |
| `seo_title` | string ≤60 | `seo-optimizer` | Flat field — **not** nested under a `seo` object |
| `seo_description` | string 140–160 | `seo-optimizer` | **Plain text.** Do NOT HTML-escape it — a literal `&amp;` here renders as `&amp;` in the meta tag. Use a raw `&` |
| `seo_keywords` | **comma-separated string** | `seo-optimizer` + `get_brand_kit_expression.preferred_terminology` | e.g. `"brand drift, brand consistency, AI governance"`. Not a JSON array |
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

## Scheduling — `leafpad_add_scheduled_posts`

Used when `mode === "scheduled"`. **Not yet calibrated** in the 2026-06-13 round-trip — confirm its exact `scheduled_at` format (ISO-8601 vs epoch, timezone handling) and accepted field set before relying on it, and record the result here.

## Brand Kit OS sections consumed (full breadth)

`/publish-pipeline` calls these in parallel to build the article. They feed the **body and SEO**, which then project onto the verified fields above.

| Brand Kit OS tool | Feeds | Used for |
|---|---|---|
| `get_brand_kit_summary` | (planning only) | Topic-fit scoring against brand mission |
| `get_brand_kit_core` | `html_content` (intro + closing CTA) | Mission/promise framing, taglines |
| `get_brand_kit_personality` | `html_content` (tone calibration) | Traits, values, principles, moods |
| `get_brand_kit_expression` | `html_content` (voice), `seo_keywords`, `tags` | Voice, preferred terminology, content categories, visual style (→ image brief) |
| `get_brand_kit_governance` | `html_content` (compliance copy + disclosure footer), formatting rules | Writing constraints (no em dashes, max 1 exclamation, `&` for `and`), negative directory, disclosure policy |
| `get_brand_kit_audience` | `html_content` (persona-aware framing) | Persona targeting |
| `get_brand_kit_products` | `html_content` (CTAs, product callouts) | Product CTAs and differentiators |
| `get_brand_kit_personas` | (byline context only) | `author` is auto-set by Leafpad, so persona name informs voice, not the byline field |
| `list_knowledge_files` + `get_knowledge_file` | `html_content` (style adherence) | Apply long-form style guides and playbooks |

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
  published:       mode === "published",                  // false for draft/scheduled-staging
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
