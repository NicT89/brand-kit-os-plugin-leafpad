# Installing on each platform

This plugin ships two things:

1. **Two remote MCP servers** — Brand Kit OS (brand context) and Leafpad (blog publishing).
   These connect to **any MCP-capable host**.
2. **The "intelligence"** — brand-voice enforcement + the publish pipeline. On **Claude** this
   is a native plugin (skills/agents/commands/hooks). On every other host it is reproduced as
   that platform's native instructions file (Cursor rules, `AGENTS.md`, `GEMINI.md`, or a
   pasted custom-instructions block).

## The two servers

| Server | Endpoint | Transport | Auth |
|---|---|---|---|
| Brand Kit OS | `https://www.brandkitos.com/mcp` | Streamable HTTP | `Authorization: Bearer <BRAND_KIT_API_KEY>` |
| Leafpad | `https://leafpad.io/mcp` | Streamable HTTP | OAuth (browser sign-in on first connect) |

**Get your Brand Kit OS API key:** <https://brandkitos.com/settings> → API Keys (requires a
Base or Premium plan). **Leafpad** needs no key — you sign in via the browser on first use.

## Compatibility matrix

| Platform | Runs the full plugin? | Brand Kit OS (Bearer) | Leafpad (OAuth) | Intelligence ported as | Guide |
|---|---|---|---|---|---|
| **Claude** (Code + Desktop/Cowork) | ✅ Yes — native | ✅ Native | ✅ Native | The plugin itself | [claude.md](claude.md) |
| **Cursor** | ❌ (MCP + rules) | ✅ `headers` | ✅ Native OAuth | `.cursor/rules/*.mdc` | [cursor.md](cursor.md) |
| **OpenAI Codex CLI** | ❌ (MCP + AGENTS.md) | ✅ `bearer_token` | ⚠️ via `mcp-remote` bridge | `AGENTS.md` | [codex.md](codex.md) |
| **ChatGPT** (Developer Mode) | ❌ (connectors) | ✅ API-key connector | ✅ OAuth connector | Custom GPT / Project instructions | [chatgpt.md](chatgpt.md) |
| **Google Gemini CLI** | ❌ (MCP + GEMINI.md) | ✅ `headers` | ✅ OAuth | `GEMINI.md` | [gemini.md](gemini.md) |
| **Manus** | ❌ (MCP integration) | ✅ URL + key | ✅ OAuth/key | Manus instructions/knowledge | [manus.md](manus.md) |
| **Perplexity** (Pro/Max/Enterprise) | ❌ (connectors) | ✅ API-key connector | ✅ OAuth connector | Space custom instructions | [perplexity.md](perplexity.md) |

## Two caveats that apply everywhere

- **Brand Kit OS host allowlist.** Brand Kit OS may reject (`403`) connections from a host that
  isn't on its allowlist. If a 403 appears with a valid key, the *platform* needs allowlisting
  on the Brand Kit OS side — not a new key.
- **Leafpad OAuth support varies.** Most hosts handle MCP OAuth natively. **Codex** does not yet
  support the full OAuth flow, so Leafpad there is reached through an `mcp-remote` stdio bridge
  (see [codex.md](codex.md)). Brand Kit OS (static bearer token) needs no bridge anywhere.

## Letting the agent set it up for you

You don't have to read these docs. Ask your agent to **"set up the Brand Kit OS + Leafpad
plugin"** and it will run the setup interview defined in
[`../setup/setup-spec.json`](../setup/setup-spec.json) — detect your platform, ask for your API
key and default publish mode, write the right config, and verify the connection. On Claude, run
`/brand-kit-os-leafpad:setup`.
