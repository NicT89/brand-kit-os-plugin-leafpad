# Proposal assets

- **`Brand-Kit-OS-x-Leafpad-Partnership-Proposal.pdf`** — the shareable partnership proposal.
- **`build_proposal.py`** — regenerates the PDF (`python3 build_proposal.py`).

## PDF toolchain note

These containers ship LibreOffice **core only** (no `libreoffice-writer`), so
`soffice --convert-to pdf file.html` fails with *"source file could not be loaded"* — HTML import
is a Writer-module filter that isn't installed. The reliable path is the pure-Python **fpdf2**
generator (`build_proposal.py`), which `scripts/ensure-pdf-toolchain.sh` provisions (it reinstalls
`cffi` so the system `cryptography`/`fpdf2` import works).

Run it once before generating:

```bash
bash scripts/ensure-pdf-toolchain.sh
python3 docs/proposal/build_proposal.py
```

### Optional: auto-provision on every web session

To avoid running the script by hand, you can wire it as a SessionStart hook. This isn't committed
by default (it modifies harness settings), so add it yourself to `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command",
        "command": "bash \"$CLAUDE_PROJECT_DIR/scripts/ensure-pdf-toolchain.sh\"" } ] }
    ]
  }
}
```
