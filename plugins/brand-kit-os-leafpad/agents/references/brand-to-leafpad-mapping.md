# Brand Kit OS → Leafpad Field Mapping

The canonical mapping from Brand Kit OS data into Leafpad's post payload. Used by `leafpad-publisher`, `seo-optimizer`, and `content-generation` to build the richest possible post.

## How this is used

1. `content-generation` and `seo-optimizer` build an internal **rich article object** with every field below populated where possible.
2. `leafpad-publisher` attempts the full payload against `leafpad_create_post`.
3. If Leafpad rejects an unknown field (error matching `unknown field`, `unexpected property`, `not allowed`, or a 4xx schema error), the publisher strips the offending field and retries — once per unknown field, max 3 retries total.
4. The publish report lists which fields were **accepted** and which were **stripped**, so the user can confirm the Leafpad instance's actual schema.

## Verified Leafpad fields (from `leafpad_create_post`)

These are documented in the plugin README and known to work:

| Leafpad field | Type | Brand Kit OS source | Notes |
|---|---|---|---|
| `name` | string | drafted title from `content-generation` | Required |
| `slug` | string | generated from `name` (kebab-case) | Auto-generated if omitted |
| `content` | string (markdown) | drafted body from `content-generation` | Required |
| `tags` | string[] | `seo-optimizer` from `leafpad_list_tags` + drafted body | `leafpad_list_tags` may return `[]` — see README limitation |
| `seo.title` | string ≤60 | `seo-optimizer` | Leads with primary keyword |
| `seo.description` | string 140–160 | `seo-optimizer` | One primary keyword, value-statement close |
| `seo.keywords` | string[] (4–8) | `seo-optimizer` + `get_brand_kit_expression.preferred_terminology` | Never use `negative_directory` terms |
| `published` | boolean | resolved from `${user_config.publish_mode}` + override flags | `true` only when `mode === "published"` |

## Candidate Leafpad fields (attempt + strip-on-reject)

These are commonly supported by blog-MCP servers but **not confirmed** in the README field list. The publisher will attempt them and strip on rejection.

| Leafpad field | Type | Brand Kit OS source | Why we attempt it |
|---|---|---|---|
| `excerpt` | string (1–2 sentences) | `seo-optimizer` — derived from intro paragraph | Used for blog index pages and social previews; richer than `seo.description` |
| `custom_excerpt` | string | same as `excerpt` | Some platforms split SEO desc from excerpt |
| `feature_image` | string (URL) | `seo-optimizer.feature_image_prompt` + visual brief from `get_brand_kit_expression.visual_style` | If Leafpad auto-generates feature images (known behavior), this is overridden — flag it |
| `feature_image_alt` | string | derived from title | Accessibility |
| `feature_image_caption` | string | from `seo-optimizer` | Used by some themes |
| `og_image` | string (URL) | usually same as `feature_image` | Social card image override |
| `twitter_image` | string (URL) | usually same as `feature_image` | Twitter card override |
| `canonical_url` | string (URL) | omitted by default | Set only when republishing existing content |
| `meta_title` | string | mirrors `seo.title` | Some platforms separate `<title>` from `seo.title` |
| `meta_description` | string | mirrors `seo.description` | Some platforms separate `<meta>` from `seo.description` |
| `author_name` | string | `get_brand_kit_personas` default persona name, else brand author | Whose byline shows |
| `author_id` | string | resolved via `leafpad_list_organizations` if needed | Some platforms require id, not name |
| `categories` | string[] | `get_brand_kit_expression.content_categories` | Distinct from tags on many platforms |
| `visibility` | enum (`public` \| `members` \| `paid`) | omitted unless brand kit governance says so | Defaults to whatever Leafpad's default is |
| `content_format` | enum (`markdown` \| `html` \| `lexical`) | `"markdown"` | Set explicitly to avoid ambiguous parsing |
| `reading_time` | integer (minutes) | computed from body word count ÷ 220 | Some platforms compute this themselves |
| `scheduled_at` | string (ISO-8601) | from `--schedule <iso>` flag | Required for `leafpad_add_scheduled_posts` |
| `published_at` | string (ISO-8601) | omitted unless backdating | Some platforms accept it on create |

## Brand Kit OS sections consumed (full breadth)

`/publish-pipeline` calls these in parallel to build the article. Each lands in specific Leafpad fields per the mapping above.

| Brand Kit OS tool | Lands in | Used for |
|---|---|---|
| `get_brand_kit_summary` | (planning only) | Topic-fit scoring against brand mission |
| `get_brand_kit_core` | `content` (intro + closing CTA) | Mission/promise framing |
| `get_brand_kit_personality` | `content` (tone calibration) | Traits, values, principles |
| `get_brand_kit_expression` | `content` (voice), `seo.keywords`, `tags`, `categories`, `feature_image` brief | Voice, terminology, visual style, content categories |
| `get_brand_kit_governance` | `content` (compliance copy), `tags` (exclusions), disclosure footer | Constraints, negative directory, disclosure policy |
| `get_brand_kit_audience` | `content` (persona-aware framing), `excerpt` | Persona targeting |
| `get_brand_kit_products` | `content` (CTAs, product callouts) | Product CTAs and differentiators |
| `get_brand_kit_personas` | `author_name` (when AI persona is the byline) | Persona-driven authorship |
| `list_knowledge_files` + `get_knowledge_file` | `content` (style adherence) | Apply long-form style guides and playbooks |

## Rich article intermediate object

The shape that `content-generation` + `seo-optimizer` build before `leafpad-publisher` maps it:

```
{
  title: string,
  slug: string,
  body: string (markdown),
  excerpt: string,
  tags: string[],
  categories: string[],
  seo: { title, description, keywords[] },
  feature_image: { url?: string, prompt: string, alt: string, caption?: string },
  og_image: { url?: string },
  author: { name?: string, id?: string },
  visibility: "public" | "members" | "paid",
  content_format: "markdown",
  reading_time: number,
  internal_links: [{ anchor, target_slug, reason }],
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
    auto_generated: ["feature_image"]            # Leafpad ignored our value and generated its own (known behavior)
```

Run `/brand-kit-os-leafpad:publish-pipeline <topic> --draft` once after install and inspect this section. Anything in `stripped` is a field your Leafpad instance doesn't support — update this reference doc to move it from "candidate" to "unsupported" so we stop retrying it.
