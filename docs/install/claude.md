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

When prompted (driven by `userConfig` in the plugin manifest), choose the **default publish
mode**: `draft` (recommended), `published`, or `scheduled`. There is no API key to paste.

Then **restart Claude** and sign in to both services the first time Claude asks. In Claude Code,
run `/mcp`, select `brand-kit-os` and choose **Authenticate** (then the same for `leafpad`); in
Claude Desktop or Cowork, click **Connect** when prompted. Any Brand Kit OS plan works, including
free. Verify with: *"What brands do I have?"* (runs `list_brand_kits`).

## Option B — Manual upload (Claude Desktop / Cowork)

Download the `plugins/brand-kit-os-leafpad` folder and upload it via
**Cowork → Customize → Browse plugins → Upload plugin**. You'll be prompted for the same two
config value (publish mode).

## What you get

- **Commands:** `/brand-kit-os-leafpad:setup`, `/brand-kit-os-leafpad:publish-pipeline`,
  `/brand-kit-os-leafpad:create-content`, `/brand-kit-os-leafpad:enforce-voice`.
- **Session hook:** auto-loads your brand summary at session start.
- **Skills + agents:** brand-context loading, voice enforcement, content generation, SEO, QA,
  Leafpad publishing.

## How the MCP servers are configured

The plugin's [`.mcp.json`](../../plugins/brand-kit-os-leafpad/.mcp.json) declares both servers;
Claude handles the OAuth sign-in for both natively. No API key and no `mcp-remote` bridge is
needed.

```json
{
  "mcpServers": {
    "brand-kit-os": { "type": "http", "url": "https://www.brandkitos.com/mcp" },
    "leafpad": { "type": "http", "url": "https://leafpad.io/mcp" }
  }
}
```

### Adding just the servers (without the plugin), Claude Code CLI

```bash
claude mcp add --transport http brand-kit-os https://www.brandkitos.com/mcp
claude mcp add --transport http leafpad https://leafpad.io/mcp
```

Then run `/mcp` and choose **Authenticate** for each. To use an API key instead (scripts or
automation), add `--header "Authorization: Bearer $BRAND_KIT_API_KEY"` to the first command.

## Troubleshooting

- **`401` from Brand Kit OS:** the connection is not signed in yet. Run `/mcp`, select
  `brand-kit-os` and choose **Authenticate** (Claude Desktop or Cowork: click **Connect**). If you
  added the server with an API key header, a rejected key does not fall back to sign-in: check
  the key, or remove the server and add it again without the header.
- **`403` from Brand Kit OS:** this is not a plan limit; every plan can connect. Contact
  Brand Kit OS support.
- **No brand summary at startup:** confirm the `brand-kit-os` server shows connected and
  signed in; re-run `/brand-kit-os-leafpad:setup`.
