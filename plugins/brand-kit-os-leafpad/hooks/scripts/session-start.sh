#!/usr/bin/env bash
# Brand Kit OS + Leafpad session-start hook.
# SessionStart hooks can only run commands, so this can't call MCP tools itself.
# It injects an instruction into context; Claude does the loading on its first turn.
# No network. Must stay cheap: it runs in every session.

set -euo pipefail

cat <<'MSG'
BRAND KIT OS + LEAFPAD: plugin active.
On the first brand- or Leafpad-related request this session, call the brand-kit-os
`get_agent_briefing` tool first (no arguments). It lists the kits you can access.
- Exactly one kit: call `get_agent_briefing` again with its `brand_kit_id` for the
  kit's health and next step, and give the user a two-sentence summary.
- Several kits: list their names and ask which one to use. Never guess a kit id.
- No kits, or the brand-kit-os tools are unavailable: continue silently.
Before writing anything for the brand, call `get_brand_context_for_agent` with
task_type "content_generation" and the target platform. Run `check_draft` on every
draft before you show it or send it anywhere, and fix every hard violation.
MSG
exit 0
