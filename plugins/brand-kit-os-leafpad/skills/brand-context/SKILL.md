---
description: Load Brand Kit OS context (summary, expression, governance, audience, products) at the right level of detail for the current task. Activates when the user asks about their brand or starts any content-creation task.
---

# Brand Context — Skill

## Purpose
Guide Claude on **when** and **how** to load specific sections of a Brand Kit OS brand kit so that every response is grounded in real brand data.

## When to activate
- The user asks about their brand, voice, audience, products, or guidelines.
- The user starts a content-creation task (blog post, email, social caption, ad copy, landing page, etc.).
- The user asks Claude to review or critique existing content for brand alignment.

## Loading strategy

| User intent | Tool(s) to call | Why |
|---|---|---|
| Quick context / "What's my brand about?" | `get_brand_kit_summary` | Returns a compact overview (~500 tokens). |
| Content creation (any format) | `get_brand_kit_expression` + `get_brand_kit_governance` | Voice rules + constraints are the minimum for on-brand writing. |
| Audience-targeted content | Above + `get_brand_kit_audience` | Adds persona details for targeting. |
| Product-focused content | Above + `get_brand_kit_products` | Adds product catalog, USPs, differentiators. |
| Full brand deep-dive | `get_brand_kit` | Returns everything. Use sparingly — large payload. |
| Knowledge file reference | `list_knowledge_files` → `get_knowledge_file` | When user references a specific doc or style guide. |

## Rules
1. **Always start light.** Call `get_brand_kit_summary` first unless the task clearly needs deeper data.
2. **Layer on demand.** If the user's request expands, load the next relevant section — don't re-fetch the full kit.
3. **Cite the source.** When applying a brand rule, mention it briefly (e.g., "Per your governance guidelines…").
4. **Respect multiple kits.** If `list_brand_kits` returns more than one, ask the user which kit to use before loading data.
