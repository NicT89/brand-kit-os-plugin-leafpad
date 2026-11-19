# Brand Kit OS: Data Model Reference

This document describes the data structure returned by the Brand Kit OS MCP tools (server
3.0 and later). Verified against the live server's `get_agent_briefing` tool map on
2026-11-19.

## The 3.0 read tools

| Tool | What it returns |
|------|-----------------|
| `get_agent_briefing` | Session bootstrap. No `brand_kit_id`: the accessible kits. With `brand_kit_id`: kit metadata, per-section health, the next step and a ranked backlog. Always includes `account_settings` (whether writes need `confirm: true`). `include: ["tool_map"]` adds the section-to-tool map. |
| `list_brand_kits` | Every kit the user can access, with `membership_role` and write capability. |
| `get_brand_kit` | Any part of a kit. No `sections`: the compact summary plus `available_sections`. `sections: [...]` returns `{ brand_kit_id, sections: { <name>: data } }`. Optional `fields`, `filter`, `ids`, `platform` (for `platform_expressions`), `view` (for `ai_personas`). |
| `get_brand_context_for_agent` | One-call bundle for a task. `task_type: "content_generation"` plus `platform` returns voice, governance (banned terms, hard constraints), expression examples, audience and the knowledge-file index. `output: "system_prompt"` with `persona_name` returns one AI persona's system prompt. |
| `get_knowledge_file` | The full body and metadata of one knowledge file. |
| `check_draft` | Checks `draft_text` against the kit's anti-slop rules, negative directory and writing constraints, plus house rules. Returns hard and soft violations with fixes, `passed`, `not_checked` and `next_step`. Deterministic and free. |

### Removed in 3.0 and what replaces them

| Removed tool | Use instead |
|---|---|
| `get_brand_kit_summary` | `get_brand_kit` with no `sections` (or `get_agent_briefing` with `brand_kit_id` for health) |
| `get_brand_kit_core` | `get_brand_kit` with `sections: ["core"]` |
| `get_brand_kit_personality` | `get_brand_kit` with `sections: ["personality"]` |
| `get_brand_kit_expression` | `get_brand_kit` with `sections: ["expression"]`, or the `get_brand_context_for_agent` bundle |
| `get_platform_expression` | `get_brand_kit` with `sections: ["platform_expressions"]` and `platform` |
| `get_brand_kit_governance` | `get_brand_kit` with `sections: ["governance"]`, or the bundle |
| `get_brand_kit_audience` | `get_brand_kit` with `sections: ["audience"]`, or the bundle |
| `get_brand_kit_products` | `get_brand_kit` with `sections: ["products"]` |
| `get_brand_kit_personas` | `get_brand_kit` with `sections: ["ai_personas"]` (`view: "index"` for a slim list) |
| `list_knowledge_files` | `get_brand_kit` with `sections: ["knowledge_files"]`, or the bundle's knowledge index |

### Sections `get_brand_kit` accepts

`summary`, `core`, `personality`, `expression`, `platform_expressions`, `governance`,
`visuals`, `seo`, `products`, `partners`, `audience`, `ai_personas`, `competitors`,
`customers`, `company_icps`, `social_profiles`, `logo_assets`, `visual_assets`,
`expression_examples`, `knowledge_files`, `customer_quotes`, `objections`,
`anti_slop_rules`, `attack_angles`, `content_drafts`, `competitor_suggestions`, `all`.

## Brand Kit Sections

### Summary (`get_brand_kit` with no `sections`)
A compact overview. **Live shape (Brand Kit OS kit, 2026-11-19):**

| Field | Type | Notes |
|-------|------|-------|
| `name`, `tagline`, `description`, `brand_voice`, `mission`, `vision` | string | May be empty string |
| `top_personality_traits` | string[] | Max 3 trait names |
| `top_values` | string[] | Max 3 value names |
| `tone` | object | `attributes[]` (attribute, min_label, max_label, value) and `description` |
| `tone_dimensions` | object | e.g. `energy`, `warmth`, `formality`, `complexity`, `confidence`, `humor` (0 to 100). Authoritative tone scale |
| `voice_tone_semantics` | object | How to read `brand_voice` vs `tone` |
| `top_constraints` | array | Max 3 from governance; strings or rule objects (`rule`, `type`, `isHard`, `platform`) |
| `products` | `{ name, type, usp }[]` | |
| `primary_audiences` | `{ persona_name, persona_type, demographics }[]` | `is_primary` only |

The response also carries `available_sections` (every section name with what it holds) and `how_to_request`.

**Example tone_dimensions:** `{ "energy": 60, "formality": 50, "warmth": 45, "confidence": 45, "complexity": 40, "humor": 80 }`

