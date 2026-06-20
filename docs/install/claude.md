# Claude (Code + Desktop / Cowork)

Claude is the only host that runs the **full plugin** — skills, agents, slash-commands, and the
session hook — alongside the two MCP servers. Everything is wired through Claude's plugin
installer, so you normally don't touch config files by hand.

## Option A — Marketplace install (recommended)

In Claude Code or Claude Desktop (Cowork):

```
/plugin marketplace add https://github.com/NicT89/brand-kit-os-plugin-leafpad
/plugin install brand-kit-os-leafpad@brand-kit-os-leafpad
```

When prompted (driven by `userConfig` in the plugin manifest):

1. **Brand Kit OS API key** — paste it (stored as a secret; from
   <https://brandkitos.com/settings> → API Keys).
2. **Default publish mode** — `draft` (recommended), `published`, or `scheduled`.

Then **restart Claude**. Verify with: *"What brands do I have?"* (runs `list_brand_kits`). The
first Leafpad action opens a browser for OAuth; the token is cached afterward.

## Option B — Manual upload (Claude Desktop / Cowork)

Download the `plugins/brand-kit-os-leafpad` folder and upload it via
**Cowork → Customize → Browse plugins → Upload plugin**. You'll be prompted for the same two
config values.

## What you get

- **Commands:** `/brand-kit-os-leafpad:setup`, `/brand-kit-os-leafpad:publish-pipeline`,
  `/brand-kit-os-leafpad:create-content`, `/brand-kit-os-leafpad:enforce-voice`.
- **Session hook:** auto-loads your brand summary at session start.
- **Skills + agents:** brand-context loading, voice enforcement, content generation, SEO, QA,
  Leafpad publishing.

## How the MCP servers are configured

The plugin's [`.mcp.json`](../../plugins/brand-kit-os-leafpad/.mcp.json) declares both servers;
Claude's runtime resolves the API key from your `userConfig` and handles Leafpad's OAuth
natively. No `mcp-remote` bridge is needed.

```json
{
  "mcpServers": {
    "brand-kit-os": {
      "url": "https://www.brandkitos.com/mcp",
      "headers": { "Authorization": "Bearer ${user_config.brand_kit_api_key}" }
    },
    "leafpad": { "url": "https://leafpad.io/mcp" }
  }
}
```

### Adding just the servers (without the plugin), Claude Code CLI

```bash
claude mcp add --transport http brand-kit-os https://www.brandkitos.com/mcp \
  --header "Authorization: Bearer $BRAND_KIT_API_KEY"
claude mcp add --transport http leafpad https://leafpad.io/mcp
```

## Troubleshooting

- **`403` from Brand Kit OS** — your key is valid but this client isn't allowlisted. Sandboxed
  Claude Code environments can be blocked; Claude Desktop is typically allowlisted. Contact
  Brand Kit OS to allowlist the host.
- **No brand summary at startup** — confirm the API key was saved and the `brand-kit-os` server
  shows connected; re-run `/brand-kit-os-leafpad:setup`.
