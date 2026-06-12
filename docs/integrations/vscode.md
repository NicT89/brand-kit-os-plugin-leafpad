# VS Code

VS Code supports MCP servers through GitHub Copilot's agent mode (and compatible extensions). You get the two MCP servers and can drive the workflow with prompts; the Claude Code plugin's slash commands and hooks don't carry over, but the agents work as reusable prompts.

## Configure MCP servers

Add to your MCP config (e.g. `.vscode/mcp.json` or the extension's settings). VS Code uses a `servers` key and a `type` field:

```json
{
  "servers": {
    "brand-kit-os": {
      "type": "http",
      "url": "https://www.brandkitos.com/mcp",
      "headers": { "Authorization": "Bearer YOUR_BKOS_API_KEY" }
    },
    "leafpad": {
      "type": "http",
      "url": "https://leafpad.io/mcp"
    }
  }
}
```

Reload the window. Complete Leafpad OAuth in the browser on first use.

## Run the workflow

There are no slash commands here. Instead, paste the workflow as a prompt. The simplest full-pipeline equivalent:

```
Using the brand-kit-os and leafpad MCP tools, write and publish a brand-aligned
blog post about "<topic>":
1. Load brand context: get_brand_kit_expression, get_brand_kit_governance,
   get_brand_kit_audience, get_brand_kit_products, get_brand_kit_core.
2. Research the topic with leafpad_get_company_data.
3. Draft an 800–1400 word article in the brand voice, as HTML.
4. Add 2–4 verified outbound citations (only sources you actually fetch and confirm).
5. Build SEO metadata and call leafpad_generate_image for a feature image.
6. Check it against the brand's governance and voice rules.
7. Publish with leafpad_create_post (published: false for a draft).
Report the draft URL and what brand rules you applied.
```

For higher fidelity, paste the relevant agent file (e.g. `agents/content-generation.md`) as a system/context prompt and let the model follow it.

## What you don't get in VS Code

- The `/brand-kit-os-leafpad:*` slash commands (use prompts instead)
- The SessionStart brand-summary hook
- `userConfig` key prompting (put the key directly in the MCP config)

The MCP tools themselves are identical, so output quality is the same when you give the model the same instructions.