### Brand Kit Root (`update_brand_kit`): writable
- **Name**: Brand name
- **Description**: Brand description
- **Tagline**: Brand tagline
- **Website URL**: Brand website
- **Social URLs**: JSONB array of `{ platform, url }` objects
- **Industry Details**: JSONB with sector, sub_sector, niche

### Visual Identity (`get_brand_kit` `sections: ["visuals"]` / `update_brand_kit` with `visuals`)
- **Colors**: `primary_color`, `secondary_color`, `accent_color`, `background_color`, `text_primary_color`, `text_secondary_color`, `link_color`, `color_scheme`, `color_details`, `custom_1-4_color`, `custom_1-4_name`
- **Fonts**: `heading_font`, `body_font`, `paragraph_font`, `font_sizes` (JSONB), `font_weights` (JSONB), `fonts_list` (JSONB array)
- **Layout**: `spacing` (JSONB), `button_styles` (JSONB)
- **Logos**: `logo_url`, `logo_dark_url`, `favicon_url`

### Core (`get_brand_kit` `sections: ["core"]` / `update_brand_kit` with `core`)
- **Mission**: The brand's purpose
- **Vision**: The brand's aspirational future state
- **Brand Story**: Narrative arc of the brand (JSONB with structured content)
- **Brand Promises**: Commitments the brand makes to its audience
- **Taglines**: Array of brand taglines and slogans
- **Storytelling Elements**: Brand narrative and storytelling (JSONB) with keys: `origin_story_summary`, `key_milestones` (string[]), `recurring_themes` (string[]), `brand_metaphors` (string[]), `hero_narrative`, `transformation_arc`, `founder_voice_notes`

### Personality (`get_brand_kit` `sections: ["personality"]` / `update_brand_kit` with `personality`)
- **Personality Traits**: Human characteristics attributed to the brand
- **Brand Values**: Core values that guide decision-making
- **Brand Principles**: Actionable rules derived from values
- **Brand Moods**: Emotional tones associated with the brand

### Expression (`get_brand_kit` `sections: ["expression"]` or `["platform_expressions"]` + `platform` / `update_brand_kit` with `expression`)
- **Tone of Voice**: How the brand sounds
- **Tone Dimensions**: scales (e.g., formal to casual)
- **Voice Archetypes**: Archetypal voice patterns
- **Verbal Style**: JSONB object with keys: `sentence_structure`, `vocabulary_level`, `punctuation_style`, and other language pattern preferences
- **Visual Style**: JSONB object describing visual identity guidelines
- **Preferred Terminology**: Words the brand uses (and avoids)
- **Content Categories**: Platform-specific content guidance
- **Situational Tone Guides**: Array of situational overrides with `situation`, `tone_adjustment`, `examples`
- **Platform Voice Rules**: Array of platform-specific rules with `platform`, `rules`, `tone_overrides`

### Products (`get_brand_kit` `sections: ["products"]` / `manage_product`)
Array of products/services, each with:
- Name, description, type
- Key benefits, USP, competitive differentiation
- Cost and special pricing

### Audience (`get_brand_kit` `sections: ["audience"]` / `manage_audience_persona` / `generate_records` kind `audience_persona`)
Array of target audience personas, each with:
- Demographics, goals, pain points
- Buying behavior, preferred channels
- Content that resonates
- Core motivation
- Representative quote
- Professional context, personal background
- Expertise level, platform behavior
- **Aspirational Identity**: Who this persona aspires to become
- **Show Don't Tell Scene**: A vivid scene depicting this persona
- **Visual Identifiers**: Visual cues that identify this persona
- **Funnel Stage Triggers**: What moves this persona between funnel stages
- **Channel Behavior Matrix**: How this persona behaves across channels
- **Paid Tools**: Tools and software this persona pays for
- **Source**: How the persona was created (manual, ai_generated, imported)

### Governance (`get_brand_kit` `sections: ["governance"]` / `update_brand_kit` with `governance`)
- **Behavioral Constraints**: What the brand must/must not do
- **Negative Directory**: banned words, phrases and topics. `check_draft` tests drafts against it
- **Compliance Notes**: Regulatory requirements (free text)
- **Compliance Selections**: Array of selected compliance standards (GDPR, CCPA, etc.)
- **Disclosure Policy**: AI and legal disclaimers (free text)
- **Disclosure Statements**: Structured JSONB with `creation`, `transparency`, and `deployment` statement objects, each containing questions, answers, and approval status
- **Writing Constraints**: rule objects (`rule`, `type`, `isHard`, `platform`). `isHard: true` rules are non-negotiable; `check_draft` reports them as hard violations
- **Usage Guidelines**: How brand assets should be used
- **Approval Workflows**: Content approval process configurations (JSONB array)
- **Drift Prevention Prompts**: Prompts to keep AI outputs on-brand (JSONB array)

