# Cursor

Cursor supports MCP servers in its settings. You get both MCP servers; the workflow runs via prompts or by pasting agent files as context.

## Configure MCP servers

Add to `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (per-project):

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

Enable both servers in Cursor → Settings → MCP. Complete Leafpad OAuth in the browser on first use.

## Run the workflow

Use Cursor's agent chat with a prompt like the one in [`vscode.md`](vscode.md#run-the-workflow), or paste an agent file from `plugins/brand-kit-os-leafpad/agents/` as context and instruct Cursor to follow it.

For repeatable use, save the pipeline prompt as a Cursor "Notepad" or project rule so it's one click away.

## What you don't get

- The `/brand-kit-os-leafpad:*` slash commands
- The SessionStart hook
- `userConfig` prompting (put the key in the MCP config)

The MCP tools are identical to other hosts.
