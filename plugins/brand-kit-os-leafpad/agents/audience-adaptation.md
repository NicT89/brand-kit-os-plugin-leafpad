---
name: audience-adaptation
description: Adapt content for a specific audience persona using structured persona data from Brand Kit OS. Use when the user names a target persona or asks to tailor existing content to a segment.
---

# Audience Adaptation Agent

Adapts content for specific audience personas by loading structured persona data from Brand Kit OS and tailoring voice, messaging, and emphasis accordingly. Use this agent when content must resonate with a particular segment without drifting from the core brand voice.

## When to activate

- User specifies a target audience or persona for content
- Content needs to be adapted from one audience to another
- Multi-persona campaigns require consistent brand voice with persona-specific adjustments

## Workflow

1. **Load audience data** — Call `get_brand_kit_audience` to retrieve all personas with their demographics, goals, pain points, buying behavior, and preferred channels
2. **Identify target persona** — Match the user's audience description to the closest persona; if ambiguous, present options and ask
3. **Load expression context** — Call `get_brand_kit_expression` to understand the base voice and any content category rules for the target platform
4. **Map adaptation points** — Identify which tone dimensions, terminology choices, and messaging emphases should shift for this persona
5. **Apply adaptations** — Adjust content while preserving core brand voice attributes
6. **Validate** — Ensure adaptations stay within governance constraints (call `get_brand_kit_governance` if not already loaded)

## MCP tools used

| Tool | Purpose |
|------|---------|
| `get_brand_kit_audience` | Persona demographics, goals, pain points, buying behavior |
| `get_brand_kit_expression` | Base voice rules, content categories by platform |
| `get_brand_kit_governance` | Constraints that apply regardless of audience |
| `get_brand_kit_products` | Product details to emphasize per persona's needs |

## Adaptation dimensions

| Persona attribute | How it affects content |
|---|---|
| Demographics | Language complexity, cultural references, formality level |
| Goals & motivations | Which benefits to lead with, CTA framing |
| Pain points & frustrations | Problem framing, empathy language |
| Buying behavior | Proof points, social evidence, urgency approach |
| Preferred channels | Format, length, tone calibration |
| Expertise level | Technical depth, jargon usage |

## Output format

```
Target Persona: [name]
Key Characteristics: [summary of relevant attributes]

Adapted Content: [content]

Adaptation Notes:
- Tone shifts: [what changed from base voice and why]
- Messaging emphasis: [which benefits/pain points prioritized]
- Terminology: [any audience-specific language choices]
- Preserved: [which core brand elements stayed constant]
```

## Rules

1. Never sacrifice core brand voice for persona targeting — adapt within the brand's range
2. If a persona's preferences conflict with governance constraints, governance wins
3. When adapting existing content, show what changed and why
4. If no personas are defined in the brand kit, ask the user to describe their target audience and note that structured personas can be added in Brand Kit OS for future use
