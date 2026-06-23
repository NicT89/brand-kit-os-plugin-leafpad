# Using this integration outside Claude Code

This plugin ships in Claude Code's plugin format (`.claude-plugin/`, agents, commands, hooks). But the **substance** — the brand-to-Leafpad workflow — is portable. The two MCP servers (Brand Kit OS + Leafpad) are vendor-neutral and work with any MCP-capable client. The agents and commands are just structured prompts you can reuse anywhere.

This directory explains how to run the same workflow in other hosts.

## What's portable vs Claude-specific

| Layer | Portable? | Notes |
|---|---|---|
| **MCP servers** (Brand Kit OS, Leafpad) | ✅ Fully | Standard MCP over HTTP. Any MCP client connects. |
| **Workflow logic** (the agents) | ✅ As prompts | The agent `.md` files are system prompts + tool lists. Copy them into any system that supports a system prompt + MCP tools. |
| **Rich-article schema** | ✅ | See [`schemas/rich-article.schema.json`](../../schemas/rich-article.schema.json). Vendor-neutral JSON Schema. |
| **Slash commands** | ⚠️ Re-expressible | Commands are orchestration recipes. In other hosts, paste the workflow steps as a prompt or wire them in code. |
| **SessionStart hook** | ❌ Claude Code-specific | Other hosts have their own startup mechanisms; replicate the behavior manually if wanted. |
| **`userConfig` prompts** | ❌ Claude Code-specific | Other hosts configure MCP auth their own way (see each guide). |

## The MCP config, everywhere

Every host needs the same two servers. The canonical config:

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

Some hosts use a slightly different key (`servers` vs `mcpServers`, or a `type: "http"` field). Each guide notes its exact shape.

## Per-host guides

- [`claude-desktop.md`](claude-desktop.md) — Claude Desktop / Cowork (the primary target)
- [`vscode.md`](vscode.md) — VS Code (GitHub Copilot MCP / compatible extensions)
- [`cursor.md`](cursor.md) — Cursor
- [`generic-mcp-client.md`](generic-mcp-client.md) — Any MCP client, or driving it from code with the Anthropic SDK or another LLM

## The agents as reusable prompts

Each file in `plugins/brand-kit-os-leafpad/agents/*.md` is a self-contained role:

- `topic-scout` — research + propose topics
- `content-generation` — draft the article (HTML)
- `citation-validator` — add verified outbound citations
- `seo-optimizer` — SEO metadata + feature image + internal links
- `quality-assurance` — brand-compliance gate
- `leafpad-publisher` — publish to Leafpad (draft/live)
- `leafpad-ai-scheduler` — schedule a Leafpad-AI-generated future post

To reuse in a non-Claude system: take the agent's body as the system prompt, give the model access to the MCP tools listed in that agent's "tools used" table, and feed it the inputs described. The output formats are specified in each file, so you can chain them the same way `/publish-pipeline` does.

## A note on model choice

The workflow is model-agnostic in principle, but quality depends on the model's instruction-following and tool-use. For best results use a strong, recent model (e.g. the latest Claude models). The brand-compliance and citation-verification steps in particular reward careful, capable models.
