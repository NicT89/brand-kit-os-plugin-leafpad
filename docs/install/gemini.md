# Google Gemini CLI

Gemini CLI supports remote MCP servers (Streamable HTTP and SSE) with custom headers and OAuth,
configured in `settings.json`, and reproduces the intelligence through **`GEMINI.md`**.

## 1. Connect the MCP servers

Edit `~/.gemini/settings.json` (global) or `.gemini/settings.json` in your project. Gemini picks
the transport from the field used: `httpUrl` → Streamable HTTP, `url` → SSE, `command` → stdio.

```json
{
  "mcpServers": {
    "brand-kit-os": {
      "httpUrl": "https://www.brandkitos.com/mcp",
      "headers": { "Authorization": "Bearer ${BRAND_KIT_API_KEY}" },
      "timeout": 10000
    },
    "leafpad": {
      "httpUrl": "https://leafpad.io/mcp"
    }
  }
}
```

- Export `BRAND_KIT_API_KEY` in your shell — Gemini expands environment variables; don't
  hardcode the key.
- **Leafpad** uses OAuth; the first Leafpad call triggers the browser sign-in, then caches the
  token.

## 2. Port the intelligence (GEMINI.md)

Copy this repo's [`GEMINI.md`](../../GEMINI.md) into your project root (Gemini reads it as
context). It mirrors the brand-voice rules and publish pipeline from
[`AGENTS.md`](../../AGENTS.md).

## 3. Verify

Ask Gemini: *"Use the brand-kit-os and leafpad tools to list my brand kits and Leafpad
organizations."*

## Troubleshooting

- **Server not connecting** — check the JSON is valid and `BRAND_KIT_API_KEY` is exported;
  restart the CLI. Use `/mcp` in Gemini to inspect server status.
- **`403` from Brand Kit OS** — host allowlist, not the key. Contact Brand Kit OS to allowlist
  Gemini.
