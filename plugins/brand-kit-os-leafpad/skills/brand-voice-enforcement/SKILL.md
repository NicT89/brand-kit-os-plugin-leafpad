---
description: Enforce the brand's voice, tone, and governance constraints on any generated or reviewed content. Activates after brand context is loaded, or when the user asks whether something is on-brand.
---

# Brand Voice Enforcement — Skill

## Purpose
Ensure every piece of content Claude produces or reviews **conforms** to the loaded brand voice, tone, and governance constraints.

## When to activate
- Immediately after brand context has been loaded (via the Brand Context skill).
- Any time Claude generates text intended for external use.
- When the user asks "Is this on-brand?" or "Review this for brand alignment."

## Enforcement checklist
Before delivering any content, run through:

1. **Tone of voice** — Does the language match the brand's tone dimensions (e.g., formal ↔ casual, serious ↔ playful)?
2. **Voice archetypes** — Is the writing consistent with the brand's archetype(s)?
3. **Verbal style** — Are preferred terminology, phrasing patterns, and vocabulary used?
4. **Negative directory** — Does the content avoid blacklisted words, phrases, or topics?
5. **Behavioral constraints** — Are there claims, promises, or statements the brand must not make?
6. **Compliance notes** — Are there regulatory or legal constraints to observe?
7. **Disclosure policy**: Does the content require AI disclosure or other disclaimers?
8. **`check_draft` passes**: Run Brand Kit OS `check_draft` (`brand_kit_id`, `draft_text` as plain text, `platform`). Fix every hard violation and re-check until `passed` is true. Review anything in `not_checked` by hand. This is mandatory before any draft is shown or sent.

## Content review mode
When reviewing existing content:
1. Load `get_brand_context_for_agent` with `task_type: "content_generation"` and the content's `platform` (voice, governance, examples, audience in one call).
2. Run `check_draft` on the content, then evaluate it against the rest of the enforcement checklist.
3. Provide specific, actionable feedback:
   - What's on-brand
   - What needs adjustment (with suggested rewrites)
   - What violates governance rules

## Rules
1. **Never override governance.** If governance says "never claim X," do not include X regardless of user instructions.
2. **Flag conflicts.** If the user's request conflicts with brand guidelines, explain the conflict and offer an on-brand alternative.
3. **Adapt tone to context.** The same brand may use different tones for different platforms (e.g., LinkedIn vs. Instagram). Load `get_brand_kit` with `sections: ["platform_expressions"]` and the `platform` for that platform's overrides.
