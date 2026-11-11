#!/usr/bin/env bash
# Brand Kit OS + Leafpad session-start hook.
# SessionStart hooks can only run commands, so this can't call MCP tools itself.
# It injects an instruction into context; Claude does the loading on its first turn.
# No network. Must stay cheap: it runs in every session.

set -euo pipefail

cat <<'MSG'
BRAND KIT OS + LEAFPAD: plugin active.
On the first brand- or Leafpad-related request this session, call the brand-kit-os
`list_brand_kits` tool first.
- Exactly one kit: call `get_brand_kit_summary` for it and give the user a
  two-sentence summary before continuing.
- Several kits: list their names and ask which one to use.
- No kits, or the brand-kit-os tools are unavailable: continue silently.
MSG
exit 0
