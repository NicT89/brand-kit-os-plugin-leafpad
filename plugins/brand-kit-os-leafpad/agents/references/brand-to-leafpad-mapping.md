# Brand Kit OS → Leafpad Field Mapping

The canonical mapping from Brand Kit OS data into Leafpad's post payload. Used by `leafpad-publisher`, `seo-optimizer`, and `content-generation` to build the richest possible post.

## How this is used

1. `content-generation` and `seo-optimizer` build an internal **rich article object** with every field below populated where possible.
2. `leafpad-publisher` attempts the full payload against `leafpad_create_post`.
3. If Leafpad rejects an unknown field, the publisher strips it and retries — max 3 retries.
4. The publish report lists which fields were **accepted** and which were **stripped**, so users can confirm their Leafpad instance's actual schema.

## Leafpad fields (per direct intel from Leafpad MCP docs)

These are the post fields exposed by `leafpad_create_post` / `leafpad_update_post`. `leafpad_update_post` can edit **every** field, including tags — there is no "tags can only be set at creation" limitation (corrected in v1.5.0).

| Leafpad field | Type | Brand Kit OS source | Notes |
|---|---|---|---|
| `name` | string | drafted title from `content-generation` | Required |
| `slug` | string | generated from `name` (kebab-case) | Auto-generated if omitted |
| `content` | **HTML** string | drafted body from `content-generation` | Required. Leafpad expects HTML, not Markdown — convert if needed. |
| `tags` | string[] | `seo-optimizer` from `leafpad_list_tags` + drafted body | Use `leafpad_list_tags` to reuse existing tags |
| `seo.title` (or `seo_title`) | string ≤60 | `seo-optimizer` | Leads with primary keyword |
| `seo.description` (or `seo_description`) | string 140–160 | `seo-optimizer` | One primary keyword, value-statement close |
| `seo.keywords` (or `seo_keywords`) | string[] (4–8) | `seo-optimizer` + `get_brand_kit_expression.preferred_terminology` | Never use `negative_directory` terms |
| `published` | boolean | resolved from `${user_config.publish_mode}` + override flags | `true` only when `mode === "published"` |

## Candidate fields (attempt + strip-on-reject)

Sent in the first publish attempt; stripped if Leafpad rejects them. Some are confirmed; others are inferred from typical CMS shapes and need validation per instance.

| Leafpad field | Type | Brand Kit OS source | Status |
|---|---|---|---|
| `excerpt` | string | `seo-optimizer` | Likely supported — Leafpad shows excerpts on index pages |
| `feature_image` | string (URL) | `leafpad_generate_image` returns CDN URL | Confirmed via the `leafpad_generate_image` MCP tool |
| `feature_image_alt` | string | derived from title | Accessibility |
| `og_image` | string (URL) | usually same as `feature_image` | To verify |
| `twitter_image` | string (URL) | usually same as `feature_image` | To verify |
| `canonical_url` | string (URL) | omitted by default | Only when republishing |
| `author_name` | string | `get_brand_kit_personas` default persona name | To verify |
| `author_id` | string | resolved via `leafpad_list_organizations` if needed | To verify |
| `categories` | string[] | `get_brand_kit_expression.content_categories` | To verify (distinct from tags) |
| `visibility` | enum | omitted unless brand kit governance says so | To verify |

## Server-computed fields (do not send)

Leafpad's public API derives these automatically on publish. Sending them is wasteful at best and likely rejected. `seo-optimizer` skips them; document for the user in the publish report.

| Leafpad field | How Leafpad derives it |
|---|---|
| `wordCount` | counted from `content` |
| `articleSection` | inferred from tags/categories |
| `inLanguage` | detected from `content` |
| `isAccessibleForFree` | from `visibility` |
| FAQPage JSON-LD | auto-extracted when 2+ H2/H3 headings end in `?` |
| Markdown delivery (`<post-url>.md`) | served alongside HTML for AI consumers; part of the llms.txt + AIO behavior |

## Brand Kit OS sections consumed (full breadth)

`/publish-pipeline` calls these in parallel to build the article. Each lands in specific Leafpad fields per the mapping above.

| Brand Kit OS tool | Lands in | Used for |
|---|---|---|
| `get_brand_kit_summary` | (planning only) | Topic-fit scoring against brand mission |
| `get_brand_kit_core` | `content` (intro + closing CTA) | Mission/promise framing |
| `get_brand_kit_personality` | `content` (tone calibration) | Traits, values, principles |
| `get_brand_kit_expression` | `content` (voice), `seo.keywords`, `tags`, `categories`, feature image style | Voice, terminology, visual style, content categories |
| `get_brand_kit_governance` | `content` (compliance copy), disclosure footer | Constraints, negative directory, disclosure policy |
| `get_brand_kit_audience` | `content` (persona-aware framing), `excerpt` | Persona targeting |
| `get_brand_kit_products` | `content` (CTAs, product callouts) | Product CTAs and differentiators |
| `get_brand_kit_personas` | `author_name` (when AI persona is the byline) | Persona-driven authorship |
| `list_knowledge_files` + `get_knowledge_file` | `content` (style adherence) | Apply long-form style guides and playbooks |

## Leafpad tools consumed during publish

| Leafpad tool | When | Purpose |
|---|---|---|
| `leafpad_list_organizations` | publisher resolves org | Determine target org |
| `leafpad_get_company_data` | content-generation research step | Pull real org facts from Leafpad KB to ground article claims |
| `leafpad_list_posts` | seo-optimizer | Internal-link candidates |
| `leafpad_get_post` | seo-optimizer (deep analysis) | Read markdown of a candidate internal-link target |
| `leafpad_list_tags` | seo-optimizer | Reuse existing tags |
| `leafpad_generate_image` | seo-optimizer | Brand-aligned feature image; returns CDN URL |
| `leafpad_create_post` | publisher (draft/published modes) | Create post |
| `leafpad_update_post` | post-publish corrections | Edit any field on an existing post |
| `leafpad_add_scheduled_posts` | `/ai-schedule` only | AI-generate a future post (NOT a delayed publish of our draft) |

## Rich article intermediate object

The shape that `content-generation` + `seo-optimizer` build before `leafpad-publisher` maps it:

```
{
  title: string,
  slug: string,
  body: string (HTML),
  excerpt: string,
  tags: string[],
  categories: string[],
  seo: { title, description, keywords[] },
  feature_image: { url: string (CDN URL from leafpad_generate_image), prompt: string, alt: string, caption?: string },
  og_image: { url?: string },
  author: { name?: string, id?: string },
  visibility: "public" | "members" | "paid",
  internal_links: [{ anchor, target_slug, reason }],
  kb_facts_used: [{ fact, source }],          # from leafpad_get_company_data
  brand_application_notes: {
    voice: string,
    tone: string,
    terminology: string[],
    governance: string[],
    audience_persona: string,
    products_referenced: string[],
    knowledge_files_applied: string[]
  }
}
```

## Verification loop

Because some candidate fields may not be supported by the user's Leafpad instance, the publisher reports back:

```
Publish Result:
  ...
  schema_fit:
    accepted: ["name", "slug", "content", "tags", "seo", "published", "excerpt", "feature_image"]
    stripped: ["canonical_url", "visibility"]   # rejected by Leafpad, retried without
    auto_generated: ["feature_image"]            # Leafpad generated its own (when omitted)
```

Run `/brand-kit-os-leafpad:publish-pipeline <topic> --draft` once after install and inspect this section. Anything in `stripped` is a field your Leafpad instance doesn't support — update this reference doc to move it from "candidate" to "unsupported" so we stop retrying.
