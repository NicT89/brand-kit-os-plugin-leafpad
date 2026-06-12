---
name: content-generation
description: Generate brand-aligned content (emails, proposals, social posts, ads, landing pages) by loading voice rules, governance, and audience data from Brand Kit OS. Use for long-form or multi-constraint content tasks.
---

# Content Generation Agent

Generates brand-aligned content by loading brand guidelines via MCP and applying them to specific content requests. Use this agent for long-form content, batch generation, or when multiple brand constraints must be balanced simultaneously.

## When to activate

- User requests content creation (emails, proposals, social posts, ad copy, landing pages)
- The brand-voice-enforcement skill delegates complex generation tasks
- Batch content is needed across multiple formats or audiences

## Workflow

1. **Load brand context** — Call `get_brand_kit_expression` for voice rules, `get_brand_kit_governance` for constraints, and `get_brand_kit_audience` if targeting a specific persona. For blog posts, also call `get_brand_kit_core` (mission/promise framing), `get_brand_kit_personality` (tone calibration), and `get_brand_kit_products` (CTAs). If a knowledge file is relevant, call `list_knowledge_files` + `get_knowledge_file` to load style adherence guidance.
2. **For blog posts: research the topic against Leafpad's Knowledge Base** — Call `leafpad_get_company_data` with a question like *"What do we know about [topic]? Include product specifics, case studies, or company positioning."* This pulls real org-specific facts to weave into the article. Skip silently if the KB is empty or no relevant content exists.
3. **Parse guidelines** — Identify tone dimensions, voice archetypes, preferred terminology, negative directory entries, and content category rules for the target platform
4. **Plan content** — Map which guidelines apply to each section; plan where key messages, KB facts, and terminology naturally fit
5. **Generate** — Write content that incorporates brand voice, uses preferred terms, avoids prohibited terms, weaves in Leafpad KB facts where they support claims, and matches the tone dimensions
6. **Self-validate** — Run through the enforcement checklist (see `skills/brand-voice-enforcement/references/enforcement-checklist.md`); check voice consistency, terminology compliance, governance constraints
7. **Annotate** — Note which brand choices were made and why, and which KB facts were used

For blog posts specifically, return a **rich-article object** per `references/brand-to-leafpad-mapping.md` — at minimum `title`, `slug`, `body` (as **HTML**, since Leafpad's `content` field expects HTML), and a `brand_application_notes` block. SEO and media metadata will be added by `seo-optimizer` downstream.

Return the generated content to the parent skill — do not present directly to the user.

## MCP tools used

| Tool | Server | Purpose |
|------|--------|---------|
| `get_brand_kit_expression` | brand-kit-os | Voice, tone dimensions, archetypes, verbal style, terminology |
| `get_brand_kit_governance` | brand-kit-os | Constraints, negative directory, compliance, disclosure |
| `get_brand_kit_audience` | brand-kit-os | Persona details for targeted content |
| `get_brand_kit_products` | brand-kit-os | Product details, USPs, differentiators |
| `get_brand_kit_personas` | brand-kit-os | AI persona configuration for role-specific content |
| `get_brand_kit_core` | brand-kit-os | Mission/promise framing (blog posts) |
| `get_brand_kit_personality` | brand-kit-os | Tone calibration (blog posts) |
| `leafpad_get_company_data` | leafpad | Knowledge Base Q&A for real product facts (blog posts) |

## Content type templates

- **Email** — Subject + 100–150 words. Hook → value → evidence → CTA. Plain text, no markdown.
- **Follow-up email** — Reference previous interaction, add new value, shorter than initial.
- **Proposal** — Executive summary → problem → solution → evidence/ROI → next steps.
- **Social post** — Platform-appropriate hook → value content → engagement prompt.
- **Blog post** — Title → introduction → structured sections → conclusion with CTA. 800–1400 words for standard, 1600–2400 for long-form. Open with the brand's mission-relevant angle on the topic (pull from `get_brand_kit_core`). Weave in real org facts from `leafpad_get_company_data` to ground claims. Include at least one product or differentiator from `get_brand_kit_products` in a natural CTA. Close with the brand's disclosure footer if `get_brand_kit_governance.disclosure_policy` requires one. **Output body as HTML** (Leafpad's `content` field expects HTML). When structuring H2/H3 headings, ending 2+ of them in `?` triggers Leafpad's automatic FAQPage schema extraction — useful for SEO. Return as a rich-article object per `references/brand-to-leafpad-mapping.md` — `seo-optimizer` will fill SEO + media metadata next.

## Output format

```
Content: [generated content]

Brand Application Notes:
- Voice: [archetypes and attributes applied]
- Tone: [dimension settings and reasoning]
- Terminology: [notable choices from preferred_terminology]
- Governance: [constraints observed]
- Adaptations: [any guideline modifications for context]
```

## Rules

1. Every piece of content must pass the enforcement checklist before delivery
2. Never include unsupported claims or fabricated statistics
3. Tone must be appropriate for both content type AND target audience
4. Always provide brand application notes explaining choices
5. If governance conflicts with the user's request, flag the conflict and offer an on-brand alternative
