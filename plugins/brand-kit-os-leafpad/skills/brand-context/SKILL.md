---
description: Load Brand Kit OS context (briefing, content bundle, kit sections, knowledge files) at the right level of detail for the current task, and check every draft before it is shown. Activates when the user asks about their brand or starts any content-creation task.
---

# Brand Context: Skill

## Purpose
Guide Claude on **when** and **how** to load Brand Kit OS data (MCP 3.0 tool set) so that every response is grounded in real brand data, and every draft is checked against the kit's rules before anyone sees it.

## When to activate
- The user asks about their brand, voice, audience, products, or guidelines.
- The user starts a content-creation task (blog post, email, social caption, ad copy, landing page, etc.).
- The user asks Claude to review or critique existing content for brand alignment.

## Loading strategy (Brand Kit OS MCP 3.0)

| User intent | Tool call | Why |
|---|---|---|
| Session start / "Which brands do I have?" | `get_agent_briefing` (no args) | Lists accessible kits. Never guess a kit id. |
| Kit health / "What should I fix next?" | `get_agent_briefing` with `brand_kit_id` | Per-section health, next step, ranked backlog, account write settings. |
| Quick context / "What's my brand about?" | `get_brand_kit` with no `sections` | Compact summary plus `available_sections`. |
| Content creation (any format) | `get_brand_context_for_agent` with `task_type: "content_generation"` and `platform` (e.g. `blog`) | One call: voice, governance (banned terms, hard constraints), examples, audience and the knowledge-file index. The default for all writing. |
| A specific section the bundle does not cover | `get_brand_kit` with `sections: [...]` (e.g. `["products"]`, `["core", "personality"]`, `["seo"]`, `["competitors"]`, `["objections"]`, `["anti_slop_rules"]`) | Ask only for what the task needs. |
| Platform-specific voice | `get_brand_kit` with `sections: ["platform_expressions"]` and `platform` | Expression merged with that platform's overrides. |
| Knowledge file content | `get_knowledge_file` with the file id from the bundle's knowledge index (or `get_brand_kit` `sections: ["knowledge_files"]`) | Load files whose `relevance_hint` matches the task. |
| Full deep-dive | `get_brand_kit` with `sections: ["all"]` | Everything. Large; use sparingly. |
| **Before showing or sending any draft** | `check_draft` with `brand_kit_id`, `draft_text` (plain text) and `platform` | Deterministic check against anti-slop rules, negative directory and writing constraints. **Mandatory.** |

## The draft gate (mandatory)

1. Every draft goes through `check_draft` before it is shown to the user, sent to Leafpad, or handed to another agent for publishing.
2. Fix every **hard** violation, then call `check_draft` again. Repeat until `passed` is true.
3. Fix **soft** violations unless there is a stated reason not to; say what you kept and why.
4. Review the draft yourself against anything listed under `not_checked` (prose rules the checker cannot test).
5. Report the final `check_draft` result (passed, counts of hard and soft violations) with the draft.

## Rules
1. **Always start with the briefing or the bundle.** `get_agent_briefing` at session start; `get_brand_context_for_agent` before writing.
2. **Layer on demand.** If the request expands, call `get_brand_kit` for the next section only. Do not re-fetch the full kit.
3. **Cite the source.** When applying a brand rule, mention it briefly (e.g., "Per your governance guidelines...").
4. **Respect multiple kits.** If the briefing lists more than one kit, ask which to use before loading data.
5. **Writes are separate.** This plugin reads the kit; write tools (`update_brand_kit`, `manage_*`) need `dry_run: true` first and explicit user confirmation.
6. **Removed tools.** MCP 3.0 removed `get_brand_kit_summary`, `get_brand_kit_core`, `get_brand_kit_personality`, `get_brand_kit_expression`, `get_brand_kit_governance`, `get_brand_kit_audience`, `get_brand_kit_products`, `get_brand_kit_personas`, `list_knowledge_files` and `get_platform_expression`. See `references/data-model.md` for the mapping.
