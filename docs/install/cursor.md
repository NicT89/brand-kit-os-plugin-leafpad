# Cursor

Cursor can't run the Claude plugin, but it fully supports **remote MCP servers** (with custom
headers and OAuth) and reproduces the intelligence through **`.cursor/rules`**.

## 1. Connect the MCP servers

Create `.cursor/mcp.json` in your project (or `~/.cursor/mcp.json` for all projects). Cursor
resolves `${env:VAR}` in `url`, `headers`, `command`, `args`, and `env`.

```json
{
  "mcpServers": {
    "brand-kit-os": {
      "url": "https://www.brandkitos.com/mcp",
      "headers": { "Authorization": "Bearer ${env:BRAND_KIT_API_KEY}" }
    },
    "leafpad": {
      "url": "https://leafpad.io/mcp"
    }
  }
}
```

- Set `BRAND_KIT_API_KEY` in your environment — **do not** hardcode the key in a committed file.
- **Leafpad** uses OAuth: when you first invoke a Leafpad tool, Cursor opens a browser to sign
  in, then caches the token. (For an OAuth server you may also add an `auth` object with
  `CLIENT_ID`/`scopes`, but the default browser flow is enough here.)
- Enable both servers in **Cursor → Settings → MCP** and confirm they show green/connected.

## 2. Port the intelligence (rules)

This repo ships [`.cursor/rules/brand-kit-os-leafpad.mdc`](../../.cursor/rules/brand-kit-os-leafpad.mdc) —
copy it into your project's `.cursor/rules/`. It carries the brand-voice enforcement rules and
the publish-pipeline workflow so Cursor's agent behaves like the Claude plugin. It's derived
from [`AGENTS.md`](../../AGENTS.md); keep them in sync.

## 3. Verify

Ask Cursor's agent: *"List my brand kits and my Leafpad organizations."* It should call
`list_brand_kits` and `leafpad_list_organizations`.

## Troubleshooting

- **Headers ignored / 401** — make sure `BRAND_KIT_API_KEY` is exported in the environment
  Cursor launched from; restart Cursor after editing `mcp.json`.
- **`403` from Brand Kit OS** — host allowlist; the key is fine. Contact Brand Kit OS to
  allowlist Cursor.
- **Transport issues** — you can append `/stream`, `/sse`, or `/stateless` to a remote MCP URL
  to force a transport mode if the default negotiation fails.
