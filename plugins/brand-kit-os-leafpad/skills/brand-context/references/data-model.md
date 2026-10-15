# Brand Kit OS — Data Model Reference

This document describes the data structure returned by Brand Kit OS MCP tools.

## Brand Kit Sections

### Summary (`get_brand_kit_summary`)
A compact overview (~500 tokens). **Live shape (Brand Kit OS kit):**

| Field | Type | Notes |
|-------|------|-------|
| `name`, `tagline`, `description`, `brand_voice`, `mission`, `vision` | string | May be empty string |
| `top_personality_traits` | string[] | Max 3 trait names |
| `top_values` | string[] | Max 3 value names |
| `tone` | object | From `tone_of_voice` JSONB (`attributes[]`, `description`) |
| `tone_dimensions` | object | e.g. `energy`, `warmth`, `formality`, `complexity`, `confidence` (0–100) |
| `top_constraints` | array | Max 3 from governance |
| `products` | `{ name, type, usp }[]` | |
| `primary_audiences` | `{ persona_name, persona_type, demographics }[]` | `is_primary` only |

**Example tone_dimensions:** `{ "energy": 60, "warmth": 25, "formality": 30, "complexity": 20, "confidence": 65 }`

**Example voice_archetypes (expression):** `primary.name` = "The Assistant", `secondary.name` = "The Synthesizer"

### Brand Kit Root (`update_brand_kit`) — writable
- **Name** — Brand name
- **Description** — Brand description
- **Tagline** — Brand tagline
- **Website URL** — Brand website
- **Social URLs** — JSONB array of `{ platform, url }` objects
- **Industry Details** — JSONB with sector, sub_sector, niche

### Visual Identity (`update_brand_kit_visuals`) — writable
- **Colors** — `primary_color`, `secondary_color`, `accent_color`, `background_color`, `text_primary_color`, `text_secondary_color`, `link_color`, `color_scheme`, `color_details`, `custom_1-4_color`, `custom_1-4_name`
- **Fonts** — `heading_font`, `body_font`, `paragraph_font`, `font_sizes` (JSONB), `font_weights` (JSONB), `fonts_list` (JSONB array)
- **Layout** — `spacing` (JSONB), `button_styles` (JSONB)
- **Logos** — `logo_url`, `logo_dark_url`, `favicon_url`

### Core (`get_brand_kit_core` / `upsert_brand_kit_core`)
- **Mission** — The brand's purpose
- **Vision** — The brand's aspirational future state
- **Brand Story** — Narrative arc of the brand (JSONB with structured content)
- **Brand Promises** — Commitments the brand makes to its audience
- **Taglines** — Array of brand taglines and slogans
- **Storytelling Elements** — Brand narrative and storytelling (JSONB) with keys: `origin_story_summary`, `key_milestones` (string[]), `recurring_themes` (string[]), `brand_metaphors` (string[]), `hero_narrative`, `transformation_arc`, `founder_voice_notes`

### Personality (`get_brand_kit_personality` / `upsert_brand_kit_personality`)
- **Personality Traits** — Human characteristics attributed to the brand
- **Brand Values** — Core values that guide decision-making
- **Brand Principles** — Actionable rules derived from values
- **Brand Moods** — Emotional tones associated with the brand

### Expression (`get_brand_kit_expression` / `upsert_brand_kit_expression`)
- **Tone of Voice** — How the brand sounds
- **Tone Dimensions** — Scales (e.g., formal ↔ casual)
- **Voice Archetypes** — Archetypal voice patterns
- **Verbal Style** — JSONB object with keys: `sentence_structure`, `vocabulary_level`, `punctuation_style`, and other language pattern preferences
- **Visual Style** — JSONB object describing visual identity guidelines
- **Preferred Terminology** — Words the brand uses (and avoids)
- **Content Categories** — Platform-specific content guidance
- **Situational Tone Guides** — Array of situational overrides with `situation`, `tone_adjustment`, `examples`
- **Platform Voice Rules** — Array of platform-specific rules with `platform`, `rules`, `tone_overrides`

### Products (`get_brand_kit_products` / `create_brand_kit_product` / `update_brand_kit_product`)
Array of products/services, each with:
- Name, description, type
- Key benefits, USP, competitive differentiation
- Cost and special pricing

### Audience (`get_brand_kit_audience` / `update_audience_persona` / `generate_audience_persona`)
Array of target audience personas, each with:
- Demographics, goals, pain points
- Buying behavior, preferred channels
- Content that resonates
- Core motivation
- Representative quote
- Professional context, personal background
- Expertise level, platform behavior
- **Aspirational Identity** — Who this persona aspires to become
- **Show Don't Tell Scene** — A vivid scene depicting this persona
- **Visual Identifiers** — Visual cues that identify this persona
- **Funnel Stage Triggers** — What moves this persona between funnel stages
- **Channel Behavior Matrix** — How this persona behaves across channels
- **Paid Tools** — Tools and software this persona pays for
- **Source** — How the persona was created (manual, ai_generated, imported)

