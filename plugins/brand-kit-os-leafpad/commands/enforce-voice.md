---
description: Load brand guidelines from Brand Kit OS and apply them to a content request
argument-hint: <content request or existing content to refine>
---

# Enforce Voice

Load brand guidelines from Brand Kit OS and apply them to the content request provided in `$ARGUMENTS`.

## Workflow

1. **Identify the brand kit**: Call `get_agent_briefing` (no args) to list kits. If multiple kits exist, ask the user which to use.
2. **Load enforcement data**: Call `get_brand_context_for_agent` with `task_type: "content_generation"` and the target `platform`. It returns voice rules, tone dimensions, archetypes, terminology, governance constraints, the negative directory and examples in one call.
3. **Analyze the request** — Determine content type, target audience, platform, and key messages from the user's input.
4. **Load audience context** (if applicable): If the request targets a specific persona, use the bundle's audience block (or `get_brand_kit` with `sections: ["audience"]`) and delegate to the audience-adaptation agent.
5. **Generate content** — Apply voice constants (archetypes, verbal style) and calibrate tone dimensions for the content type and platform. Delegate to the content-generation agent for complex or long-form requests.
6. **Validate**: Run `check_draft` on the output (plain text, target `platform`); fix every hard violation and re-check until `passed` is true. Then run the quality-assurance agent against the enforcement checklist before presenting.
7. **Present** — Deliver the content with a brief explanation of brand choices made. Note any governance constraints that shaped the output.
8. **Offer refinement** — Ask if the user wants adjustments, alternative approaches, or adaptation for a different audience.

## When no brand kit is found

If `get_agent_briefing` lists no kits, inform the user:
> "No brand kits found. Create a brand kit at brandkitos.com to use voice enforcement."

## Rules

1. Always load governance data — never skip constraints even for simple requests
2. If the user's request conflicts with governance guidelines, explain the conflict and offer an on-brand alternative
3. Reference specific brand guidelines when explaining content choices (e.g., "Per your tone dimensions, I kept this formal…")
4. For platform-specific rules, call `get_brand_kit` with `sections: ["platform_expressions"]` and the `platform` before generating

To publish the result to Leafpad, run `/brand-kit-os-leafpad:publish-pipeline`.
