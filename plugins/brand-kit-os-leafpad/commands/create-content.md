---
description: Generate brand-aligned content for a specified content type, audience, and topic
argument-hint: <content type> for <audience> about <topic>
---

# Create Content

Generate brand-aligned content for a specified content type, audience, and topic using Brand Kit OS data.

## Arguments

`$ARGUMENTS` should include any combination of:
- **Content type** — email, proposal, social post, blog post, ad copy, landing page, etc.
- **Audience** — target persona or audience description
- **Topic** — subject matter, key messages, or brief

## Workflow

1. **Identify brand kit**: Call `get_agent_briefing` (no args) to list kits. If multiple kits exist, ask the user which to use. Never guess a kit id.
2. **Parse arguments** — Extract content type, audience, and topic from the user's input. If any are missing, ask before proceeding.
3. **Load relevant context**: Based on the content type:
   - Always: `get_brand_context_for_agent` with `task_type: "content_generation"` and the target `platform` (voice, governance, examples, audience and the knowledge index in one call)
   - If product-focused: `get_brand_kit` with `sections: ["products"]`
   - If persona-driven: `get_brand_kit` with `sections: ["ai_personas"]`
   - If a knowledge file's `relevance_hint` matches: `get_knowledge_file`
4. **Delegate to content-generation agent** — Pass brand context, content requirements, and audience details for generation.
5. **Adapt for audience** — If a specific persona is targeted, delegate to the audience-adaptation agent for persona-specific tuning.
6. **Validate**: Run `check_draft` on the draft (plain text, target `platform`). Fix every hard violation and re-check until `passed` is true. Then run the quality-assurance agent for the rest of the checklist. Never present a draft that has not passed `check_draft`.
7. **Present** — Deliver the content with brand application notes explaining voice, tone, and terminology choices.
8. **Offer next steps** — Suggest variations (different audience, platform, or tone), batch generation, or content review.

## When no brand kit is found

If `get_agent_briefing` lists no kits, inform the user:
> "No brand kits found. Create a brand kit at brandkitos.com to start generating brand-aligned content."

## Rules

1. Always load the `get_brand_context_for_agent` bundle before generating: voice and governance are the minimum for on-brand content
1b. Always run `check_draft` before presenting a draft
2. Layer additional data on demand — don't load the full brand kit unless explicitly needed
3. For batch requests (e.g., "5 emails for different personas"), generate each variant with persona-specific adaptation while maintaining brand consistency
4. Include brand application notes with every delivery so the user understands what guidelines shaped the output

To publish the result to Leafpad, run `/brand-kit-os-leafpad:publish-pipeline`.