### Governance (`get_brand_kit_governance` / `upsert_brand_kit_governance`)
- **Behavioral Constraints** — What the brand must/must not do
- **Negative Directory** — Blacklisted words, phrases, topics
- **Compliance Notes** — Regulatory requirements (free text)
- **Compliance Selections** — Array of selected compliance standards (GDPR, CCPA, etc.)
- **Disclosure Policy** — AI and legal disclaimers (free text)
- **Disclosure Statements** — Structured JSONB with `creation`, `transparency`, and `deployment` statement objects, each containing questions, answers, and approval status
- **Writing Constraints** — Structured JSONB object with keys like `max_sentence_length`, `active_voice_preference`, `readability_target`, formatting and structural rules
- **Usage Guidelines** — How brand assets should be used
- **Approval Workflows** — Content approval process configurations (JSONB array)
- **Drift Prevention Prompts** — Prompts to keep AI outputs on-brand (JSONB array)

### Personas (`get_brand_kit_personas` / `update_ai_persona` / `generate_ai_persona`)
AI persona configurations for different use cases (e.g., customer support bot, social media manager). Each includes:
- Name, purpose type, role definition
- Tasks, behavioral rules, tone overrides
- Voice profile, lexicon/syntax preferences
- Safety compliance, negative guardrails
- Execution protocol, interaction context
- **Personality Description** — Free-text personality description
- **Is Default** — Whether this is the default persona
- **Reference Protocols** — How the persona handles citations and sources

### Competitors (`get_brand_kit_competitors` / `create_brand_kit_competitor` / `update_brand_kit_competitor`)
Array of competitor brands, each with:
- Name, URL, description, tagline
- Brand colors, fonts, typography
- Brand personality, value propositions
- Social profiles, design framework
- Logo URL, color scheme

### SEO (`get_brand_kit_seo` / `upsert_brand_kit_seo`)
- **Keywords** — Target SEO keywords (JSONB array)
- **Tags** — Content tags (JSONB array)
- **Suggested Keywords** — AI-suggested keywords (JSONB array)

### Expression Examples (`list_expression_examples` / `create_expression_example`)
Array of brand voice content samples, each with:
- Platform (linkedin, twitter, email, blog, etc.)
- Context type (post, reply, headline, caption, cta, etc.)
- User response (the brand-voice example text)
- Original content (what was being adapted)
- Source (manual, ai_generated, imported)

### Social Profiles (`get_brand_kit_social_profiles`)
Connected social media accounts with full metadata: platform, profile URL, bio, headline, followers, business category, etc.

### Logo Assets (`list_logo_assets` / `get_logo_asset` / `update_logo_asset`)
Array of logo variants, each with:
- Asset key, label, URL/storage path
- Description, long description, usage guidelines
- File type, dimensions, size
- Default flag, sort order

### Knowledge Files (`list_knowledge_files` / `get_knowledge_file` / `upload_knowledge_file`)
Supplementary documents attached to a brand kit (style guides, playbooks, etc.). Linked via `brand_kit_knowledge_files` to `library_knowledge_files`.

## Write Tool Summary

| Tool | Table | Action |
|------|-------|--------|
| `update_brand_kit` | `brand_kits` | Update name, description, tagline, website, social URLs, industry |
| `update_brand_kit_visuals` | `brand_kits` | Update colors, fonts, spacing, logos |
| `upsert_brand_kit_core` | `brand_kit_core` | Upsert mission, vision, story, promises, taglines, storytelling |
| `upsert_brand_kit_personality` | `brand_kit_personality` | Upsert traits, values, principles, moods |
| `upsert_brand_kit_expression` | `brand_kit_expression` | Upsert tone, voice, style, terminology, situational guides, platform rules |
| `upsert_brand_kit_governance` | `brand_kit_governance` | Upsert constraints, negative dir, writing rules, workflows, drift prompts |
| `upsert_brand_kit_seo` | `brand_kit_seo` | Upsert keywords, tags, suggested keywords |
| `create_brand_kit_product` | `brand_kit_products` | Create product |
| `update_brand_kit_product` | `brand_kit_products` | Update product |
| `update_audience_persona` | `brand_kit_target_audience` | Update audience persona |
| `generate_audience_persona` | `brand_kit_target_audience` | AI-generate audience persona (1 token) |
| `update_ai_persona` | `brand_kit_personas` | Update AI persona |
| `generate_ai_persona` | `brand_kit_personas` | AI-generate AI persona (1 token) |
| `create_expression_example` | `expression_examples` | Create expression example |
| `create_brand_kit_competitor` | `brand_kit_competitors` | Create competitor |
| `update_brand_kit_competitor` | `brand_kit_competitors` | Update competitor |
| `update_logo_asset` | `brand_kit_logo_assets` | Update logo asset metadata |
| `upload_knowledge_file` | `user_knowledge_file_uploads` | Upload knowledge file |

All write tools support `dry_run: true` for previewing changes before committing. All require the `brand_kit:write` scope (except `upload_knowledge_file` which requires `knowledge_files:write`).