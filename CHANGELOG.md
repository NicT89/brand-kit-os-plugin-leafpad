# Changelog

## 1.3.0 — 2026-06-11

- New command `/brand-kit-os-leafpad:publish-pipeline` — end-to-end orchestrator that drafts, optimizes for SEO, runs QA, and publishes to Leafpad in one call
- New agent `seo-optimizer` — builds the `seo` block, suggests internal links from existing Leafpad posts, and proposes tags (without rewriting the body)
- New agent `leafpad-publisher` — generic publisher that encapsulates field mapping, mode dispatch, and failure handling
- New `publish_mode` userConfig (`draft` | `published` | `scheduled`, default `draft`) — controls default publishing behavior
- Per-run override flags `--draft`, `--publish`, and `--schedule <iso>` on `/publish-pipeline`
- Refactor: `cowork-digest-publisher` now delegates its publish step to `leafpad-publisher` (no behavior change for digest users)

## 1.2.0 — 2026-04-18

Initial public marketplace release.

- 2 MCP servers: Brand Kit OS and Leafpad (both via `mcp-remote`)
- 2 skills: `brand-context`, `brand-voice-enforcement`
- 5 agents: `content-generation`, `brand-review`, `audience-adaptation`, `quality-assurance`, `cowork-digest-publisher`
- 2 commands: `/brand-kit-os-leafpad:enforce-voice`, `/brand-kit-os-leafpad:create-content`
- SessionStart agent hook that auto-loads brand summary when exactly one brand kit exists
- Brand Kit OS API key prompted at install via `userConfig` and injected into `.mcp.json` via `${user_config.brand_kit_api_key}`
