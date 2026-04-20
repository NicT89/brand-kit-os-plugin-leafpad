# Brand Kit OS — Data Model Reference

This document describes the data structure returned by Brand Kit OS MCP tools.

## Brand Kit Sections

### Summary (`get_brand_kit_summary`)
A compact overview (~500 tokens) containing:
- Brand name and tagline
- Top personality traits
- Primary tone dimensions
- Key constraints
- Product/service count

### Core (`get_brand_kit_core`)
- **Mission** — The brand's purpose
- **Vision** — The brand's aspirational future state
- **Brand Story** — Narrative arc of the brand (JSONB with structured content)
- **Brand Promises** — Commitments the brand makes to its audience
- **Taglines** — Array of brand taglines and slogans

### Personality (`get_brand_kit_personality`)
- **Personality Traits** — Human characteristics attributed to the brand
- **Brand Values** — Core values that guide decision-making
- **Brand Principles** — Actionable rules derived from values
- **Brand Moods** — Emotional tones associated with the brand

### Expression (`get_brand_kit_expression`)
- **Tone of Voice** — How the brand sounds
- **Tone Dimensions** — Scales (e.g., formal ↔ casual)
- **Voice Archetypes** — Archetypal voice patterns
- **Verbal Style** — JSONB object with keys: `sentence_structure`, `vocabulary_level`, `punctuation_style`, and other language pattern preferences
- **Visual Style** — JSONB object describing visual identity guidelines
- **Preferred Terminology** — Words the brand uses (and avoids)
- **Content Categories** — Platform-specific content guidance

### Products (`get_brand_kit_products`)
Array of products/services, each with:
- Name, description, type
- Key benefits, USP, competitive differentiation
- Cost and special pricing

### Audience (`get_brand_kit_audience`)
Array of target audience personas, each with:
- Demographics, goals, pain points
- Buying behavior, preferred channels
- Content that resonates
- Core motivation
- Representative quote
- Professional context, personal background
- Expertise level, platform behavior

### Governance (`get_brand_kit_governance`)
- **Behavioral Constraints** — What the brand must/must not do
- **Negative Directory** — Blacklisted words, phrases, topics
- **Compliance Notes** — Regulatory requirements (free text)
- **Compliance Selections** — Array of selected compliance standards (GDPR, CCPA, etc.)
- **Disclosure Policy** — AI and legal disclaimers (free text)
- **Disclosure Statements** — Structured JSONB with `creation`, `transparency`, and `deployment` statement objects, each containing questions, answers, and approval status
- **Writing Constraints** — Structured JSONB object with keys like `max_sentence_length`, `active_voice_preference`, `readability_target`, formatting and structural rules
- **Usage Guidelines** — How brand assets should be used
- **Approval Workflows** — Content approval process configurations
- **Drift Prevention Prompts** — Prompts to keep AI outputs on-brand

### Personas (`get_brand_kit_personas`)
AI persona configurations for different use cases (e.g., customer support bot, social media manager). Each includes:
- Name, purpose type, role definition
- Tasks, behavioral rules, tone overrides
- Voice profile, lexicon/syntax preferences
- Safety compliance, negative guardrails
- Execution protocol, interaction context

### Competitors
Array of competitor brands, each with:
- Name, URL, description, tagline
- Brand colors, fonts, typography
- Brand personality, value propositions
- Social profiles, design framework
- Logo URL

### SEO
- **Keywords** — Target SEO keywords
- **Tags** — Content tags
- **Suggested Keywords** — AI-suggested keywords

### Social Profiles
Connected social media account URLs and metadata stored in `brand_kit_social_urls` (JSONB on `brand_kits` table).

### Logo Assets
Array of logo variants, each with:
- Asset key, label, URL/storage path
- Description, usage guidelines
- File type, dimensions, size
- Default flag, sort order

### Knowledge Files (`list_knowledge_files`, `get_knowledge_file`)
Supplementary documents attached to a brand kit (style guides, playbooks, etc.). Linked via `brand_kit_knowledge_files` to `library_knowledge_files`.
