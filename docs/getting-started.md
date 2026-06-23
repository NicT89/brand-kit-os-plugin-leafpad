# Getting Started

A step-by-step guide to go from zero to a published, brand-aligned blog post — and then to a self-running content calendar.

## 1. What this plugin does

It connects two systems to Claude:

- **Brand Kit OS** — your brand's voice, audience, products, and governance rules
- **Leafpad** — your blog/website publishing platform

With both connected, Claude can research topics, write on-brand articles grounded in your real product data, optimize them for SEO, add verified citations, and publish them to Leafpad — as drafts, live posts, or AI-scheduled future posts.

## 2. Prerequisites

1. A **Brand Kit OS** account (Base or Premium) with at least one brand kit filled in. Get an API key at [brandkitos.com/settings](https://brandkitos.com/settings).
2. A **Leafpad** account with at least one organization.
3. **Claude** — either Claude Desktop (with Cowork) or Claude Code.

## 3. Install

### In Claude Desktop / Cowork (recommended for most users)

Add both MCP servers to your Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "brand-kit-os": {
      "url": "https://www.brandkitos.com/mcp",
      "headers": { "Authorization": "Bearer YOUR_BKOS_API_KEY" }
    },
    "leafpad": {
      "url": "https://leafpad.io/mcp"
    }
  }
}
```

Then install the plugin via Cowork → Customize → Browse plugins, or the marketplace command in Claude:

```
/plugin marketplace add https://github.com/NicT89/brand-kit-os-plugin-leafpad
/plugin install brand-kit-os-leafpad@brand-kit-os-leafpad
```

When prompted, paste your Brand Kit OS API key and choose a default `publish_mode` (`draft` is safest to start).

**Fully quit and reopen Claude Desktop.** On first use of Leafpad, a browser window opens for OAuth — sign in and approve.

### In Claude Code

Same marketplace commands. The plugin's bundled `.mcp.json` configures both servers; you'll be prompted for the API key at install.

> Detailed, copy-paste setup and a full test script: [`docs/testing/claude-desktop-test-protocol.md`](testing/claude-desktop-test-protocol.md).

## 4. Verify everything works

Run the built-in health check:

```
/brand-kit-os-leafpad:doctor
```

It checks both connections, lists your brand kits and Leafpad orgs, inspects your brand kit's completeness, and tells you exactly what to fix if anything's off. Green across the board means you're ready.

## 5. Publish your first post

```
/brand-kit-os-leafpad:publish-pipeline How to choose a brand voice for B2B SaaS --draft
```

This will:
1. Load your full brand context
2. Research the topic against your Leafpad Knowledge Base
3. Draft the article in your brand voice (as HTML)
4. Add 2–4 verified citations
5. Generate a brand-aligned feature image
6. Build SEO metadata + internal links
7. Run a brand-compliance QA pass
8. Save it as a **draft** in Leafpad

Open the draft in Leafpad, review it, and publish when happy. Once you trust the output, swap `--draft` for `--publish` to go live in one step.

No topic in mind? Just run:

```
/brand-kit-os-leafpad:publish-pipeline
```

The research agent (`topic-scout`) will propose on-brand ideas and let you pick.

## 6. Set up topic research (optional but powerful)

The more the plugin knows about your trusted sources, the better its topic ideas. Create a **sources registry**:

```
Help me set up my content sources registry.
```

Claude will walk you through adding RSS feeds, citation domains, keyword themes, and your posting cadence, then save it to `~/.brand-kit-os-leafpad/registry.json`. See the **topic-sourcing** skill and [`registry.example.json`](../plugins/brand-kit-os-leafpad/skills/topic-sourcing/references/registry.example.json) for the shape.

## 7. Plan a week of content

```
/brand-kit-os-leafpad:plan-week --count 3
```

The research agent proposes 3 brand-relevant topics (from your sources, company updates, content gaps, and trends), assigns publish slots, and saves a calendar. Then:

```
/brand-kit-os-leafpad:execute-calendar
```

…schedules each one via Leafpad's AI scheduler — or use `--draft-now` to hand-craft all three immediately as drafts.

## 8. Make it recurring

To have Claude build and schedule a content calendar automatically (e.g., every Monday at 8am), see [`docs/routines/weekly-3-articles.md`](routines/weekly-3-articles.md).

## 9. Supercharge Leafpad's own AI (optional)

Push your brand context into Leafpad's Knowledge Base so **every** Leafpad-generated post is brand-aware:

```
/brand-kit-os-leafpad:sync-brand-to-kb --dry-run
```

Review what would be uploaded, then run it for real.

## Command cheat sheet

| Command | What it does |
|---|---|
| `/brand-kit-os-leafpad:doctor` | Health check + setup punch list |
| `/brand-kit-os-leafpad:publish-pipeline <topic> [--draft\|--publish]` | Research → draft → cite → SEO → QA → publish |
| `/brand-kit-os-leafpad:ai-schedule "<title>" <iso>` | Schedule a Leafpad-AI-generated future post |
| `/brand-kit-os-leafpad:plan-week [--count N]` | Research + build a content calendar |
| `/brand-kit-os-leafpad:execute-calendar [--ai-schedule\|--draft-now]` | Schedule/draft a planned calendar |
| `/brand-kit-os-leafpad:sync-brand-to-kb` | Push brand context into Leafpad's KB |
| `/brand-kit-os-leafpad:create-content <type> for <audience> about <topic>` | Generate any content type (not just blog) |
| `/brand-kit-os-leafpad:enforce-voice <content>` | Apply brand voice to a request or existing text |

## Troubleshooting

- **A command says no brand kit found** — run `/brand-kit-os-leafpad:doctor`; usually the API key or kit setup.
- **Leafpad asks for auth repeatedly** — fully quit and reopen Claude Desktop to complete OAuth.
- **Topic ideas feel generic** — set up the sources registry (step 6) and sync brand to KB (step 9).
- **Feature image didn't generate** — Leafpad may auto-generate one on publish; check the draft in the UI.
- For anything else, `/brand-kit-os-leafpad:doctor` is the fastest diagnosis.
