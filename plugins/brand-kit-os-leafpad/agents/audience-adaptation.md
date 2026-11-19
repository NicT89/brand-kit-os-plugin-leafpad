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

1. **Load audience data**: Call `get_brand_kit` with `sections: ["audience"]` to retrieve all personas with their demographics, goals, pain points, buying behavior, and preferred channels
2. **Identify target persona** — Match the user's audience description to the closest persona; if ambiguous, present options and ask
3. **Load expression context**: Call `get_brand_context_for_agent` with `task_type: "content_generation"` and the target `platform` for the base voice, governance and examples, plus `get_brand_kit` with `sections: ["platform_expressions"]` and `platform` when that platform has overrides
4. **Map adaptation points** — Identify which tone dimensions, terminology choices, and messaging emphases should shift for this persona
5. **Apply adaptations** — Adjust content while preserving core brand voice attributes
6. **Validate**: Ensure adaptations stay within governance constraints, then run `check_draft` on the adapted text with the target `platform`. Fix every hard violation and re-check until `passed` is true before returning it

## MCP tools used

| Tool | Purpose |
|------|---------|
| `get_brand_kit` (`sections: ["audience"]`) | Persona demographics, goals, pain points, buying behavior |
| `get_brand_context_for_agent` | Base voice, governance and examples for the target platform |
| `get_brand_kit` (`sections: ["products"]`) | Product details to emphasize per persona's needs |
| `check_draft` | Mandatory check of the adapted text before it is returned |

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
