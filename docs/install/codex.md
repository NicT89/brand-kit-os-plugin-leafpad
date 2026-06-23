# OpenAI Codex CLI

Codex supports remote (Streamable HTTP) MCP servers via `config.toml`, and reproduces the
intelligence through **`AGENTS.md`**. Two important limits shape the setup:

- Remote HTTP MCP requires the experimental RMCP client: `experimental_use_rmcp_client = true`.
- Codex supports **bearer-token** auth for HTTP MCP, but **not the full OAuth flow yet**. So
  Brand Kit OS (bearer) connects directly; **Leafpad (OAuth) needs an `mcp-remote` bridge**.

## 1. Connect Brand Kit OS (direct, bearer token)

Edit `~/.codex/config.toml` (global) or `.codex/config.toml` in a trusted project:

```toml
experimental_use_rmcp_client = true

[mcp_servers.brand-kit-os]
url = "https://www.brandkitos.com/mcp"
bearer_token_env_var = "BRAND_KIT_API_KEY"
```

Export the key before launching Codex:

```bash
export BRAND_KIT_API_KEY="sk-..."
```

> Don't mix stdio and HTTP fields in one entry (e.g. `command` + `bearer_token`) — Codex's
> config parser rejects that.

## 2. Connect Leafpad (OAuth, via mcp-remote bridge)

Because Codex can't do the OAuth handshake itself, wrap Leafpad in the `mcp-remote` stdio
bridge, which runs the browser OAuth flow and caches the token:

```toml
[mcp_servers.leafpad]
command = "npx"
args = ["-y", "mcp-remote", "https://leafpad.io/mcp"]
```

The first run opens a browser to sign in to Leafpad. (Requires Node.js/`npx`.) When Codex adds
full MCP OAuth support, you can replace this with a plain `url = "https://leafpad.io/mcp"` entry.

## 3. Port the intelligence (AGENTS.md)

Copy this repo's [`AGENTS.md`](../../AGENTS.md) into your project root (Codex reads `AGENTS.md`
automatically). It carries the brand-voice rules, the publish pipeline, and the Leafpad field
mapping.

## 4. Verify

In Codex, ask: *"List my brand kits, then list my Leafpad organizations."*

## Troubleshooting

- **Brand Kit OS tools don't appear** — confirm `experimental_use_rmcp_client = true` is set and
  `BRAND_KIT_API_KEY` is exported; restart Codex.
- **`403` from Brand Kit OS** — host allowlist, not the key. Contact Brand Kit OS to allowlist
  Codex.
- **Leafpad bridge fails** — ensure Node.js is installed; run
  `npx -y mcp-remote https://leafpad.io/mcp` once in a terminal to complete OAuth, then retry.
