# Claude Desktop / Cowork

The primary, best-supported host. The full plugin (agents, commands, skills, hooks) works here.

## Configure MCP servers

Edit `claude_desktop_config.json`:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

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

Fully quit (Cmd-Q) and reopen. On first Leafpad use, complete the browser OAuth.

## Install the plugin

Via Cowork → Customize → Browse plugins → install `brand-kit-os-leafpad`, or:

```
/plugin marketplace add https://github.com/NicT89/brand-kit-os-plugin-leafpad
/plugin install brand-kit-os-leafpad@brand-kit-os-leafpad
```

Provide the API key and `publish_mode` when prompted.

## Verify

```
/brand-kit-os-leafpad:doctor
```

## Recurring content

Cowork's scheduled sessions are the recommended way to run the weekly/monthly routines. See [`../routines/weekly-3-articles.md`](../routines/weekly-3-articles.md).

## Notes

- The SessionStart hook auto-loads your brand summary when you open a session — Claude Desktop supports plugin hooks.
- All slash commands are available under the `/brand-kit-os-leafpad:` namespace.