### AI Personas (`get_brand_kit` `sections: ["ai_personas"]` / `manage_ai_persona` / `generate_records` kind `ai_persona`)
AI persona configurations for different use cases (e.g., customer support bot, social media manager). Each includes:
- Name, purpose type, role definition
- Tasks, behavioral rules, tone overrides
- Voice profile, lexicon/syntax preferences
- Safety compliance, negative guardrails
- Execution protocol, interaction context
- **Personality Description**: Free-text personality description
- **Is Default**: Whether this is the default persona
- **Reference Protocols**: How the persona handles citations and sources

### Competitors (`get_brand_kit` `sections: ["competitors"]` / `manage_competitor`)
Array of competitor brands, each with:
- Name, URL, description, tagline
- Brand colors, fonts, typography
- Brand personality, value propositions
- Social profiles, design framework
- Logo URL, color scheme

### SEO (`get_brand_kit` `sections: ["seo"]` / `update_brand_kit` with `seo`)
- **Keywords**: Target SEO keywords (JSONB array)
- **Tags**: Content tags (JSONB array)
- **Suggested Keywords**: AI-suggested keywords (JSONB array)

### Expression Examples (`get_brand_kit` `sections: ["expression_examples"]` / `manage_expression_example`)
Array of brand voice content samples, each with:
- Platform (linkedin, twitter, email, blog, etc.)
- Context type (post, reply, headline, caption, cta, etc.)
- User response (the brand-voice example text)
- Original content (what was being adapted)
- Source (manual, ai_generated, imported)

### Social Profiles (`get_brand_kit` `sections: ["social_profiles"]`)
Connected social media accounts with full metadata: platform, profile URL, bio, headline, followers, business category, etc.

### Logo Assets (`get_brand_kit` `sections: ["logo_assets"]`, with `ids` for full rows / `manage_logo_asset`)
Array of logo variants, each with:
- Asset key, label, URL/storage path
- Description, long description, usage guidelines
- File type, dimensions, size
- Default flag, sort order

### Knowledge Files (`get_brand_kit` `sections: ["knowledge_files"]` / `get_knowledge_file` / `manage_knowledge_file`)
Supplementary documents attached to a brand kit (style guides, playbooks, etc.). Linked via `brand_kit_knowledge_files` to `library_knowledge_files`.

### Anti-slop Rules (`get_brand_kit` `sections: ["anti_slop_rules"]` / `manage_anti_slop_rule`)
Banned terms and AI-tell rules for drafts. `check_draft` applies them.

### Objections (`get_brand_kit` `sections: ["objections"]` / `manage_objection`)
Buyer objections with responses, links and evidence.

### Customers, Company ICPs, Partners, Customer Quotes
`get_brand_kit` with `sections: ["customers"]`, `["company_icps"]`, `["partners"]` or `["customer_quotes"]`. Only approved quotes are usable proof (`include_proposed` also returns quotes waiting for review).

## Write Tool Summary (3.0)

| Tool | Writes |
|------|--------|
| `update_brand_kit` | Root fields and any of `core`, `personality`, `expression`, `governance`, `visuals`, `seo` (several sections in one atomic call) |
| `manage_product` | Products (`action: create / update`) |
| `manage_audience_persona` | Audience personas |
| `manage_ai_persona` | AI personas |
| `manage_competitor` | Competitors and competitor suggestions |
| `manage_partner` | Partners |
| `manage_company_profile` | Customers and company ICPs (`kind`) |
| `manage_expression_example` | Expression examples |
| `manage_logo_asset`, `manage_visual_asset` | Logo and visual assets |
| `manage_knowledge_file` | Knowledge files (`upload`, `create_upload_url`, `update`) |
| `manage_objection`, `manage_anti_slop_rule`, `manage_attack_angle` | Review-queue items; may be staged for human approval (`routed_to_review: true`) |
| `archive_records` | Archive or restore any record (hard deletes were removed in 3.0) |
| `generate_records`, `enrich_record`, `scrape_source` | Credit-spending jobs; return a `run_id` to poll with `get_run` |

Every write takes `dry_run: true` first. When `get_agent_briefing` reports
`account_settings.write_confirmation_required: true`, commit with `confirm: true` after the
user approves the preview. Send `basis` (provenance) on every write. This plugin only reads
the kit; it never writes to it on its own.
