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
2. **Parse guidelines** — Identify tone dimensions, voice archetypes, preferred terminology, negative directory entries, and content category rules for the target platform
3. **Plan content** — Map which guidelines apply to each section; plan where key messages and terminology naturally fit
4. **Generate** — Write content that incorporates brand voice, uses preferred terms, avoids prohibited terms, and matches the tone dimensions
5. **Self-validate** — Run through the enforcement checklist (see `skills/brand-voice-enforcement/references/enforcement-checklist.md`); check voice consistency, terminology compliance, governance constraints
6. **Annotate** — Note which brand choices were made and why

For blog posts specifically, return a **rich-article object** per `../references/brand-to-leafpad-mapping.md` — at minimum `title`, `slug`, `body`, and a `brand_application_notes` block. SEO and media metadata will be added by `seo-optimizer` downstream.

Return the generated content to the parent skill — do not present directly to the user.

## MCP tools used

| Tool | Purpose |
|------|---------|
| `get_brand_kit_expression` | Voice, tone dimensions, archetypes, verbal style, terminology |
| `get_brand_kit_governance` | Constraints, negative directory, compliance, disclosure |
| `get_brand_kit_audience` | Persona details for targeted content |
| `get_brand_kit_products` | Product details, USPs, differentiators |
| `get_brand_kit_personas` | AI persona configuration for role-specific content |

## Content type templates

- **Email** — Subject + 100–150 words. Hook → value → evidence → CTA. Plain text, no markdown.
- **Follow-up email** — Reference previous interaction, add new value, shorter than initial.
- **Proposal** — Executive summary → problem → solution → evidence/ROI → next steps.
- **Social post** — Platform-appropriate hook → value content → engagement prompt.
- **Blog post** — Title → introduction → structured sections → conclusion with CTA.
  - **Title: exactly 8–12 words** (hard rule). Count before returning; revise if outside the range.
  - **Body: minimum 800 words, target 900+** for standard, 1600–2400 for long-form. Under 800 fails QA — write to the target, do not pad with fluff.
  - Open with the brand's mission-relevant angle on the topic (pull from `get_brand_kit_core`). Weave at least one product or differentiator from `get_brand_kit_products` into a natural CTA. Close with the brand's disclosure footer if `get_brand_kit_governance.disclosure_policy` requires one.
  - **If research findings are provided** (from the pipeline's research step), ground claims in them and cite credible **external** sources as links (2+ where the article makes factual/data/trend claims), in addition to internal links.
  - Return as a rich-article object per `../references/brand-to-leafpad-mapping.md` — `seo-optimizer` adds SEO metadata + the image brief next.

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
